/* NATIVEX: whole-stage native kernels for the flat spherical profile.
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * Task: NATIVEX (the speed work; no physics of its own). Acceptance test:
 * tests/hf/test_nativex.py, which holds every kernel to the torch/numpy path it replaces, and the
 * G-NATIVEX closeness gate (docs/results/hf-nativex.md).
 *
 * TALYS routines computed here, in compound.target_batch's arrangement:
 *     comptarget.f90:1 (comptarget)      -- the (J, parity) sum, with and without Moldauer
 *     compprepare.f90:1 (compprepare)    -- denomhf and the exit-channel selection rules
 *     molprepare.f90:1 (molprepare)      -- the Gauss-Laguerre node product
 *     moldauer.f90:1 (moldauer)          -- G_b, G_gamma and the elastic E_a
 *
 * Not bit-identical: the sums run in loop order, in double precision, so cells move by rounding.
 *
 * The selection rule `ok_j & ok_s` of target_batch._mask_for, for a compound spin J2 against a
 * continuum residual spin Irspin2 = 2 i + base, is an interval in i for every exit (l', updown):
 * with ok_s holding, jj2' has the parity of parspin2, and so has |J2 - Irspin2|, so the rule is
 * |J2 - jj2'| <= Irspin2 <= J2 + jj2'. The kernel scans the rule once per (J2, l', updown) and
 * returns -1 if a set is not an interval (the caller then runs torch).
 */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define NJ 41 /* NUMJ + 1 */
#define NHILL 20
#define NNODE 32

int nx_version(void) { return 1; }

static double dof(double tav, double st, int64_t wf)
{
    if (wf == 1) {
        double v = 1.78 + (pow(tav, 1.212) - 0.78) * exp(-0.228 * st);
        return v > 2.0 ? 2.0 : v;
    }
    if (wf == 2) {
        double fT = 0.177 / (1.0 - pow(tav, 20.337));
        double gT = 1.0 + 3.148 * tav * (1.0 - tav);
        double v = 2.0 - 1.0 / (1.0 + fT * pow(st, gT));
        return v < 1.0 ? 1.0 : (v > 2.0 ? 2.0 : v);
    }
    double alpha1 = 0.0287892 * tav + 0.245856;
    double beta1 = 1.0 + 2.5 * tav * (1.0 - tav) * exp(-2.0 * st);
    double g = st - 2.0 * tav;
    double gamma1 = tav * tav - g * g;
    double delta1 = 1.0;
    if (gamma1 > 0 && st < 2 * tav) delta1 = sqrt(gamma1) / (tav > 0 ? tav : 1.0);
    double f = alpha1 * (st + tav) / (1.0 - tav) * beta1 * delta1;
    return 2.0 - 1.0 / (1.0 + f);
}

static inline int64_t iabs64(int64_t a) { return a < 0 ? -a : a; }
static inline int64_t floordiv(int64_t a, int64_t b)
{
    int64_t q = a / b;
    return (a % b != 0 && ((a < 0) != (b < 0))) ? q - 1 : q;
}

/* One exit type. Entries are the (row, l', updown) with a non-zero, lmaxhf-allowed transmission. */
typedef struct {
    int64_t t, photon, nex, nlast, L, spin2, parspin2, nd, base;
    const double *rho;             /* (nex, NJ, 2) */
    const int64_t *lmaxhf, *maxj;  /* (nex,) */
    const int64_t *jdis2, *parlev; /* (nex,) */
    const double *T;               /* particle (nex, L, 3) Tjl; photon (nex, L, 2) Tgam[l', irad] */
    double *rho_c;                 /* (nex, NJ, 2) */
    double *rho_d;                 /* (nd,) */
    int64_t *ird, *pd, *ok;        /* (nd,) */
    int64_t ne;                    /* entries */
    int32_t *en, *el, *eu;         /* (ne,) row, l', updown */
    double *S;                     /* (ne, 2): continuum rows, sum of rho_c over the spin interval */
    uint8_t *okd;                  /* (ne,): discrete rows, the rule against the level's spin */
    int16_t *ilo, *ihi;            /* (L, 3) for the J2 being processed */
    double *tpow;                  /* (ne,): tav**1.212 (wfcfactor 1) */
    double *nu;                    /* (ne,): nu of the cell being processed */
    double *totd;                  /* (K, nd) */
    double *acc;                   /* (nex, NJ, 2) */
    double *accd;                  /* (nd,) */
    double dcell;                  /* this type's denomhf term of the cell being processed */
} Ty;

static int ok_s(const Ty *y, int64_t l, int64_t u)
{
    if (y->photon) return u == 1 && l >= 1;
    int64_t jj = 2 * l + (u - 1) * y->spin2;
    int64_t dj = jj - 2 * l;
    return iabs64(dj) <= y->parspin2 && ((dj - y->parspin2) & 1) == 0 && jj >= 0
           && 2 * l >= iabs64(jj - y->parspin2);
}

static inline int64_t jj_of(const Ty *y, int64_t l, int64_t u)
{
    return y->photon ? 2 * l : 2 * l + (u - 1) * y->spin2;
}

static inline int ok_j(int64_t J2, int64_t irs2, int64_t jj)
{
    int64_t lo = iabs64(J2 - irs2), hi = J2 + irs2;
    return jj >= lo && jj <= hi && ((jj - lo) & 1) == 0;
}

/* The rule against a discrete level of spin jd2 in row n: `ok_s & ok_j`, except for a level whose
 * 2J parity is impossible for its mass (anom = (J2 + jd2 + parspin2) mod 2 = 1). There TALYS's
 * `lprime = l2prime / 2` truncates, so l2' = 2 l' + 1, jj2' = l2' + updown * spin2, capped by
 * l2' <= 2 lmaxhf (OPEN3M; prepare.anomalous_exit_mask and target_batch._prepare's cap). */
static int ok_disc(const Ty *y, int64_t J2, int64_t jd2, int64_t n, int64_t l, int64_t u)
{
    if (((J2 + jd2 + y->parspin2) & 1) == 0) return ok_s(y, l, u) && ok_j(J2, jd2, jj_of(y, l, u));
    int64_t l2 = 2 * l + 1;
    if (l2 > 2 * y->lmaxhf[n]) return 0;
    if (y->photon) return u == 1 && l2 >= 2 && ok_j(J2, jd2, l2);
    int64_t dj = (u - 1) * y->spin2, jj = l2 + dj;
    return iabs64(dj) <= y->parspin2 && ((dj - y->parspin2) & 1) == 0 && jj >= 0
           && l2 >= iabs64(jj - y->parspin2) && ok_j(J2, jd2, jj);
}

/* A photon's Tgam as the cell with c = |P - P'| / 2 reads it: irad = 1 where l' mod 2 == c. */
static inline double tg_c(const Ty *y, int64_t c, int64_t n, int64_t l)
{
    return y->T[(n * y->L + l) * 2 + (((l & 1) == c) ? 1 : 0)];
}

static void ty_free(Ty *y)
{
    free(y->rho_c); free(y->rho_d); free(y->ird); free(y->pd); free(y->ok);
    free(y->en); free(y->el); free(y->eu); free(y->S); free(y->okd);
    free(y->ilo); free(y->ihi); free(y->totd); free(y->acc); free(y->accd);
    free(y->tpow); free(y->nu);
}

static void ty_setup(Ty *y, int64_t K, int64_t j2first)
{
    int64_t nex = y->nex, L = y->L;
    y->base = (j2first + y->parspin2) % 2;
    y->rho_c = calloc((size_t)(nex * NJ * 2), sizeof(double));
    y->acc = calloc((size_t)(nex * NJ * 2), sizeof(double));
    for (int64_t n = y->nlast + 1; n < nex; n++) {
        if (n < 0) continue;
        for (int64_t i = 0; i < NJ; i++) {
            if (2 * i + y->base > 2 * y->maxj[n]) continue;
            for (int64_t q = 0; q < 2; q++) {
                double r = y->rho[(n * NJ + i) * 2 + q];
                y->rho_c[(n * NJ + i) * 2 + q] = r >= 1.0e-20 ? r : 0.0;
            }
        }
    }
    y->nd = y->nlast >= 0 ? (y->nlast < nex - 1 ? y->nlast : nex - 1) + 1 : 0;
    int64_t nd = y->nd;
    y->rho_d = calloc((size_t)(nd + 1), sizeof(double));
    y->ird = calloc((size_t)(nd + 1), sizeof(int64_t));
    y->pd = calloc((size_t)(nd + 1), sizeof(int64_t));
    y->ok = calloc((size_t)(nd + 1), sizeof(int64_t));
    y->accd = calloc((size_t)(nd + 1), sizeof(double));
    y->totd = calloc((size_t)(K * nd + 1), sizeof(double));
    for (int64_t n = 0; n < nd; n++) {
        int64_t ird = floordiv(y->jdis2[n], 2);
        int64_t pd = y->parlev[n] > 0;
        int64_t ok = ird >= 0 && ird <= NJ - 1;
        int64_t irc = ird < 0 ? 0 : (ird > NJ - 1 ? NJ - 1 : ird);
        double r = y->rho[(n * NJ + irc) * 2 + pd];
        y->rho_d[n] = (ok && r >= 1.0e-20) ? r : 0.0;
        y->ird[n] = irc;
        y->pd[n] = pd;
        y->ok[n] = ok;
    }
    /* entries */
    int64_t cap = nex * L * 3;
    y->en = malloc((size_t)(cap + 1) * sizeof(int32_t));
    y->el = malloc((size_t)(cap + 1) * sizeof(int32_t));
    y->eu = malloc((size_t)(cap + 1) * sizeof(int32_t));
    int64_t ne = 0;
    for (int64_t n = 0; n < nex; n++) {
        int64_t lm = y->lmaxhf[n];
        for (int64_t l = 0; l < L && l <= lm; l++) {
            if (y->photon) {
                if (y->T[(n * L + l) * 2] == 0.0 && y->T[(n * L + l) * 2 + 1] == 0.0) continue;
                y->en[ne] = (int32_t)n; y->el[ne] = (int32_t)l; y->eu[ne] = 1; ne++;
            } else {
                for (int64_t u = 0; u < 3; u++) {
                    if (y->T[(n * L + l) * 3 + u] == 0.0) continue;
                    y->en[ne] = (int32_t)n; y->el[ne] = (int32_t)l; y->eu[ne] = (int32_t)u; ne++;
                }
            }
        }
    }
    y->ne = ne;
    y->S = calloc((size_t)(2 * ne + 2), sizeof(double));
    y->okd = calloc((size_t)(ne + 1), sizeof(uint8_t));
    y->tpow = calloc((size_t)(ne + 1), sizeof(double));
    y->nu = calloc((size_t)(ne + 1), sizeof(double));
    if (!y->photon)
        for (int64_t e = 0; e < ne; e++) {
            double raw = y->T[(y->en[e] * L + y->el[e]) * 3 + y->eu[e]];
            y->tpow[e] = raw > 1.0e-30 ? pow(raw, 1.212) : 0.0;
        }
    y->ilo = malloc((size_t)(L * 3) * sizeof(int16_t));
    y->ihi = malloc((size_t)(L * 3) * sizeof(int16_t));
}

/* The spin intervals and the per-entry sums of one compound J2. Returns -1 on a non-interval. */
static int ty_j2(Ty *y, int64_t J2)
{
    int64_t L = y->L;
    for (int64_t l = 0; l < L; l++) {
        for (int64_t u = 0; u < 3; u++) {
            int16_t lo = 1, hi = 0;
            if (ok_s(y, l, u)) {
                int64_t jj = jj_of(y, l, u);
                int64_t first = -1, last = -2, count = 0;
                for (int64_t i = 0; i < NJ; i++) {
                    if (ok_j(J2, 2 * i + y->base, jj)) {
                        if (first < 0) first = i;
                        last = i;
                        count++;
                    }
                }
                if (count && count != last - first + 1) return -1;
                if (count) { lo = (int16_t)first; hi = (int16_t)last; }
            }
            y->ilo[l * 3 + u] = lo;
            y->ihi[l * 3 + u] = hi;
        }
    }
    for (int64_t e = 0; e < y->ne; e++) {
        int64_t n = y->en[e], l = y->el[e], u = y->eu[e];
        if (n > y->nlast) {
            const double *rc = y->rho_c + n * NJ * 2;
            double s0 = 0.0, s1 = 0.0;
            for (int64_t i = y->ilo[l * 3 + u]; i <= y->ihi[l * 3 + u]; i++) {
                s0 += rc[2 * i];
                s1 += rc[2 * i + 1];
            }
            y->S[2 * e] = s0;
            y->S[2 * e + 1] = s1;
        } else if (n < y->nd) {
            y->okd[e] = (uint8_t)ok_disc(y, J2, y->jdis2[n], n, l, u);
        }
    }
    return 0;
}

/* This type's denomhf term for cell (k, parity index p); fills totd[k]. */
static double ty_denom(Ty *y, int64_t k, int64_t p)
{
    double a0 = 0.0, a1 = 0.0;
    double *td = y->totd + k * y->nd;
    for (int64_t n = 0; n < y->nd; n++) td[n] = 0.0;
    for (int64_t e = 0; e < y->ne; e++) {
        int64_t n = y->en[e], l = y->el[e], u = y->eu[e];
        if (n > y->nlast) {
            if (y->photon) {
                a0 += tg_c(y, p != 0, n, l) * y->S[2 * e];
                a1 += tg_c(y, p != 1, n, l) * y->S[2 * e + 1];
            } else {
                int64_t qs = (l & 1) ? 1 - p : p;
                double v = y->T[(n * y->L + l) * 3 + u] * y->S[2 * e + qs];
                if (qs) a1 += v; else a0 += v;
            }
        } else if (n < y->nd && y->okd[e]) {
            int64_t cm = p != y->pd[n];
            if (y->photon) td[n] += tg_c(y, cm, n, l);
            else if ((l & 1) == cm) td[n] += y->T[(n * y->L + l) * 3 + u];
        }
    }
    double d = a0 + a1, dd = 0.0;
    for (int64_t n = 0; n < y->nd; n++) dd += td[n] * y->rho_d[n];
    return d + dd;
}

/* Scatter a no-WFC cell weight w through this type's transmissions (target_batch._feed_type). */
static void ty_scatter_w(Ty *y, int64_t k, int64_t p, double w)
{
    if (w == 0.0) return;
    for (int64_t e = 0; e < y->ne; e++) {
        int64_t n = y->en[e], l = y->el[e], u = y->eu[e];
        if (n <= y->nlast) continue;
        int64_t lo = y->ilo[l * 3 + u], hi = y->ihi[l * 3 + u];
        if (lo > hi) continue;
        double *ac = y->acc + n * NJ * 2;
        if (y->photon) {
            double v0 = w * tg_c(y, p != 0, n, l), v1 = w * tg_c(y, p != 1, n, l);
            for (int64_t i = lo; i <= hi; i++) { ac[2 * i] += v0; ac[2 * i + 1] += v1; }
        } else {
            int64_t qs = (l & 1) ? 1 - p : p;
            double v = w * y->T[(n * y->L + l) * 3 + u];
            for (int64_t i = lo; i <= hi; i++) ac[2 * i + qs] += v;
        }
    }
    const double *td = y->totd + k * y->nd;
    for (int64_t n = 0; n < y->nd; n++) y->accd[n] += td[n] * w;
}

/* acc and accd into pop[t] */
static void ty_flush(Ty *y, double *pop, int64_t nexmax)
{
    double *pt = pop + y->t * nexmax * NJ * 2;
    for (int64_t n = y->nlast + 1; n < y->nex; n++) {
        if (n < 0) continue;
        for (int64_t x = 0; x < NJ * 2; x++) pt[n * NJ * 2 + x] += y->rho_c[n * NJ * 2 + x] * y->acc[n * NJ * 2 + x];
    }
    for (int64_t n = 0; n < y->nd; n++)
        if (y->ok[n]) pt[(n * NJ + y->ird[n]) * 2 + y->pd[n]] += y->accd[n] * y->rho_d[n];
}

/* molprepare's log(1 + eps) sum over the nodes for one channel: fac[m] += a log1p(c x_m) for
 * eps = c x_m > 1e-30. */
static inline void node_log(double *fac, const double *x, double a, double c)
{
    for (int m = 0; m < NNODE; m++) {
        double eps = c * x[m];
        if (eps > 1.0e-30) fac[m] += a * log1p(eps);
    }
}

/* G = sum_m PH_m / (1 + x_m f) */
static inline double node_g(const double *PH, const double *x, double f)
{
    double tmp[NNODE];
    for (int m = 0; m < NNODE; m++) tmp[m] = PH[m] / (1.0 + x[m] * f);
    double g0 = 0.0, g1 = 0.0;
    for (int m = 0; m < NNODE; m += 2) { g0 += tmp[m]; g1 += tmp[m + 1]; }
    return g0 + g1;
}

/* A channel with c x_max < SER_TAU takes both node sums as power series in c:
 *   sum_m over log1p(c x_m) = sum_j (-1)^(j+1) (c x_m)^j / j, and
 *   sum_m PH_m / (1 + c x_m) = sum_j (-c)^j mu_j with mu_j = sum_m PH_m x_m^j,
 * truncated after SER_J terms: the remainder is below SER_TAU^(SER_J+1) ~ 1e-17 relative, with no
 * cancellation (the terms fall geometrically). */
#define SER_TAU 0.05
#define SER_J 12

static inline double ser_g(const double *mu, double c)
{
    double g = mu[SER_J];
    for (int j = SER_J - 1; j >= 0; j--) g = mu[j] - c * g;
    return g;
}

/* comptarget for one incident energy (target_batch.case_nowfc / case_moldauer).
 * ip: K, wfc, wfcfactor, k0, ltarget, nexmax, has_fis, targetspin2, target_parity, lmaxinc,
 *     tjlinc_rows, ntypes, type order (7 slots), then per type t (8 slots at 20 + 8 t): present, nex,
 *     nlast, L, spin2, parspin2, -, -
 * pp: j2 (K), pidx (K), tjlinc (rows, 3), tfis (K) or 0, hump ratio (K, 20), hump t, hump rho,
 *     hump on (K int64), x (32), w (32), then per type t (6 slots at 10 + 6 t): rho, lmaxhf, maxj,
 *     jdis2, parlev, T
 * dp: cn
 * pop: (7, nexmax, NJ, 2), zero on entry; out[0] = xs_fis, out[1] = number of live cells.
 * Returns 0, or -1 (nothing written) when the kernel does not cover the input. */
int nx_target(const int64_t *ip, const uint64_t *pp, const double *dp, double *pop, double *out)
{
    int64_t K = ip[0], wfc = ip[1], wf = ip[2], k0 = ip[3], lt = ip[4], nexmax = ip[5];
    int64_t has_fis = ip[6], ts2 = ip[7], tpar = ip[8], lmaxinc = ip[9], trows = ip[10];
    int64_t ntypes = ip[11];
    const int64_t *j2 = (const int64_t *)pp[0], *pidx = (const int64_t *)pp[1];
    const double *tjlinc = (const double *)pp[2], *tfis = (const double *)pp[3];
    const double *hr = (const double *)pp[4], *ht = (const double *)pp[5], *hrho = (const double *)pp[6];
    const int64_t *hon = (const int64_t *)pp[7];
    const double *x = (const double *)pp[8], *wts = (const double *)pp[9];
    double cn = dp[0];
    Ty ty[7];
    memset(ty, 0, sizeof(ty));
    int64_t order[7];
    Ty *photon = NULL, *yk0 = NULL;
    for (int64_t a = 0; a < ntypes; a++) {
        int64_t t = ip[12 + a];
        order[a] = t;
        Ty *y = &ty[t];
        const int64_t *ti = ip + 20 + 8 * t;
        y->t = t; y->photon = t == 0; y->nex = ti[1]; y->nlast = ti[2]; y->L = ti[3];
        y->spin2 = ti[4]; y->parspin2 = ti[5];
        const uint64_t *tp = pp + 10 + 6 * t;
        y->rho = (const double *)tp[0]; y->lmaxhf = (const int64_t *)tp[1];
        y->maxj = (const int64_t *)tp[2]; y->jdis2 = (const int64_t *)tp[3];
        y->parlev = (const int64_t *)tp[4]; y->T = (const double *)tp[5];
        ty_setup(y, K, j2[0]);
        if (t == 0) photon = y;
        if (t == k0) yk0 = y;
    }
    int rc = 0;
    double xs_fis = 0.0, elas = 0.0;
    int64_t nlive = 0;
    double *denom = calloc((size_t)(K + 1), sizeof(double));
    double *dph = calloc((size_t)(K + 1), sizeof(double));
    /* incident channels of the largest cell set: at most (2 ts2 + 1) (2 s2 + 1) */
    int64_t s2 = yk0 ? yk0->parspin2 : 0, sp2 = yk0 ? yk0->spin2 : 1;
    int64_t amax = (ts2 + 1) * (s2 + 1) + 4;
    double *tinc = malloc((size_t)amax * sizeof(double)), *nuinc = malloc((size_t)amax * sizeof(double));
    double *fa = malloc((size_t)amax * sizeof(double)), *ea = malloc((size_t)amax * sizeof(double));
    int64_t *il = malloc((size_t)amax * sizeof(int64_t)), *iu = malloc((size_t)amax * sizeof(int64_t));
    double fac[NNODE], prod[NNODE], PH[NNODE];
    int64_t j2min = j2[0], j2max = j2[0];
    for (int64_t k = 0; k < K; k++) {
        if (j2[k] < j2min) j2min = j2[k];
        if (j2[k] > j2max) j2max = j2[k];
    }
    for (int64_t J2 = j2min; J2 <= j2max; J2 += 2) {
        for (int64_t a = 0; a < ntypes; a++)
            if (ty_j2(&ty[order[a]], J2) < 0) { rc = -1; goto done; }
        for (int64_t k = 0; k < K; k++) {
            if (j2[k] != J2) continue;
            int64_t p = pidx[k];
            double d = 0.0;
            int first = 1;
            for (int64_t a = 0; a < ntypes; a++) {
                Ty *y = &ty[order[a]];
                y->dcell = ty_denom(y, k, p);
                d = first ? y->dcell : d + y->dcell;
                first = 0;
            }
            if (has_fis) d = d + tfis[k];
            denom[k] = d;
            dph[k] = photon ? photon->dcell : 0.0;
            if (d == 0.0) continue;
            nlive++;
            /* incident channels (prepare.incident_channels) */
            int64_t parity = p == 0 ? -1 : 1;
            int64_t pardif = iabs64(tpar - parity) / 2;
            int64_t na = 0;
            for (int64_t jj2 = iabs64(J2 - ts2); jj2 <= J2 + ts2; jj2 += 2) {
                int64_t l2hi = jj2 + s2 < 2 * lmaxinc ? jj2 + s2 : 2 * lmaxinc;
                for (int64_t l2 = iabs64(jj2 - s2); l2 <= l2hi; l2 += 2) {
                    int64_t l = l2 / 2;
                    if (l % 2 != pardif) continue;
                    int64_t ud = floordiv(jj2 - l2, sp2);
                    if (l >= trows || na >= amax) { rc = -1; goto done; }
                    il[na] = l; iu[na] = ud + 1;
                    tinc[na] = tjlinc[l * 3 + ud + 1];
                    na++;
                }
            }
            double pref;
            if (!wfc) {
                double feed = 0.0;
                for (int64_t i = 0; i < na; i++) feed += tinc[i];
                double w = cn * (J2 + 1.0) / d * feed;
                for (int64_t a = 0; a < ntypes; a++) ty_scatter_w(&ty[order[a]], k, p, w);
                if (has_fis) xs_fis += w * tfis[k];
                continue;
            }
            double st = d;
            for (int64_t i = 0; i < na; i++) nuinc[i] = dof(tinc[i], st, wf);
            for (int m = 0; m < NNODE; m++) fac[m] = 0.0;
            double Aser[SER_J + 1];
            for (int j = 0; j <= SER_J; j++) Aser[j] = 0.0;
            double ex228 = exp(-0.228 * st);
            double ctau = SER_TAU / x[NNODE - 1];
            for (int64_t a = 0; a < ntypes; a++) {
                Ty *y = &ty[order[a]];
                if (y->photon) continue;
                for (int64_t e = 0; e < y->ne; e++) {
                    int64_t n = y->en[e], l = y->el[e], u = y->eu[e];
                    double raw = y->T[(n * y->L + l) * 3 + u];
                    if (!(raw > 1.0e-30)) continue;
                    double nu;
                    if (wf == 1) {
                        nu = 1.78 + (y->tpow[e] - 0.78) * ex228;
                        if (nu > 2.0) nu = 2.0;
                    } else {
                        nu = dof(raw, st, wf);
                    }
                    y->nu[e] = nu;
                    double r;
                    if (n > y->nlast) r = y->S[2 * e + ((l & 1) ? 1 - p : p)];
                    else if (n < y->nd && y->okd[e] && (l & 1) == (p != y->pd[n])) r = y->rho_d[n];
                    else continue;
                    if (r == 0.0) continue;
                    double c = 2.0 * raw / (st * nu), am = -nu * 0.5 * r;
                    if (c < ctau) {
                        double cj = am;
                        for (int j = 1; j <= SER_J; j++) { cj *= c; Aser[j] += cj; }
                    } else {
                        node_log(fac, x, am, c);
                    }
                }
            }
            double nuh[NHILL];
            if (has_fis) {
                for (int h = 0; h < NHILL; h++) {
                    double th = ht[k * NHILL + h];
                    nuh[h] = dof(th, st, wf);
                    node_log(fac, x, -nuh[h] * 0.5 * hrho[k * NHILL + h], 2.0 * th / (st * nuh[h]));
                }
            }
            {
                /* sum_j (-1)^(j+1) A_j x^j / j, Horner in x */
                double B[SER_J + 1];
                for (int j = 1; j <= SER_J; j++) B[j] = ((j & 1) ? 1.0 : -1.0) * Aser[j] / j;
                for (int m = 0; m < NNODE; m++) {
                    double v = B[SER_J];
                    for (int j = SER_J - 1; j >= 1; j--) v = B[j] + x[m] * v;
                    fac[m] += x[m] * v;
                }
            }
            double gam = dph[k];
            for (int m = 0; m < NNODE; m++) {
                double expo = gam * x[m] / st;
                double capt = expo > 80.0 ? 0.0 : exp(-expo);
                prod[m] = wts[m] * wts[m] * exp(x[m]) * exp(fac[m]) * capt;
            }
            for (int64_t i = 0; i < na; i++) fa[i] = 2.0 * tinc[i] / (st * nuinc[i]);
            double gg = 0.0;
            for (int m = 0; m < NNODE; m++) {
                double H = 0.0;
                for (int64_t i = 0; i < na; i++) H += tinc[i] / (1.0 + x[m] * fa[i]);
                PH[m] = prod[m] * H;
                gg += PH[m];
            }
            pref = cn * (J2 + 1.0) / st;
            double mu[SER_J + 1];
            for (int j = 0; j <= SER_J; j++) mu[j] = 0.0;
            for (int m = 0; m < NNODE; m++) {
                double v = PH[m];
                for (int j = 0; j <= SER_J; j++) { mu[j] += v; v *= x[m]; }
            }
            if (has_fis && hon[k]) {
                double per = 0.0;
                for (int h = 0; h < NHILL; h++) {
                    double ratio = hr[k * NHILL + h];
                    if (ratio == 0.0) continue;
                    double fb = 2.0 * ht[k * NHILL + h] / (st * nuh[h]);
                    per += node_g(PH, x, fb) * ratio;
                }
                xs_fis += pref * tfis[k] * per;
            }
            if (photon) ty_scatter_w(photon, k, p, pref * gg);
            int elastic = yk0 && yk0->nd > 0 && lt >= 0 && lt < yk0->nd;
            if (elastic) {
                for (int64_t i = 0; i < na; i++) {
                    double ee = 0.0, da;
                    for (int m = 0; m < NNODE; m++) {
                        da = 1.0 + x[m] * fa[i];
                        ee += prod[m] * (2.0 / nuinc[i]) / (da * da);
                    }
                    ea[i] = ee;
                }
            }
            for (int64_t a = 0; a < ntypes; a++) {
                Ty *y = &ty[order[a]];
                if (y->photon) continue;
                for (int64_t e = 0; e < y->ne; e++) {
                    int64_t n = y->en[e], l = y->el[e], u = y->eu[e];
                    int64_t cont = n > y->nlast;
                    int64_t qs = (l & 1) ? 1 - p : p;
                    if (cont) {
                        if (y->ilo[l * 3 + u] > y->ihi[l * 3 + u]) continue;
                    } else if (!(n < y->nd && y->okd[e] && (l & 1) == (p != y->pd[n]))) {
                        continue;
                    }
                    double raw = y->T[(n * y->L + l) * 3 + u];
                    double Gb = gg;
                    if (raw > 1.0e-30) {
                        double c = 2.0 * raw / (st * y->nu[e]);
                        Gb = c < ctau ? ser_g(mu, c) : node_g(PH, x, c);
                    }
                    double Y = pref * (raw * Gb);
                    if (cont) {
                        double *ac = y->acc + n * NJ * 2;
                        for (int64_t i = y->ilo[l * 3 + u]; i <= y->ihi[l * 3 + u]; i++) ac[2 * i + qs] += Y;
                    } else {
                        y->accd[n] += Y;
                    }
                }
                if (y == yk0 && elastic) {
                    int64_t cm = p != y->pd[lt];
                    double ex = 0.0;
                    for (int64_t i = 0; i < na; i++) {
                        int64_t l = il[i], u = iu[i];
                        if (l >= y->L) continue;
                        if (!ok_disc(y, J2, y->jdis2[lt], lt, l, u)) continue;
                        if ((l & 1) != cm || l > y->lmaxhf[lt]) continue;
                        ex += y->T[(lt * y->L + l) * 3 + u] * tinc[i] * ea[i];
                    }
                    elas += pref * ex;
                }
            }
        }
    }
    for (int64_t a = 0; a < ntypes; a++) ty_flush(&ty[order[a]], pop, nexmax);
    if (wfc && yk0 && yk0->nd > 0 && lt >= 0 && lt < yk0->nd && yk0->ok[lt])
        pop[((k0 * nexmax + lt) * NJ + yk0->ird[lt]) * 2 + yk0->pd[lt]] += elas * yk0->rho_d[lt];
    out[0] = xs_fis;
    out[1] = (double)nlive;
done:
    for (int64_t a = 0; a < ntypes; a++) ty_free(&ty[order[a]]);
    free(denom); free(dph); free(tinc); free(nuinc); free(fa); free(ea); free(il); free(iu);
    return rc;
}

/* ============================================================================================
 * The multiple-emission walk down one cascade nucleus (emission.multiple._decay_nucleus_numpy
 * over compound.decay_fast.NucleusWidths), bins nex_hi down to nex_lo.
 * ============================================================================================
 *
 * Every array update of the numpy walk, in its order per array element: a particle exit feeds a
 * different nucleus, so applying it right after its bin (instead of after the whole walk, bin by
 * bin) is the same sequence of additions on every daughter element; the mother's own records
 * (xspopnuc, xsfeed, xspartial of the photon exit) are sums in bin order either way.
 *
 * ip  (int64): 0 Xrows, 1 maxex, 2 nlast, 3 m (NucleusWidths bins; 0 = none), 4 nj, 5 has_d6,
 *              6 has_fis, 7 -, then per type t at 16 + 16 t: 0 present, 1 drows, 2 record,
 *              3 closed, 4 n, 5 jx, 6 np, 7 L, 8 C, 9 nd, 10 fe_nrows, 11 fe_ncols
 * pp  (ptr):   0 ex, 1 tau, 2 jdis (int), 3 level parity index, 4 branch offsets (Xrows + 1),
 *              5 branch daughter level, 6 branch ratio, 7 rowmap (Xrows, -1 = no width row),
 *              8 maxj (m), 9 dsum6 (m, nj, 2), 10 zero6 (uint8), 11 d6, 12 fis, 13 levels0 jdis2,
 *              14 levels0 parity index, 15 X (Xrows, NJ, 2), 16 XE; per type t at 20 + 16 t:
 *              0 DX, 1 DXE, 2 rho_c, 3 T, 4 lbeg, 5 lend, 6 nrows (m), 7 tot0, 8 tot1, 9 rho_d,
 *              10 ird, 11 pd, 12 fe_val, 13 fe_present (uint8);
 *              136 popexcl (Xrows), 137 part (7, Xrows), 138 part flag (7, Xrows, uint8),
 *              139 fisfeed (Xrows), 140 fisfeed flag, 141 xsfeed (8, type + 1), 142 xsfeed flag,
 *              143 xspopnuc (7), 144 created (7, uint8), 145 work (V, dp, mc, feed, dead),
 *              146 multiple pre-equilibrium block or 0 (mpe_bin), 17 mother dex
 * dp:          0 smin, 1 popepsA, 2 gamdis (in/out), 3..9 sfac per type
 * Returns 0; -2 when a bin that decays has no width row (the caller then runs numpy).
 */

/* compound.f90's feeding of one bin by F[J, P] (J < nj): decay_native.c's dk_contract, B = 1.
 * NXC: the same additions in the same order, restricted to where they can be non-zero -- l below
 * the last non-zero transmission of the bin's daughter rows (tmax) and, per residual spin i, the
 * l range some fed (J, P) reaches -- so every skipped term is an exact zero (bit-identical). mc[k]
 * holds row k's transmission extent until it is overwritten at the end. ext[k] (out): row k's spin
 * extent, dpb[k, i >= ext[k]] == +0, so callers can stop there too. nr: the bin's row count
 * (NucleusWidths.nrows); rows past it are not scanned. */
static void contract1(int64_t row, int64_t n, int64_t jx, int64_t np_, int64_t L, int64_t nj,
                      int64_t C, const double *F, const int64_t *lbeg, const int64_t *lend,
                      const double *T, const double *rho, double sfac, int64_t nd,
                      const double *tot0, const double *tot1, const double *rho_d,
                      const int64_t *ird, const int64_t *pd, int64_t njd, double *V, double *dpb,
                      double *mc, int64_t *ext, int64_t nr)
{
    /* rows k >= nr (past the bin's nexmax) have no density in either widths path */
    int64_t nlive = nr < n ? (nr > 0 ? nr : 0) : n;
    int64_t tmax = 0;
    for (int64_t k = nlive; k < n; k++) mc[k] = 0.0;
    for (int64_t k = 0; k < nlive; k++) {
        const double *T0, *T1;
        if (C == 1) { T0 = T + (row * n + k) * L; T1 = T0; }
        else { T0 = T + ((row * 2 + 0) * n + k) * L; T1 = T + ((row * 2 + 1) * n + k) * L; }
        int64_t tl = 0;
        for (int64_t l = L - 1; l >= 0; l--) if (T0[l] != 0.0 || T1[l] != 0.0) { tl = l + 1; break; }
        mc[k] = (double)tl;
        if (tl > tmax) tmax = tl;
    }
    int64_t vlo[NJ], vhi[NJ];
    for (int64_t i = 0; i < jx; i++) {
        int64_t lo = tmax, hi = -1;
        for (int64_t J = 0; J < nj; J++) {
            if (F[J * 2] == 0.0 && F[J * 2 + 1] == 0.0) continue;
            int64_t lb = lbeg[J * jx + i], le = lend[J * jx + i];
            if (le > tmax - 1) le = tmax - 1;
            if (lb > le) continue;
            if (lb < lo) lo = lb;
            if (le > hi) hi = le;
        }
        vlo[i] = lo;
        vhi[i] = hi;
        if (hi >= lo)
            for (int64_t q = 0; q < 2; q++)
                memset(V + (i * 2 + q) * L + lo, 0, (size_t)(hi - lo + 1) * sizeof(double));
    }
    for (int64_t i = 0; i < jx; i++) {
        if (vhi[i] < vlo[i]) continue;
        for (int64_t J = 0; J < nj; J++) {
            int64_t lb = lbeg[J * jx + i], le = lend[J * jx + i];
            if (le > tmax - 1) le = tmax - 1;
            if (lb > le) continue;
            for (int64_t q = 0; q < 2; q++) {
                double f = F[J * 2 + q];
                if (f == 0.0) continue;
                double *Vo = V + (i * 2 + q) * L;
                for (int64_t l = lb; l <= le; l++) Vo[l] += f;
            }
        }
    }
    for (int64_t k = 0; k < n; k++) {
        const double *rk = rho + ((row * n + k) * jx) * np_;
        const double *T0, *T1;
        if (C == 1) { T0 = T + (row * n + k) * L; T1 = T0; }
        else { T0 = T + ((row * 2 + 0) * n + k) * L; T1 = T + ((row * 2 + 1) * n + k) * L; }
        int64_t tl = (int64_t)mc[k];
        /* spins past the row's last non-zero density only write zeros: one memset */
        int64_t ihi = 0;
        if (k < nlive)
            for (int64_t x = jx * np_ - 1; x >= 0; x--) if (rk[x] != 0.0) { ihi = x / np_ + 1; break; }
        if (ihi < jx) memset(dpb + (k * jx + ihi) * 2, 0, (size_t)((jx - ihi) * 2) * sizeof(double));
        ext[k] = ihi;
        for (int64_t i = 0; i < ihi; i++) {
            int64_t l0 = vlo[i], l1 = vhi[i] < tl - 1 ? vhi[i] : tl - 1;
            for (int64_t q = 0; q < 2; q++) {
                double r = rk[i * np_ + (np_ == 1 ? 0 : q)];
                double out = 0.0;
                if (r != 0.0) {
                    const double *Vq = V + (i * 2 + q) * L, *Vn = V + (i * 2 + 1 - q) * L;
                    double tv;
                    if (C == 1) {
                        tv = 0.0;
                        for (int64_t l = l0; l <= l1; l++) tv += T0[l] * ((l & 1) ? Vn[l] : Vq[l]);
                    } else {
                        double s0 = 0.0, s1 = 0.0;
                        for (int64_t l = l0; l <= l1; l++) { s0 += T0[l] * Vq[l]; s1 += T1[l] * Vn[l]; }
                        tv = s0 + s1;
                    }
                    out = sfac * r * tv;
                }
                dpb[(k * jx + i) * 2 + q] = out;
            }
        }
    }
    for (int64_t k = 0; k < nd; k++) {
        double r = rho_d[row * nd + k];
        if (r == 0.0) continue;
        double a = 0.0, c = 0.0;
        for (int64_t J = 0; J < nj; J++) {
            a += F[J * 2 + pd[k]] * tot0[(row * njd + J) * nd + k];
            c += F[J * 2 + 1 - pd[k]] * tot1[(row * njd + J) * nd + k];
        }
        dpb[(k * jx + ird[k]) * 2 + pd[k]] += sfac * r * (a + c);
        if (ird[k] + 1 > ext[k]) ext[k] = ird[k] + 1;
    }
    for (int64_t k = 0; k < n; k++) {
        double s = 0.0;
        for (int64_t i = 0; i < ext[k]; i++) s += dpb[(k * jx + i) * 2] + dpb[(k * jx + i) * 2 + 1];
        mc[k] = s;
    }
}

/* multipreeq2.f90's particle-hole helpers, as native/speedw.c has them (sw_mpe_bin) */
#define MPE_NFACN 26
#define MPE_FEED_MIN_MB 1.0e-10
#define MPE_PHDENS_FLOOR 1.0e-10
#define NUMZPH 4
#define NUMNPH 8

static double MPE_NFAC[MPE_NFACN];
static int mpe_nfac_ready = 0;

static void mpe_nfac_init(void)
{
    if (mpe_nfac_ready) return;
    for (int n = 0; n < MPE_NFACN; n++) {
        double o = 1.0;
        for (int i = 2; i <= n; i++) o *= (double)i;
        MPE_NFAC[n] = o;
    }
    mpe_nfac_ready = 1;
}

static double mpe_fact(int64_t n)
{
    if (n < 0) n = 0;
    if (n > MPE_NFACN - 1) n = MPE_NFACN - 1;
    return MPE_NFAC[n];
}

static double mpe_coef(int64_t k, int64_t h)
{
    if (h > MPE_NFACN - 1) h = MPE_NFACN - 1;
    double sign = (k % 2) ? -1.0 : 1.0;
    double nc = (k < 0 || k > h) ? 0.0 : MPE_NFAC[h] / (MPE_NFAC[k] * MPE_NFAC[h - k]);
    return sign * nc;
}

static double mpe_apauli2(int64_t pp, int64_t hp, int64_t pn, int64_t hn, double gsp, double gsn)
{
    if (pp == -1 || hp == -1 || pn == -1 || hn == -1) return 0.0;
    double ppf = (double)pp, hpf = (double)hp, pnf = (double)pn, hnf = (double)hn;
    double mp = ppf > hpf ? ppf : hpf;
    double mn = pnf > hnf ? pnf : hnf;
    double eppi = (mp * mp) / gsp;
    double epnu = (mn * mn) / gsn;
    double factorp = (ppf * ppf + hpf * hpf + ppf + hpf) / (4.0 * gsp);
    double factorn = (pnf * pnf + hnf * hnf + pnf + hnf) / (4.0 * gsn);
    return eppi + epnu - factorp - factorn;
}

static double mpe_finitewell(int64_t p, int64_t h, double eex, double ew)
{
    int64_t n = p + h;
    double nm1 = (double)(n - 1);
    double acc = 1.0;
    for (int64_t k = 1; k <= h; k++) {
        double ek = eex - (double)k * ew;
        int ok = (ek > 0.0) && (h >= k) && (eex > 0.0);
        double safe = eex > 0.0 ? eex : 1.0;
        double ratio = ok ? ek / safe : 1.0;
        double term = mpe_coef(k, h) * pow(ratio, nm1);
        if (!ok) term = 0.0;
        acc = acc + term;
    }
    if ((eex <= ew) || (h == 1 && n == 1)) acc = 1.0;
    return acc;
}

static double mpe_phdens2(int64_t ppi, int64_t hpi, int64_t pnu, int64_t hnu, double gsp,
                          double gsn, double ex, double ew, double ap2)
{
    double ppf = (double)ppi, hpf = (double)hpi, pnf = (double)pnu, hnf = (double)hnu;
    double factorn = (pnf * pnf + hnf * hnf + pnf + hnf) / (4.0 * gsn);
    double factorp = (ppf * ppf + hpf * hpf + ppf + hpf) / (4.0 * gsp);
    int64_t n = ppi + hpi + pnu + hnu;
    int64_t p = ppi + pnu;
    int64_t h = hpi + hnu;
    double n1 = (double)(n - 1);
    int ok = ppi >= 0 && hpi >= 0 && pnu >= 0 && hnu >= 0 && n != 0 &&
             (ap2 + factorn + factorp < ex);
    double fac1 = mpe_fact(ppi) * mpe_fact(hpi) * mpe_fact(pnu) * mpe_fact(hnu) * mpe_fact(n - 1);
    double factor = pow(gsp, (double)(ppi + hpi)) * pow(gsn, (double)(pnu + hnu)) / fac1;
    double u = ok ? ex - ap2 : 1.0;
    double dens = factor * pow(u, n1);
    dens = dens * mpe_finitewell(p, h, ex, ew);
    if (!ok) dens = 0.0;
    if (dens < MPE_PHDENS_FLOOR) dens = 0.0;
    return dens;
}

/* grids.locate_scalar on a float32 copy of the grid */
static int64_t locate_scalar32(const float *xs, int64_t ib, int64_t ie, double xd)
{
    if (ib > ie) return 0;
    float x = (float)xd;
    int64_t jl = ib - 1, ju = ie + 1;
    int ascend = xs[ie] >= xs[ib];
    while (ju - jl > 1) {
        int64_t jm = (ju + jl) / 2;
        if (ascend == (x >= xs[jm])) jl = jm; else ju = jm;
    }
    if (x == xs[ib]) return ib;
    if (x == xs[ie]) return ie - 1;
    return jl;
}

/* FeedTable.add on the dense part */
static inline void fe_add(double *val, uint8_t *present, int64_t ncols, int64_t a, int64_t b, double v)
{
    int64_t x = a * ncols + b;
    val[x] = (present[x] ? val[x] : 0.0) + v;
    present[x] = 1;
}

/* multipreeq2.f90 for mother bin nex of the nucleus being walked (Cascade.mpe_inputs +
 * preeq.mpe_fast's kernel, sw_mpe_bin's loop), applied as multiple._apply_mpe applies it.
 * mi (int64): 0 P, 1 nb, 2-3 daughter nlast, 4-5 zix, 6-7 nix, 8-9 maxex, 10-11 ebegin,
 *             12-13 eend (<= maxen), 14 maxen, 15 Xrows;
 * md (double): 0 gp(Zcomp, Ncomp), 1 gn, 2 gp(0, 0), 3 gn(0, 0), 4 Efermi, 5-6 S, 7-8 daughter gp,
 *             9-10 daughter gn;
 * mp (ptr):   0 mother particle-hole populations (Xrows, P1^4), 1 flags (Xrows, uint8; 1 = has
 *             one, set to 2 when applied), 2 nexmax (Xrows, 7), 3 jw (2, nb, NJ), 4 ex (2, nb),
 *             5 dex (2, nb), 6 float32 egrid (maxen + 1), 7-8 s-wave Tjl (rows) per daughter,
 *             9-10 daughter particle-hole additions (drows, P1^4), 11-12 their flags (drows, uint8),
 *             13 mulpre out (2, uint8), 14 scratch term (2 nb), 15 term_tot (2 nb),
 *             16 xspop_add (2, nb, NJ), 17 tsw (2 nb)
 * Returns Dmulti (0 when nothing was emitted). */
static double mpe_bin(const int64_t *ip, const uint64_t *pp, double *XE, int64_t nex,
                      double *part, uint8_t *partf, double *xsfeed, uint8_t *xsfeedf,
                      double *xspopnuc, uint8_t *created)
{
    const uint64_t *mq = (const uint64_t *)pp[146];
    const int64_t *mi = (const int64_t *)mq[0];
    const double *md = (const double *)mq[1];
    const uint64_t *mp = (const uint64_t *)mq[2];
    int64_t P = mi[0], nb = mi[1], maxen = mi[14], Xrows = mi[15];
    int64_t P1 = P + 1, P4 = P1 * P1 * P1 * P1;
    double *mother = (double *)mp[0] + nex * P4;
    uint8_t *mflag = (uint8_t *)mp[1];
    const int64_t *nxm = (const int64_t *)mp[2];
    const double *jw = (const double *)mp[3], *d_ex = (const double *)mp[4], *d_dex = (const double *)mp[5];
    const float *xs = (const float *)mp[6];
    double *term = (double *)mp[14], *term_tot = (double *)mp[15], *xspop_add = (double *)mp[16];
    double *tsw = (double *)mp[17];
    uint8_t *mulpre_out = (uint8_t *)mp[13];
    const double *ex = (const double *)pp[0];
    const double *dexa = (const double *)((const uint64_t *)pp)[17]; /* mother dex */
    double exinc = ex[nex], dexinc = dexa[nex];
    double tot_mother = 0.0;
    for (int64_t x = 0; x < P4; x++) tot_mother += mother[x];
    if (tot_mother <= MPE_FEED_MIN_MB) return 0.0;
    mpe_nfac_init();
    int64_t d_nexmax[2];
    for (int di = 0; di < 2; di++) {
        int64_t t = di + 1;
        int64_t dmaxex = mi[8 + di];
        int64_t nx = nxm[nex * 7 + t];
        d_nexmax[di] = nx < dmaxex ? nx : dmaxex;
        double *tw = tsw + di * nb;
        for (int64_t j = 0; j < nb; j++) tw[j] = 0.0;
        int64_t lo = mi[2 + di] + 1 < dmaxex + 1 ? mi[2 + di] + 1 : dmaxex + 1;
        int64_t hi = nx + 1 < dmaxex + 1 ? nx + 1 : dmaxex + 1;
        const double *tj = (const double *)mp[7 + di];
        int64_t ee = mi[12 + di] < maxen ? mi[12 + di] : maxen;
        for (int64_t j = lo; j < hi; j++) {
            double eo = exinc - d_ex[di * nb + j] - md[5 + di];
            int64_t nen = locate_scalar32(xs, mi[10 + di], ee, eo);
            tw[j] = tj[nen];
        }
    }
    memset(term_tot, 0, (size_t)(2 * nb) * sizeof(double));
    memset(xspop_add, 0, (size_t)(2 * nb * NJ) * sizeof(double));
    double gsp_state = md[0], gsn_state = md[1];
    double gp_cn0 = md[2], gn_cn0 = md[3], ef = md[4];
    double summpe = 0.0, sumtype_tot[2] = {0.0, 0.0};
    int64_t last_nlast = mi[2];
    int any_key = 0;
    static const int64_t PZ[3] = {0, 0, 1}, PN[3] = {0, 1, 0};
    for (int64_t ipp = 0; ipp <= P; ipp++)
    for (int64_t ihp = 0; ihp <= P; ihp++)
    for (int64_t ipn = 0; ipn <= P; ipn++) {
        int64_t ipt = ipp + ipn;
        if (ipt == 0 || ipt > P) continue;
        for (int64_t ihn = 0; ihn <= P; ihn++) {
            int64_t iht = ihp + ihn;
            if (iht == 0 || iht > P) continue;
            double feedph = mother[((ipp * P1 + ihp) * P1 + ipn) * P1 + ihn];
            if (feedph <= MPE_FEED_MIN_MB) continue;
            double ap = mpe_apauli2(ipp, ihp, ipn, ihn, gp_cn0, gn_cn0);
            double omegaph = mpe_phdens2(ipp, ihp, ipn, ihn, gsp_state, gsn_state, exinc, ef, ap);
            int live_om = omegaph > 0.0;
            memset(term, 0, (size_t)(2 * nb) * sizeof(double));
            double sumtype[2] = {0.0, 0.0};
            double sumterm = 0.0;
            for (int di = 0; di < 2; di++) {
                int64_t t = di + 1, ti = di;
                last_nlast = mi[2 + di];
                if (mi[4 + di] > NUMZPH || mi[6 + di] > NUMNPH) continue;
                int64_t zej = PZ[t], nej = PN[t];
                if (ipp - zej < 0 || ipn - nej < 0) continue;
                int64_t lo = mi[2 + di] + 1, hi = d_nexmax[di];
                if (hi < lo) continue;
                double *tr = term + ti * nb;
                if (live_om) {
                    double gsp_o = md[7 + di], gsn_o = md[9 + di];
                    gsp_state = gsp_o;
                    gsn_state = gsn_o;
                    const double *exd = d_ex + di * nb, *dexd = d_dex + di * nb, *tw = tsw + di * nb;
                    double ap1 = mpe_apauli2(ipp - zej, ihp, ipn - nej, ihn, gp_cn0, gn_cn0);
                    double ap1p = mpe_apauli2(zej, 0, nej, 0, gp_cn0, gn_cn0);
                    double exm = exinc + 0.5 * dexinc - md[5 + di];
                    double exmin = exd[hi] - 0.5 * dexd[hi];
                    double rsum = 0.0;
                    for (int64_t j = lo; j <= hi; j++) {
                        double omegap1h = mpe_phdens2(ipp - zej, ihp, ipn - nej, ihn, gsp_o, gsn_o,
                                                      exd[j], ef, ap1);
                        double omega1p = mpe_phdens2(zej, 0, nej, 0, gsp_o, gsn_o, exinc - exd[j],
                                                     ef, ap1p);
                        double proba = omega1p * omegap1h / omegaph / (double)(ipp + ipn);
                        double pescape = proba * tw[j];
                        double dj = (j == hi) ? exm - exmin : dexd[j];
                        double row = feedph * pescape * dj;
                        tr[j] = row;
                        rsum = rsum + row;
                    }
                    sumterm = sumterm + rsum;
                }
                double sacc = 0.0;
                for (int64_t j = lo; j <= hi; j++) sacc = sacc + tr[j];
                sumtype[ti] = sumtype[ti] + sacc;
            }
            if (sumterm > feedph) {
                double scale = feedph / sumterm;
                for (int di = 0; di < 2; di++) {
                    int64_t lo = last_nlast + 1, hi = d_nexmax[di];
                    if (hi >= lo) {
                        double *tr = term + di * nb;
                        for (int64_t j = lo; j <= hi; j++) tr[j] = tr[j] * scale;
                    }
                    sumtype[di] = sumtype[di] * scale;
                }
            }
            double sumph = 0.0;
            for (int di = 0; di < 2; di++) {
                int64_t t = di + 1, ti = di;
                if (mi[4 + di] > NUMZPH || mi[6 + di] > NUMNPH) continue;
                int64_t zej = PZ[t], nej = PN[t];
                if (ipp - zej < 0 || ipn - nej < 0) continue;
                int64_t lo = mi[2 + di] + 1, hi = d_nexmax[di];
                if (hi >= lo) {
                    const double *tr = term + ti * nb;
                    const int64_t *ti16 = ip + 16 + 16 * t;
                    int64_t drows = ti16[0] ? ti16[1] : 0;
                    double *acc = (double *)mp[9 + di];
                    uint8_t *accf = (uint8_t *)mp[11 + di];
                    int64_t kidx = (((ipp - zej) * P1 + ihp) * P1 + (ipn - nej)) * P1 + ihn;
                    any_key = 1;
                    for (int64_t j = lo; j <= hi; j++) {
                        if (j < drows && acc != NULL && tr[j] != 0.0) {
                            acc[j * P4 + kidx] += tr[j];
                            accf[j] = 1;
                        }
                        double *tt = term_tot + ti * nb;
                        tt[j] = tt[j] + tr[j];
                        double *xa = xspop_add + (ti * nb + j) * NJ;
                        const double *w = jw + (ti * nb + j) * NJ;
                        for (int64_t J = 0; J < NJ; J++) xa[J] = xa[J] + tr[j] * w[J];
                    }
                }
                sumph = sumph + sumtype[ti];
                summpe = summpe + sumtype[ti];
                sumtype_tot[ti] = sumtype_tot[ti] + sumtype[ti];
            }
            if (ipt <= P - 1 && iht <= P - 1) {
                double rest = 0.5 * (feedph - sumph);
                if (ipp <= P - 1 && ihp <= P - 1) {
                    int64_t k = (((ipp + 1) * P1 + ihp + 1) * P1 + ipn) * P1 + ihn;
                    mother[k] = mother[k] + rest;
                }
                if (ipn <= P - 1 && ihn <= P - 1) {
                    int64_t k = ((ipp * P1 + ihp) * P1 + ipn + 1) * P1 + ihn + 1;
                    mother[k] = mother[k] + rest;
                }
            }
        }
    }
    if (summpe == 0.0 && !any_key) return 0.0;
    mflag[nex] = 2;
    for (int di = 0; di < 2; di++) {
        int64_t t = di + 1;
        const int64_t *ti16 = ip + 16 + 16 * t;
        const uint64_t *pt = pp + 20 + 16 * t;
        if (!ti16[0]) continue;
        int64_t drows = ti16[1];
        int64_t n = nb < drows ? nb : drows;
        double *DX = (double *)pt[0], *DXE = (double *)pt[1];
        const double *tt = term_tot + di * nb;
        for (int64_t j = 0; j < n; j++) DXE[j] += tt[j];
        for (int64_t j = 0; j < n; j++) {
            const double *xa = xspop_add + (di * nb + j) * NJ;
            double *xr = DX + j * NJ * 2;
            for (int64_t J = 0; J < NJ; J++) xr[J * 2] += xa[J];
        }
        for (int64_t j = 0; j < n; j++) {
            const double *xa = xspop_add + (di * nb + j) * NJ;
            double *xr = DX + j * NJ * 2;
            for (int64_t J = 0; J < NJ; J++) xr[J * 2 + 1] += xa[J];
        }
        double tot = sumtype_tot[di];
        xspopnuc[t] += tot;
        part[t * Xrows + nex] += tot;
        partf[t * Xrows + nex] = 1;
        xsfeed[t + 1] += tot;
        xsfeedf[t + 1] = 1;
        if (tot != 0.0) mulpre_out[di] = 1;
        if (ti16[2]) {
            created[t] = 1;
            for (int64_t j = 0; j < n; j++)
                if (tt[j] != 0.0) fe_add((double *)pt[12], (uint8_t *)pt[13], ti16[11], nex, j, tt[j]);
        }
    }
    double dmulti = summpe / XE[nex];
    XE[nex] -= summpe;
    return dmulti;
}

int nx_walk(const int64_t *ip, const uint64_t *pp, double *dpar, int64_t nex_hi, int64_t nex_lo,
            int64_t resume, double dmulti)
{
    int64_t Xrows = ip[0], nlast = ip[2], m = ip[3], nj = ip[4], has_d6 = ip[5], has_fis = ip[6];
    const double *ex = (const double *)pp[0], *tau = (const double *)pp[1];
    const int64_t *jdis = (const int64_t *)pp[2], *lpar = (const int64_t *)pp[3];
    const int64_t *boff = (const int64_t *)pp[4], *bk = (const int64_t *)pp[5];
    const double *bratio = (const double *)pp[6];
    const int64_t *rowmap = (const int64_t *)pp[7], *maxj = (const int64_t *)pp[8];
    const double *dsum6 = (const double *)pp[9], *d6 = (const double *)pp[11], *fis = (const double *)pp[12];
    const uint8_t *zero6 = (const uint8_t *)pp[10];
    const int64_t *l0jd2 = (const int64_t *)pp[13], *l0pi = (const int64_t *)pp[14];
    double *X = (double *)pp[15], *XE = (double *)pp[16];
    double *popexcl = (double *)pp[136], *part = (double *)pp[137];
    uint8_t *partf = (uint8_t *)pp[138];
    double *fisfeed = (double *)pp[139];
    uint8_t *fisf = (uint8_t *)pp[140];
    double *xsfeed = (double *)pp[141];
    uint8_t *xsfeedf = (uint8_t *)pp[142];
    double *xspopnuc = (double *)pp[143];
    uint8_t *created = (uint8_t *)pp[144];
    const uint64_t *work = (const uint64_t *)pp[145];
    double *V = (double *)work[0], *dpw = (double *)work[1], *mcw = (double *)work[2];
    double *feed = (double *)work[3], *feed6 = (double *)work[4];
    uint8_t *dead = (uint8_t *)work[5];
    double smin = dpar[0], popepsA = dpar[1];
    const int64_t *t0 = ip + 16;
    const uint64_t *p0 = pp + 20;
    int64_t rec0 = t0[2];
    int64_t nmaxr = 1;
    for (int64_t t = 0; t < 7; t++) if (ip[16 + 16 * t + 4] > nmaxr) nmaxr = ip[16 + 16 * t + 4];
    int64_t *cext = malloc((size_t)nmaxr * sizeof(int64_t)); /* contract1's row extents */
    if (cext == NULL) return -2;
    for (int64_t nex = nex_hi; nex >= nex_lo; nex--) {
        int first = resume && nex == nex_hi;
        if (!first) {
            popexcl[nex] = XE[nex];
            if (nex <= nlast && ex[nex] <= smin) {
                if (tau[nex] == 0.0) {
                    double xsjp = X[(nex * NJ + jdis[nex]) * 2 + lpar[nex]];
                    for (int64_t b = boff[nex]; b < boff[nex + 1]; b++) {
                        int64_t k = bk[b];
                        double intens = xsjp * bratio[b];
                        X[(k * NJ + jdis[k]) * 2 + lpar[k]] += intens;
                        XE[k] += intens;
                        XE[nex] -= intens;
                        /* the numpy walk records per daughter level in a dict: a level named
                         * twice in the branching list keeps its last intensity only */
                        int later = 0;
                        for (int64_t b2 = b + 1; b2 < boff[nex + 1]; b2++) if (bk[b2] == k) later = 1;
                        if (rec0 && !later) {
                            fe_add((double *)p0[12], (uint8_t *)p0[13], t0[11], nex, k, intens);
                            part[nex] += intens;
                            partf[nex] = 1;
                            dpar[2] += intens;
                        }
                    }
                    if (rec0 && boff[nex + 1] > boff[nex]) created[0] = 1;
                }
                continue;
            }
            if (XE[nex] < popepsA) continue;
        }
        double dm = first ? dmulti : 0.0;
        if (!first && pp[146] && ((const uint8_t *)((const uint64_t *)((const uint64_t *)pp[146])[2])[1])[nex] == 1)
            dm = mpe_bin(ip, pp, XE, nex, part, partf, xsfeed, xsfeedf, xspopnuc, created);
        int64_t i = m > 0 ? rowmap[nex] : -1;
        if (i < 0) { free(cext); return -2; }
        int64_t mj = maxj[i], njb = mj + 1;
        const double *pop = X + nex * NJ * 2;
        double popeps_b = popepsA / (5 * (mj > 1 ? mj : 1)) * 0.5;
        const double *ds = dsum6 + i * nj * 2, *dd6 = has_d6 ? d6 + i * nj * 2 : NULL;
        const uint8_t *z6 = zero6 + i * nj * 2;
        int any_dead = 0, trapped = 0;
        for (int64_t x = 0; x < njb * 2; x++) {
            int active = pop[x] >= popeps_b;
            dead[x] = (uint8_t)(active && z6[x]);
            any_dead |= dead[x];
        }
        double leftover = 0.0;
        for (int64_t x = 0; x < njb * 2; x++) {
            int active = pop[x] >= popeps_b;
            double denom = ds[x];
            if (dd6) denom = any_dead ? denom + (dead[x] ? 0.0 : dd6[x]) : denom + dd6[x];
            int live = active && pop[x] != 0.0 && denom != 0.0;
            feed[x] = live ? (1.0 - dm) * pop[x] / denom : 0.0;
            if (active && pop[x] != 0.0 && denom == 0.0) {
                trapped = 1;
                leftover += pop[x];
            }
        }
        if (trapped) {
            /* compound.f90:404-419, multiple._apply_leftover: the mother's own discrete levels */
            if (nlast >= 0 && leftover != 0.0) {
                double share = leftover / (nlast + 1.0);
                int64_t top = nlast < Xrows - 1 ? nlast : Xrows - 1;
                for (int64_t k = 0; k <= top; k++) XE[k] += share;
                part[nex] += leftover;
                partf[nex] = 1;
            }
        }
        /* the photon exit, into this nucleus's own lower bins */
        {
            int64_t r = ((const int64_t *)p0[6])[i];
            int64_t n = r < Xrows ? r : Xrows;
            int64_t jx = t0[5];
            int64_t closed = t0[3];
            if (!closed)
                contract1(i, t0[4], jx, t0[6], t0[7], njb, t0[8], feed, (const int64_t *)p0[4],
                          (const int64_t *)p0[5], (const double *)p0[3], (const double *)p0[2],
                          dpar[3], t0[9], (const double *)p0[7], (const double *)p0[8],
                          (const double *)p0[9], (const int64_t *)p0[10], (const int64_t *)p0[11],
                          nj, V, dpw, mcw, cext, ((const int64_t *)p0[6])[i]);
            if (!closed || trapped) {
                if (closed) {
                    jx = 0;
                    for (int64_t k = 0; k < n; k++) mcw[k] = 0.0;
                }
                for (int64_t k = 0; k < n; k++) {
                    double *xr = X + k * NJ * 2;
                    const double *dr = dpw + k * jx * 2;
                    if (trapped && k <= nlast) {
                        int64_t cell = (l0jd2[k] / 2) * 2 + l0pi[k];
                        for (int64_t c = 0; c < jx * 2; c++) {
                            double v = dr[c];
                            if (c == cell) {
                                for (int64_t x = 0; x < njb * 2; x++) {
                                    int active = pop[x] >= popeps_b;
                                    double denom = ds[x];
                                    if (dd6) denom = any_dead ? denom + (dead[x] ? 0.0 : dd6[x]) : denom + dd6[x];
                                    if (active && pop[x] != 0.0 && denom == 0.0) v += pop[x] / (nlast + 1.0);
                                }
                            }
                            xr[c] += v;
                        }
                        if (cell >= jx * 2) {
                            double v = 0.0;
                            for (int64_t x = 0; x < njb * 2; x++) {
                                int active = pop[x] >= popeps_b;
                                double denom = ds[x];
                                if (dd6) denom = any_dead ? denom + (dead[x] ? 0.0 : dd6[x]) : denom + dd6[x];
                                if (active && pop[x] != 0.0 && denom == 0.0) v += pop[x] / (nlast + 1.0);
                            }
                            xr[cell] += v;
                        }
                    } else {
                        int64_t ce = closed ? 0 : cext[k] * 2; /* NXC: dpw is +0 past it */
                        for (int64_t c = 0; c < ce; c++) xr[c] += dr[c];
                    }
                }
                double tot = 0.0;
                for (int64_t k = 0; k < n; k++) XE[k] += mcw[k];
                for (int64_t k = 0; k < n; k++) tot += mcw[k];
                XE[nex] -= tot;
                part[nex] += tot;
                partf[nex] = 1;
                xspopnuc[0] += tot;
                xsfeed[1] += tot;
                xsfeedf[1] = 1;
                if (rec0) {
                    for (int64_t k = 0; k < n; k++)
                        if (mcw[k] != 0.0) fe_add((double *)p0[12], (uint8_t *)p0[13], t0[11], nex, k, mcw[k]);
                }
            } else {
                part[nex] += 0.0;
                partf[nex] = 1;
                xsfeed[1] += 0.0;
                xsfeedf[1] = 1;
            }
            if (rec0) {
                created[0] = 1;
                if (trapped && leftover != 0.0 && nlast >= 0) {
                    double share = leftover / (nlast + 1.0);
                    int64_t top = nlast < Xrows - 1 ? nlast : Xrows - 1;
                    for (int64_t k = 0; k <= top; k++)
                        fe_add((double *)p0[12], (uint8_t *)p0[13], t0[11], nex, k, share);
                }
            }
        }
        /* the particle exits, into the daughters */
        if (any_dead)
            for (int64_t x = 0; x < njb * 2; x++) feed6[x] = dead[x] ? 0.0 : feed[x];
        for (int64_t t = 1; t < 7; t++) {
            const int64_t *ti = ip + 16 + 16 * t;
            const uint64_t *pt = pp + 20 + 16 * t;
            if (!ti[0]) continue;
            double *prt = part + t * Xrows;
            uint8_t *prf = partf + t * Xrows;
            if (ti[2]) created[t] = 1;
            if (ti[3]) {
                prt[nex] += 0.0;
                prf[nex] = 1;
                xspopnuc[t] += 0.0;
                xsfeed[t + 1] += 0.0;
                xsfeedf[t + 1] = 1;
                continue;
            }
            int64_t ne = ti[4], jx = ti[5], drows = ti[1];
            const double *F = (t == 6 && any_dead) ? feed6 : feed;
            contract1(i, ne, jx, ti[6], ti[7], njb, ti[8], F, (const int64_t *)pt[4],
                      (const int64_t *)pt[5], (const double *)pt[3], (const double *)pt[2],
                      dpar[3 + t], ti[9], (const double *)pt[7], (const double *)pt[8],
                      (const double *)pt[9], (const int64_t *)pt[10], (const int64_t *)pt[11], nj,
                      V, dpw, mcw, cext, ((const int64_t *)pt[6])[i]);
            int64_t n = ne < drows ? ne : drows;
            double *DX = (double *)pt[0], *DXE = (double *)pt[1];
            for (int64_t k = 0; k < n; k++) {
                double *xr = DX + k * NJ * 2;
                const double *dr = dpw + k * jx * 2;
                for (int64_t c = 0; c < cext[k] * 2; c++) xr[c] += dr[c]; /* NXC: +0 past it */
            }
            for (int64_t k = 0; k < n; k++) DXE[k] += mcw[k];
            int64_t nr = ((const int64_t *)pt[6])[i];
            int64_t ntot = nr < n ? nr : n;
            double tot = 0.0;
            for (int64_t k = 0; k < ntot; k++) tot += mcw[k];
            XE[nex] -= tot;
            xspopnuc[t] += tot;
            prt[nex] += tot;
            prf[nex] = 1;
            xsfeed[t + 1] += tot;
            xsfeedf[t + 1] = 1;
            if (ti[2]) {
                for (int64_t k = 0; k < n; k++)
                    if (mcw[k] != 0.0) fe_add((double *)pt[12], (uint8_t *)pt[13], ti[11], nex, k, mcw[k]);
            }
        }
        if (has_fis) {
            const double *fr = fis + i * nj * 2;
            double ff = 0.0;
            for (int64_t x = 0; x < njb * 2; x++) ff += feed[x] * fr[x];
            if (ff != 0.0) {
                fisfeed[nex] += ff;
                fisf[nex] = 1;
                xsfeed[0] += ff;
                xsfeedf[0] = 1;
                XE[nex] -= ff;
            }
        }
    }
    free(cext);
    return 0;
}

/* ============================================================================================
 * The decay widths of one cascade nucleus (compound.decay_fast.NucleusWidths.__init__ after the
 * photon strength functions): _Geometry, _particles, _cap_l and _finish for all seven exits.
 * ============================================================================================
 *
 * ip  (int64): 0 m, 1 nj, 2 odd, 3 k0, 4 lmaxinc, 5 maxen, 6 L (Tl columns), 7 Tl rows,
 *              8 egrid length, 9 photon columns (gammax + 1); per type t at 16 + 8 t: 0 n (rows),
 *              1 nlast (unclamped), 2 ntop, 3 rhogrid rows, 4 discrete levels given, 5 parspin2
 * pp  (ptr):   0 exinc (m), 1 dexinc, 2 nexmax (m, 7), 3 sep (7), 4 Tl (6, rows, L), 5 lmax (6, rows),
 *              6 head0 (6), 7 egrid, 8 egrid as float32 (maxen + 1), 9 ebegin (6), 10 eend (6),
 *              11 Fnorm (6, types 1..6), 12 Tgam (m, n0, gammax + 1, 2);
 *              per type t at 20 + 8 t: 0 ex (n), 1 dex, 2 maxj, 3 jdis2 (float32-doubled), 4 int(jdis),
 *              5 parlev, 6 rhogrid (rows, NJ, 2)
 * dp:          0 transeps, 1 + t discfactor
 * out per type t at 0 + 12 t (ptr): 0 rho_c (m, n, jx, 2) compacted, 1 T (m, n, Lc) particle or
 *              (m, 2, n, Lc) photon compacted, 2 tot0 (m, nj, nd), 3 tot1, 4 rho_d (m, nd), 5 ird (nd),
 *              6 pd (nd), 7 D (m, nj, 2), 8 nrows (m), 9 lbeg (nj * jx), 10 lend
 *              (buffers sized for jx = NJ, Lc = max columns, nd = discrete levels given)
 * meta (int64, 8 per type): closed, jx, Lc, nd
 * Returns 0. */

static int64_t locate_right32(const float *xs, int64_t n, float x)
{
    int64_t lo = 0, hi = n; /* first index with xs[i] > x */
    while (lo < hi) {
        int64_t mid = (lo + hi) / 2;
        if (xs[mid] <= x) lo = mid + 1; else hi = mid;
    }
    return lo;
}

static const int64_t PARSPIN2_[7] = {0, 1, 1, 2, 1, 1, 0};

int nx_widths(const int64_t *ip, const uint64_t *pp, const double *dp, const uint64_t *outp,
              int64_t *meta)
{
    int64_t m = ip[0], nj = ip[1], odd = ip[2], k0 = ip[3], lmaxinc = ip[4], maxen = ip[5];
    int64_t Ltl = ip[6], tlrows = ip[7], L0 = ip[9];
    const double *exinc = (const double *)pp[0], *dexinc = (const double *)pp[1];
    const int64_t *nxm = (const int64_t *)pp[2];
    const double *sep = (const double *)pp[3];
    const double *TL = (const double *)pp[4];
    const int64_t *LM = (const int64_t *)pp[5], *head0 = (const int64_t *)pp[6];
    const double *egrid = (const double *)pp[7];
    const float *xs = (const float *)pp[8];
    const int64_t *ebeg = (const int64_t *)pp[9], *eend = (const int64_t *)pp[10];
    const double *fn = (const double *)pp[11], *tgam = (const double *)pp[12];
    double transeps = dp[0];
    int64_t Lmax = Ltl > L0 ? Ltl : L0;
    int64_t nmax = 1;
    for (int64_t t = 0; t < 7; t++) if (ip[16 + 8 * t] > nmax) nmax = ip[16 + 8 * t];
    double *rb = malloc((size_t)(m * nmax) * sizeof(double));
    double *eout = malloc((size_t)(m * nmax) * sizeof(double));
    int64_t *lmaxhf = malloc((size_t)(m * nmax) * sizeof(int64_t));
    double *Tw = malloc((size_t)(m * nmax * Lmax * 2) * sizeof(double)); /* (b, r, l[, c]) */
    double *R = malloc((size_t)(m * NJ * 2 * Lmax * 2) * sizeof(double));
    int64_t nddmax = 1;
    for (int64_t t = 0; t < 7; t++) if (ip[16 + 8 * t + 4] > nddmax) nddmax = ip[16 + 8 * t + 4];
    int64_t *rext_d = malloc((size_t)(2 * nddmax) * sizeof(int64_t));
    int64_t *wext = malloc((size_t)(m * nmax) * sizeof(int64_t));
    int64_t *live_d = malloc((size_t)nddmax * sizeof(int64_t));
    int64_t *win_d = malloc((size_t)(2 * NJ * nddmax) * sizeof(int64_t));
    for (int64_t t = 0; t < 7; t++) {
        const int64_t *ti = ip + 16 + 8 * t;
        const uint64_t *pt = pp + 20 + 8 * t;
        const uint64_t *o = outp + 12 * t;
        int64_t *mt = meta + 8 * t;
        int64_t n = ti[0], nl = ti[1], ntop = ti[2], ndd_given = ti[4], ps2 = ti[5];
        const double *ex = (const double *)pt[0], *dex = (const double *)pt[1];
        const int64_t *maxjd = (const int64_t *)pt[2], *jd2 = (const int64_t *)pt[3];
        const int64_t *irw = (const int64_t *)pt[4], *parlev = (const int64_t *)pt[5];
        const double *rhog = (const double *)pt[6];
        int64_t *nrows = (int64_t *)o[8];
        double ss = sep[t];
        double sfac = t == 0 ? 1.0 : (double)(PARSPIN2_[t] + 1);
        /* _Geometry, this type's rows */
        for (int64_t b = 0; b < m; b++) {
            int64_t nexmax = nxm[b * 7 + t] > 0 ? nxm[b * 7 + t] : 0;
            nrows[b] = nexmax + 1;
            double ex0plus = exinc[b] + 0.5 * dexinc[b], ex0min = exinc[b] - 0.5 * dexinc[b];
            for (int64_t r = 0; r < n; r++) {
                double e1min = ex[r] - 0.5 * dex[r];
                int top = r == nexmax && t >= 1;
                double e1plus = top ? ex0plus - ss : ex[r] + 0.5 * dex[r];
                double rbv, eo;
                if (r > nl) {
                    double emax = (ex0plus - ss) - e1min, emin = (ex0min - ss) - e1plus;
                    double mid = 0.5 * (emin + emax), half = 0.5 * (emax - emin);
                    if (emin < 0.0) {
                        if (mid > 0.0) { double q = emin / half; rbv = 1.0 - 0.5 * (q * q); }
                        else { double q = emax / half; rbv = 0.5 * (q * q); }
                    } else {
                        rbv = 1.0;
                    }
                    eo = 0.5 * ((emin < 0.0 ? 0.0 : emin) + emax);
                } else {
                    double exm = ex[r] + ss;
                    int part = ex0min < exm && exm <= ex0plus;
                    rbv = part ? (ex0plus - exm) / dexinc[b] : 1.0;
                    eo = part ? 0.5 * (ex0plus + exm) - ss - ex[r] : (exinc[b] - ss) - ex[r];
                }
                rb[b * n + r] = rbv;
                eout[b * n + r] = r <= nexmax ? eo : 0.0;
            }
        }
        /* transmissions, lmaxhf-capped, on (b, r, l) */
        int64_t L = t == 0 ? L0 : Ltl;
        int64_t Lc = 0;
        double *T = (double *)o[1];
        if (t == 0) {
            for (int64_t b = 0; b < m; b++)
                for (int64_t r = 0; r < n; r++)
                    for (int64_t l = 0; l < L; l++) {
                        double a = tgam[((b * n + r) * L + l) * 2 + 1 - (l & 1)];
                        double c = tgam[((b * n + r) * L + l) * 2 + (l & 1)];
                        if (k0 == 0 && r == 0 && l > lmaxinc) a = c = 0.0; /* _cap_l, photon projectile */
                        Tw[(b * n + r) * L * 2 + 2 * l] = a;
                        Tw[(b * n + r) * L * 2 + 2 * l + 1] = c;
                        if ((a != 0.0 || c != 0.0) && l + 1 > Lc) Lc = l + 1;
                    }
        } else {
            int64_t tt = t - 1;
            /* NXC: no zero fill of Tw; wext[b, r] is how many columns the row has written, and
             * everything past it reads as zero (the cap, Lc and the compaction below) */
            for (int64_t x = 0; x < m * n; x++) { lmaxhf[x] = 0; wext[x] = 0; }
            if (ebeg[tt] < eend[tt]) {
                int64_t eb = ebeg[tt], ee = eend[tt];
                double lo = egrid[eb];
                for (int64_t b = 0; b < m; b++) {
                    int64_t nexmax = nrows[b] - 1;
                    for (int64_t r = 0; r <= nexmax && r < n; r++) {
                        double e = eout[b * n + r];
                        float x = (float)e;
                        int64_t jl = locate_right32(xs, maxen + 1, x) - 1;
                        if (jl < eb - 1) jl = eb - 1;
                        if (jl > ee) jl = ee;
                        if (x == xs[eb]) jl = eb;
                        else if (x == xs[ee]) jl = ee - 1;
                        int64_t nen = e < lo ? 0 : jl;
                        int64_t nc_ = nen < 0 ? 0 : (nen > maxen ? maxen : nen);
                        int64_t lsel = LM[tt * tlrows + nc_];
                        lmaxhf[b * n + r] = lsel;
                        if (e < lo && head0[tt]) continue;
                        int centred = nen > eb + 1 || nen >= maxen - 1;
                        int64_t na = centred ? nen - 1 : nen, nb = na + 1, nc = na + 2;
                        /* numpy's negative indices wrap; they only arise below the grid */
                        int64_t ga = na < 0 ? na + ip[8] : na, gb = nb < 0 ? nb + ip[8] : nb;
                        int64_t gc = nc < 0 ? nc + ip[8] : nc;
                        double ea = egrid[ga], ebv = egrid[gb], ec = egrid[gc];
                        if (na < 0) na += tlrows;
                        if (nb < 0) nb += tlrows;
                        if (nc < 0) nc += tlrows;
                        double w1 = (e - ebv) * (e - ec) / ((ea - ebv) * (ea - ec));
                        double w2 = (e - ea) * (e - ec) / ((ebv - ea) * (ebv - ec));
                        double w3 = (e - ea) * (e - ebv) / ((ec - ea) * (ec - ebv));
                        int64_t lt = lsel < L - 1 ? lsel : L - 1;
                        wext[b * n + r] = lt + 1 > 0 ? lt + 1 : 0;
                        const double *ta = TL + (tt * tlrows + na) * L, *tb = TL + (tt * tlrows + nb) * L;
                        const double *tc = TL + (tt * tlrows + nc) * L;
                        for (int64_t l = 0; l <= lt; l++) {
                            double u = w1 * ta[l] + w2 * tb[l] + w3 * tc[l];
                            Tw[(b * n + r) * L + l] = (u < transeps ? 0.0 : u) * fn[tt];
                        }
                    }
                }
                for (int64_t b = 0; b < m; b++) {
                    int64_t nexm = nrows[b] - 1;
                    if (nexm > 0 && nexm < n) lmaxhf[b * n + nexm] = lmaxhf[b * n + nexm - 1];
                    if (t == k0) lmaxhf[b * n] = lmaxinc;
                }
                for (int64_t b = 0; b < m; b++)
                    for (int64_t r = 0; r < n; r++) {
                        int64_t w = wext[b * n + r], lim = lmaxhf[b * n + r];
                        int64_t w2 = lim + 1 < w ? (lim + 1 > 0 ? lim + 1 : 0) : w;
                        double *row = Tw + (b * n + r) * L;
                        for (int64_t l = w2; l < w; l++) row[l] = 0.0; /* l > lmaxhf */
                        wext[b * n + r] = w2;
                        for (int64_t l = w2 - 1; l >= 0; l--)
                            if (row[l] != 0.0) { if (l + 1 > Lc) Lc = l + 1; break; }
                    }
            }
        }
        mt[2] = Lc;
        if (Lc == 0) {
            mt[0] = 1; mt[1] = 1; mt[3] = 0;
            continue;
        }
        /* compacted T */
        if (t == 0) {
            for (int64_t b = 0; b < m; b++)
                for (int64_t c = 0; c < 2; c++)
                    for (int64_t r = 0; r < n; r++)
                        for (int64_t l = 0; l < Lc; l++)
                            T[((b * 2 + c) * n + r) * Lc + l] = Tw[(b * n + r) * L * 2 + 2 * l + c];
        } else {
            for (int64_t b = 0; b < m; b++)
                for (int64_t r = 0; r < n; r++) {
                    int64_t w = wext[b * n + r] < Lc ? wext[b * n + r] : Lc;
                    for (int64_t l = 0; l < w; l++) T[(b * n + r) * Lc + l] = Tw[(b * n + r) * L + l];
                    for (int64_t l = w; l < Lc; l++) T[(b * n + r) * Lc + l] = 0.0;
                }
        }
        /* _finish */
        int64_t base = (odd + ps2) % 2;
        int64_t jc = 0;
        for (int64_t r = nl + 1; r < n; r++) {
            if (r < 0) continue;
            for (int64_t i = 0; i < NJ; i++)
                if (2 * i + base <= 2 * maxjd[r] && i <= maxjd[r] && i + 1 > jc) jc = i + 1;
        }
        int64_t ndd = (nl < n - 1 ? nl : n - 1) + 1;
        if (ndd > ndd_given) ndd = ndd_given;
        if (ndd < 0) ndd = 0;
        int64_t *ird = (int64_t *)o[5], *pd = (int64_t *)o[6];
        int64_t jx = jc;
        for (int64_t k = 0; k < ndd; k++) {
            int64_t v = floordiv(jd2[k], 2);
            if (v >= 0 && v <= NJ - 1 && v + 1 > jx) jx = v + 1;
        }
        if (jx < 1) jx = 1;
        mt[0] = 0; mt[1] = jx;
        double *rho_c = (double *)o[0];
        memset(rho_c, 0, (size_t)(m * n * jx * 2) * sizeof(double));
        if (jc) {
            for (int64_t b = 0; b < m; b++) {
                int64_t r1 = nrows[b] < n ? nrows[b] : n;
                for (int64_t r = nl + 1 > 0 ? nl + 1 : 0; r < r1; r++) {
                    double rbv = rb[b * n + r];
                    int64_t ihi = maxjd[r] < jx - 1 ? maxjd[r] : jx - 1;
                    for (int64_t i = 0; i <= ihi; i++) {
                        if (2 * i + base > 2 * maxjd[r]) break;
                        for (int64_t q = 0; q < 2; q++) {
                            double v = rbv * rhog[(r * NJ + i) * 2 + q];
                            rho_c[((b * n + r) * jx + i) * 2 + q] = v >= 1.0e-20 ? v : 0.0;
                        }
                    }
                }
            }
        }
        int64_t *lbeg = (int64_t *)o[9], *lend = (int64_t *)o[10];
        for (int64_t J = 0; J < nj; J++) {
            int64_t j2 = 2 * J + odd;
            for (int64_t i = 0; i < jx; i++) {
                int64_t irs2 = 2 * i + base;
                lbeg[J * jx + i] = iabs64(iabs64(j2 - irs2) - ps2) / 2;
                lend[J * jx + i] = (j2 + irs2 + ps2) / 2;
            }
        }
        double *D = (double *)o[7];
        int64_t NC = t == 0 ? 2 : 1;
        /* NXC: R is zeroed only over the columns the previous bin wrote (rext), and the J sums stop
         * at this bin's extent: every skipped term is an exact zero (bit-identical) */
        int64_t rext[2] = {Lc, Lc};
        int64_t iprev = jx; /* spins the previous bin wrote */
        for (int64_t b = 0; b < m; b++) {
            /* R[c, i, p, l] = sum_r rho_c T_c */
            for (int64_t c = 0; c < NC; c++)
                if (rext[c] > 0)
                    for (int64_t x = 0; x < iprev * 2; x++)
                        memset(R + (c * jx * 2 + x) * Lc, 0, (size_t)rext[c] * sizeof(double));
            rext[0] = rext[1] = 0;
            int64_t iext = 0; /* one past the last spin with a contribution */
            int64_t r1 = nrows[b] < n ? nrows[b] : n;
            for (int64_t r = nl + 1 > 0 ? nl + 1 : 0; r < r1; r++) {
                int64_t lr[2] = {0, 0}; /* one past the last non-zero l' of the row */
                for (int64_t c = 0; c < NC; c++) {
                    const double *Tr = t == 0 ? T + ((b * 2 + c) * n + r) * Lc : T + (b * n + r) * Lc;
                    for (int64_t l = Lc - 1; l >= 0; l--) if (Tr[l] != 0.0) { lr[c] = l + 1; break; }
                }
                if (lr[0] == 0 && lr[1] == 0) continue;
                /* rho_c[b, r, i] is zero past min(maxJ(r), jx - 1) (the fill above) */
                int64_t ihi = maxjd[r] < jx - 1 ? maxjd[r] : jx - 1;
                int live = 0;
                for (int64_t i = 0; i <= ihi; i++)
                    for (int64_t q = 0; q < 2; q++) {
                        double rc = rho_c[((b * n + r) * jx + i) * 2 + q];
                        if (rc == 0.0) continue;
                        live = 1;
                        if (i + 1 > iext) iext = i + 1;
                        for (int64_t c = 0; c < NC; c++) {
                            const double *Tr = t == 0 ? T + ((b * 2 + c) * n + r) * Lc : T + (b * n + r) * Lc;
                            double *Ro = R + ((c * jx + i) * 2 + q) * Lc;
                            for (int64_t l = 0; l < lr[c]; l++) Ro[l] += rc * Tr[l];
                        }
                    }
                if (live)
                    for (int64_t c = 0; c < NC; c++) if (lr[c] > rext[c]) rext[c] = lr[c];
            }
            iprev = iext;
            for (int64_t J = 0; J < nj; J++) {
                double MR[2][2] = {{0.0, 0.0}, {0.0, 0.0}};
                for (int64_t i = 0; i < iext; i++) {
                    int64_t lb = lbeg[J * jx + i], le = lend[J * jx + i];
                    if (le > Lc - 1) le = Lc - 1;
                    for (int64_t q = 0; q < 2; q++) {
                        if (t == 0) {
                            for (int64_t c = 0; c < 2; c++) {
                                const double *Ro = R + ((c * jx + i) * 2 + q) * Lc;
                                int64_t lec = le < rext[c] - 1 ? le : rext[c] - 1;
                                for (int64_t l = lb; l <= lec; l++) MR[c][q] += Ro[l];
                            }
                        } else {
                            const double *Ro = R + ((0 * jx + i) * 2 + q) * Lc;
                            int64_t lec = le < rext[0] - 1 ? le : rext[0] - 1;
                            double se = 0.0, so = 0.0;
                            for (int64_t l = lb + (lb & 1); l <= lec; l += 2) se += Ro[l];
                            for (int64_t l = lb + 1 - (lb & 1); l <= lec; l += 2) so += Ro[l];
                            MR[0][q] += se;
                            MR[1][q] += so;
                        }
                    }
                }
                D[(b * nj + J) * 2 + 0] = (MR[0][0] + MR[1][1]) * sfac;
                D[(b * nj + J) * 2 + 1] = (MR[1][0] + MR[0][1]) * sfac;
            }
        }
        /* discrete rows */
        double discf = dp[1 + t];
        double *rho_d = (double *)o[4];
        int any = 0;
        for (int64_t k = 0; k < ndd; k++) {
            int64_t v = floordiv(jd2[k], 2);
            int64_t okk = v >= 0 && v <= NJ - 1;
            ird[k] = v < 0 ? 0 : (v > NJ - 1 ? NJ - 1 : v);
            pd[k] = parlev[k] > 0;
            int64_t pidx = parlev[k] == -1 ? 0 : 1;
            int same = irw[k] == v && pidx == pd[k] && irw[k] >= 0 && irw[k] <= NJ - 1 && okk;
            for (int64_t b = 0; b < m; b++) {
                double val = k > ntop ? rb[b * n + k] * discf : rb[b * n + k];
                double rv = (same && k < nrows[b]) ? val : 0.0;
                if (!(rv >= 1.0e-20)) rv = 0.0;
                if (nl == 0 && k == 0) rv = 0.0;
                rho_d[b * ndd + k] = rv;
                if (rv != 0.0) any = 1;
            }
        }
        mt[3] = 0;
        if (any) {
            mt[3] = ndd;
            double *tot0 = (double *)o[2], *tot1 = (double *)o[3];
            /* NXC: the l windows of every (J, level) once per type, not per bin; per bin only the
             * levels with a density are summed (the rest of the bin's tot is one zero fill), and
             * each sum stops at its row's last non-zero transmission (bit-identical) */
            for (int64_t J = 0; J < nj; J++) {
                int64_t j2 = 2 * J + odd;
                for (int64_t k = 0; k < ndd; k++) {
                    int64_t le = (j2 + jd2[k] + ps2) / 2;
                    win_d[2 * (J * ndd + k)] = iabs64(iabs64(j2 - jd2[k]) - ps2) / 2;
                    win_d[2 * (J * ndd + k) + 1] = le > Lc - 1 ? Lc - 1 : le;
                }
            }
            for (int64_t b = 0; b < m; b++) {
                int64_t nlive = 0;
                for (int64_t k = 0; k < ndd; k++) {
                    if (rho_d[b * ndd + k] == 0.0) continue;
                    int64_t e0 = 0, e1 = 0;
                    const double *A = t == 0 ? T + ((b * 2 + 0) * n + k) * Lc : T + (b * n + k) * Lc;
                    for (int64_t l = Lc - 1; l >= 0; l--) if (A[l] != 0.0) { e0 = l + 1; break; }
                    if (t == 0) {
                        const double *B = T + ((b * 2 + 1) * n + k) * Lc;
                        for (int64_t l = Lc - 1; l >= 0; l--) if (B[l] != 0.0) { e1 = l + 1; break; }
                    }
                    live_d[nlive] = k;
                    rext_d[2 * nlive] = e0;
                    rext_d[2 * nlive + 1] = e1;
                    nlive++;
                }
                memset(tot0 + b * nj * ndd, 0, (size_t)(nj * ndd) * sizeof(double));
                memset(tot1 + b * nj * ndd, 0, (size_t)(nj * ndd) * sizeof(double));
                for (int64_t J = 0; J < nj; J++) {
                    double a00 = 0.0, a10 = 0.0, a01 = 0.0, a11 = 0.0;
                    for (int64_t x = 0; x < nlive; x++) {
                        int64_t k = live_d[x];
                        int64_t lb = win_d[2 * (J * ndd + k)], le = win_d[2 * (J * ndd + k) + 1];
                        double s0 = 0.0, s1 = 0.0;
                        if (t == 0) {
                            const double *A = T + ((b * 2 + 0) * n + k) * Lc, *B = T + ((b * 2 + 1) * n + k) * Lc;
                            int64_t le0 = le < rext_d[2 * x] - 1 ? le : rext_d[2 * x] - 1;
                            int64_t le1 = le < rext_d[2 * x + 1] - 1 ? le : rext_d[2 * x + 1] - 1;
                            for (int64_t l = lb; l <= le0; l++) s0 += A[l];
                            for (int64_t l = lb; l <= le1; l++) s1 += B[l];
                        } else {
                            const double *A = T + (b * n + k) * Lc;
                            int64_t le0 = le < rext_d[2 * x] - 1 ? le : rext_d[2 * x] - 1;
                            for (int64_t l = lb; l <= le0; l++) { if (l & 1) s1 += A[l]; else s0 += A[l]; }
                        }
                        tot0[(b * nj + J) * ndd + k] = s0;
                        tot1[(b * nj + J) * ndd + k] = s1;
                        double r = rho_d[b * ndd + k];
                        double rpar = pd[k] == 1 ? r : 0.0, rnpar = pd[k] == 0 ? r : 0.0;
                        a00 += s0 * rnpar;
                        a10 += s1 * rpar;
                        a01 += s0 * rpar;
                        a11 += s1 * rnpar;
                    }
                    D[(b * nj + J) * 2 + 0] += sfac * (a00 + a10);
                    D[(b * nj + J) * 2 + 1] += sfac * (a01 + a11);
                }
            }
        }
        int nz = 0;
        for (int64_t x = 0; x < m * nj * 2; x++) if (D[x] != 0.0) { nz = 1; break; }
        mt[0] = !nz;
    }
    free(rb); free(eout); free(lmaxhf); free(Tw); free(R); free(rext_d); free(wext); free(live_d); free(win_d);
    return 0;
}

/* ============================================================================================
 * finitewell.f90's sum (density.particle_hole._sum_terms_arr) on broadcast arrays:
 *   acc = 1 + sum_{k=1..hmax} [e_k > 0, h >= k, E > 0] tab[k-1][clip(h)] (e_k / E)^nm,
 *   e_k = E - k Ewell, added one k at a time as the numpy loop adds them.
 * tab (hmax, ncols); every array (n,) contiguous.
 * ============================================================================================ */
void nx_sum_terms(int64_t n, const double *een, const double *ewn, const int64_t *hn,
                  const double *nmn, int64_t hmax, const double *tab, int64_t ncols, double *acc)
{
    for (int64_t x = 0; x < n; x++) {
        double e = een[x], a = 1.0;
        int64_t h = hn[x];
        int64_t hc = h < 0 ? 0 : (h > ncols - 1 ? ncols - 1 : h);
        if (e > 0.0) {
            for (int64_t k = 1; k <= hmax; k++) {
                double ek = e - k * ewn[x];
                if (ek > 0.0 && h >= k) a += tab[(k - 1) * ncols + hc] * pow(ek / e, nmn[x]);
            }
        }
        acc[x] = a;
    }
}
