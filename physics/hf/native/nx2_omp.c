/* NATIVEX2 lever `omp`: the spherical optical-model solve of `omp.schrodinger` (ECIS's integrator,
 * card rounding and matching) for one (target, particle) over an energy axis in one call, plus the
 * pieces the torch path exposes on their own (card quantisation, ECIS's grid, Coulomb functions).
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 * ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license.
 *
 * nx2_omp_card     -- `ecis_card_value` (mode 0) / `ecis_card_energy` (mode 1): f10.5, or es10.3,
 *                     with the straight-through forward value x + (y - x).
 * nx2_omp_grid     -- `ecis_grid` (lect, ecist.f:3627): h, ism, rm per energy.
 * nx2_omp_coulomb  -- `coulomb_functions` (fcou, ecist.f:5775) for one call: F, F', G, G' for
 *                     L = 0..L1-1. The inward Numerov (under the barrier) takes the call's step
 *                     count, from its largest range, as the torch call does over its batch; the
 *                     continued fractions start from their own column's rho (converged either way).
 *                     The Numerov itself is `native.numerov_inward`'s kernel when it is handed over
 *                     (`nx2_omp_set_numerov`), else a copy of its recurrence.
 * nx2_omp_job      -- `solve_spherical` with ECIS's integrator: card rounding, relativistic
 *                     kinematics (lecl, khco), the grid, the potentials (wosa), the modified
 *                     Numerov per (l, j) (the loop of `native.ecis_job`), the Coulomb functions,
 *                     tlnc's matching (ecist.f:14445) and the reaction/total/shape-elastic sums.
 *                     `active[e] = 0` skips an energy (zeros out); `cap[e]` is the last l whose
 *                     T_lj is written (the rows above it are the zeros `_clip_to_njmax` leaves);
 *                     with `tail` the rows above `cap` are still solved for the cross sections
 *                     unless the capped row's contribution is below 1e-14 of the sum (beyond
 *                     njmax, l is far past grazing and T_l falls by orders per step).
 *                     `rounding`: bit 1 rounds the energy and the masses (`ecis_rounding`),
 *                     bit 2 the potential cards (`CARD_ROUNDING`).
 * Every energy runs only its own ism radial steps (the torch loop runs the batch's largest and
 * rescales the matching values on the way; the ratio tlnc forms is scale-free). Held to closeness
 * with the torch path, not to bits. Returns 0, or -1 (allocation failed). */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifdef __clang__
#pragma STDC FP_CONTRACT OFF
#endif

/* ECIS-06's constants (schrodinger.py) */
static const double OMP_CM = 931.494043;
static const double OMP_CHB = 197.326968;
static const double OMP_CZ = 137.03599911;
static const double OMP_ACONV = 1.0e-10;
static const double OMP_PI = 3.141592653589793;
#define OMP_NCOL 19

/* ------------------------------------------------------------------------------ input cards */
static double nx2_omp_f10_5(double x) { return nearbyint(x * 1.0e5) / 1.0e5; }

static double nx2_omp_es10_3(double x)
{
    const double ax = x == 0.0 ? 1.0 : fabs(x);
    const double e = floor(log10(ax));
    const double m = nearbyint(x / pow(10.0, e) * 1.0e3) / 1.0e3;
    return x == 0.0 ? x : m * pow(10.0, e);
}

static double nx2_omp_value(double x)
{
    const double y = fabs(x) >= 1000.0 ? nx2_omp_es10_3(x) : nx2_omp_f10_5(x);
    return x + (y - x);
}

static double nx2_omp_energy(double x)
{
    const double y = x >= 0.01 ? nx2_omp_f10_5(x) : nx2_omp_es10_3(x);
    return x + (y - x);
}

void nx2_omp_card(int64_t n, int64_t mode, const double *x, double *out)
{
    for (int64_t i = 0; i < n; i++)
        out[i] = mode ? nx2_omp_energy(x[i]) : nx2_omp_value(x[i]);
}

/* ------------------------------------------------------------------------------ ECIS's grid */
static void nx2_omp_grid1(const double *q, int64_t E, int64_t e, double am3, double k, double ecm,
                          double *h_out, int64_t *ism_out, double *rm_out)
{
    const double w3 = k / (OMP_ACONV * ecm);
    double rm = 0.0, w2 = 1.0e21;
    for (int p = 0; p < 6; p++) {
        const double dep = fabs(q[3 * p * E + e]);
        const double R = q[(3 * p + 1) * E + e] * am3;
        const double aa = q[(3 * p + 2) * E + e];
        if (dep != 0.0) {
            const double val = R + log(w3 * dep) * aa;
            rm = (rm != rm || val != val) ? NAN : (val > rm ? val : rm);
            w2 = (w2 != w2 || aa != aa) ? NAN : (aa < w2 ? aa : w2);
        }
    }
    const double rc = q[18 * E + e] * am3;
    rm = (rm != rm || rc != rc) ? NAN : (rc > rm ? rc : rm);
    const double a = w2 / 2.0, b = 0.5 / k;
    double h = (a != a || b != b) ? NAN : (b < a ? b : a);
    int64_t ism = (int64_t)floor(rm / h + 0.5);
    if (ism < 4)
        ism = 4;
    h = rm / (double)ism;
    *h_out = h;
    *ism_out = ism;
    *rm_out = h * (double)ism;
}

void nx2_omp_grid(int64_t E, int64_t rounding, const double *cols, double m_targ, const double *k,
                  const double *ecm, double *h, int64_t *ism, double *rm)
{
    double *q = malloc(sizeof(double) * (size_t)(OMP_NCOL * E > 0 ? OMP_NCOL * E : 1));
    if (!q)
        return;
    for (int64_t i = 0; i < OMP_NCOL * E; i++)
        q[i] = rounding ? nx2_omp_value(cols[i]) : cols[i];
    const double am3 = pow(m_targ, 1.0 / 3.0);
    for (int64_t e = 0; e < E; e++)
        nx2_omp_grid1(q, E, e, am3, k[e], ecm[e], h + e, ism + e, rm + e);
    free(q);
}

/* ------------------------------------------------------------------------ Coulomb functions */
static inline double nx2_omp_sign(double d)
{
    if (d > 0.0)
        return 1.0;
    if (d < 0.0)
        return -1.0;
    return d; /* 0 or nan, as np.sign */
}

/* `_cf1`: F'_L/F_L for L = 0..width-1 (written when out != NULL) by the backward recurrence from
 * ltop, and the sign of F_0/F_ltop; returns f_0. */
static double nx2_omp_cf1(double eta, double rho, int64_t ltop, int64_t width, double *out,
                          double *sign)
{
    const double inv = 1.0 / rho;
    double Li = (double)(ltop + 1);
    double f = Li * inv + eta / Li, sg = 1.0;
    for (int64_t L = ltop; L > 0; L--) {
        const double dl = (double)L;
        const double S = dl * inv + eta / dl;
        const double q = eta / dl;
        const double R2 = 1.0 + q * q;
        double d = S + f;
        if (fabs(d) < 1.0e-290)
            d = 1.0e-290;
        sg = sg * nx2_omp_sign(d);
        f = S - R2 / d;
        if (out && L - 1 < width)
            out[L - 1] = f;
    }
    *sign = sg;
    return f;
}

/* `_cf2`: p + i q = H+'/H+ at L = 0 (Steed's CF2). */
static void nx2_omp_cf2(double eta, double rho, double *p_out, double *q_out)
{
    const double xi = 1.0 / rho, wi = 2.0 * eta;
    double p = 0.0, q = 1.0 - eta * xi;
    double ar = -(eta * eta), ai = eta, br = 2.0 * (rho - eta), bi = 2.0;
    double dr = br / (br * br + bi * bi), di = -bi / (br * br + bi * bi);
    double dp = -xi * (ar * di + ai * dr), dq = xi * (ar * dr - ai * di), pk = 0.0;
    for (int it = 0; it < 20000; it++) {
        p = p + dp;
        q = q + dq;
        pk = pk + 2.0;
        ar = ar + pk;
        ai = ai + wi;
        bi = bi + 2.0;
        const double d = ar * dr - ai * di + br;
        di = ai * dr + ar * di + bi;
        double c = 1.0 / (d * d + di * di);
        dr = c * d;
        di = -c * di;
        const double a = br * dr - bi * di - 1.0;
        const double b = bi * dr + br * di;
        c = dp * a - dq * b;
        dq = dp * b + dq * a;
        dp = c;
        if ((fabs(dp) + fabs(dq)) < (fabs(p) + fabs(q)) * 1.0e-15)
            break;
    }
    *p_out = p;
    *q_out = q;
}

/* `_steed_g0`: G_0 and dG_0/drho at rho by Steed's method, CF1 started at ltop. */
static void nx2_omp_steed(double eta, double rho, int64_t ltop, double *g, double *dg)
{
    double sign, p, q;
    const double f0 = nx2_omp_cf1(eta, rho, ltop, 0, NULL, &sign);
    nx2_omp_cf2(eta, rho, &p, &q);
    const double gam = (f0 - p) / q;
    const double w = 1.0 / sqrt((f0 - p) * gam + q);
    const double F0 = sign * w;
    *g = gam * F0;
    *dg = (p * gam - q) * F0;
}

/* `_numerov_inward` for up to eight columns sharing the step count nn (lanes padded by the
 * caller), in the arm64 kernel's form: 1 - 2 eta / x evaluated once per node. out[j] = u(ra),
 * u(ra - h), u(ra + h), h, c, 2 eta. Used when `native.numerov_inward`'s kernel is not handed
 * over (`nx2_omp_set_numerov`). */
static void nx2_omp_numerov8(const double *ee, const double *ra, const double *rb, const double *gb,
                             const double *gb1, int64_t nn, double out[8][6])
{
    double h[8], c[8], c5[8], e2[8], u1[8], u2[8], q1[8], q2[8], prev[8];
    for (int j = 0; j < 8; j++) {
        h[j] = (rb[j] - ra[j]) / (double)nn;
        c[j] = h[j] * h[j] / 12.0;
        c5[j] = 5.0 * c[j];
        e2[j] = 2.0 * ee[j];
        q2[j] = 1.0 - e2[j] / ((rb[j] - h[j]) + h[j]);
        q1[j] = 1.0 - e2[j] / (rb[j] - h[j]);
        u2[j] = gb[j];
        u1[j] = gb1[j];
        prev[j] = 0.0;
    }
    for (int64_t i = 2; i < nn + 2; i++) {
        const double di = (double)i;
        for (int j = 0; j < 8; j++) {
            const double x0 = rb[j] - di * h[j];
            const double q0 = 1.0 - e2[j] / x0;
            const double A = 2.0 * (1.0 - c5[j] * q1[j]);
            const double B = 1.0 + c[j] * q2[j];
            const double C = 1.0 + c[j] * q0;
            const double t = A * u1[j] - B * u2[j];
            u2[j] = u1[j];
            u1[j] = t / C;
            q2[j] = q1[j];
            q1[j] = q0;
        }
        if (i == nn - 1)
            for (int j = 0; j < 8; j++)
                prev[j] = u1[j];
    }
    for (int j = 0; j < 8; j++) {
        out[j][0] = u2[j];
        out[j][1] = u1[j];
        out[j][2] = prev[j];
        out[j][3] = h[j];
        out[j][4] = c[j];
        out[j][5] = e2[j];
    }
}

/* `native.numerov_inward`'s compiled kernel (hf_numerov_inward), handed over by address */
typedef void (*nx2_omp_numerov_t)(int64_t, const double *, const double *, const double *,
                                  const double *, const double *, const int64_t *, double *,
                                  double *, double *, double *, double *, double *);
static nx2_omp_numerov_t nx2_omp_numerov_ext;

void nx2_omp_set_numerov(void *f) { nx2_omp_numerov_ext = (nx2_omp_numerov_t)f; }

static inline double nx2_omp_max(double a, double b)
{
    return (a != a || b != b) ? NAN : (b > a ? b : a);
}

/* `coulomb_functions(eta, rho, L1 - 1)` on the columns with active[e] != 0 (NULL: all). The
 * inward Numerov's step count is the call's (from its largest range, over every column). The
 * continued fractions start at int(rho) + 60 of their own column rather than of the call's largest
 * rho: they have converged many orders below either start (checked against the call-wide start on
 * the bench targets: the same T_lj). F, dF, G, dG: (E, L1). */
static int nx2_omp_coulomb_cols(int64_t E, int64_t L1, const double *eta, const double *rho,
                                const int64_t *active, double *F, double *dF, double *G,
                                double *dG)
{
    const int64_t lmax = L1 - 1;
    double max_range = -HUGE_VAL;
    for (int64_t e = 0; e < E; e++) {
        if (eta[e] == 0.0)
            continue;
        const double far = nx2_omp_max(rho[e], 2.0 * eta[e] + 20.0);
        if (far > rho[e])
            max_range = nx2_omp_max(max_range, far - rho[e]);
    }
    int64_t nn = 0;
    if (max_range > -HUGE_VAL) {
        double x = ceil(max_range / 0.004);
        x = x > 200.0 ? x : 200.0;
        x = x < 40000.0 ? x : 40000.0;
        nn = (int64_t)x;
    }
    const int64_t S = E + 8; /* column stride: room to pad the last lane group */
    int64_t *queue = malloc(sizeof(int64_t) * (size_t)S);
    double *cb = malloc(sizeof(double) * 11 * (size_t)S);
    int64_t *nb = malloc(sizeof(int64_t) * (size_t)S);
    if (!queue || !cb || !nb) {
        free(queue);
        free(cb);
        free(nb);
        return -1;
    }
    /* Steed's G_0 beyond the turning point, or the boundary values of the inward Numerov */
    int64_t nq = 0;
    for (int64_t e = 0; e < E; e++) {
        if (active && !active[e])
            continue;
        const double r = rho[e], et = eta[e];
        if (et == 0.0) {
            G[e * L1] = cos(r);
            dG[e * L1] = -sin(r);
            continue;
        }
        const double far = nx2_omp_max(r, 2.0 * et + 20.0);
        if (far > r) {
            const double h = (far - r) / (double)nn;
            double dg;
            queue[nq] = e;
            nx2_omp_steed(et, far, (int64_t)far + 60, &cb[3 * S + nq], &dg);
            nx2_omp_steed(et, far - h, (int64_t)(far - h) + 60, &cb[4 * S + nq], &dg);
            nq++;
        } else {
            nx2_omp_steed(et, far, (int64_t)far + 60, &G[e * L1], &dG[e * L1]);
        }
    }
    /* cb: ee, ra, rb, gb, gb1 (inputs), then the six outputs, stride S; the columns are padded
     * to a multiple of eight with copies of the last one, so every lane group is full */
    const int64_t np = (nq + 7) / 8 * 8;
    for (int64_t k = 0; k < np; k++) {
        const int64_t e = queue[k < nq ? k : nq - 1];
        cb[k] = eta[e];
        cb[S + k] = rho[e];
        cb[2 * S + k] = nx2_omp_max(rho[e], 2.0 * eta[e] + 20.0);
        if (k >= nq) {
            cb[3 * S + k] = cb[3 * S + nq - 1];
            cb[4 * S + k] = cb[4 * S + nq - 1];
        }
        nb[k] = nn;
    }
    double *o = cb + 5 * S;
    if (nq > 0 && nx2_omp_numerov_ext) {
        nx2_omp_numerov_ext(np, cb, cb + S, cb + 2 * S, cb + 3 * S, cb + 4 * S, nb, o, o + S,
                            o + 2 * S, o + 3 * S, o + 4 * S, o + 5 * S);
    } else {
        for (int64_t k0 = 0; k0 < np; k0 += 8) {
            double lane[5][8], lo[8][6];
            for (int j = 0; j < 8; j++)
                for (int i = 0; i < 5; i++)
                    lane[i][j] = cb[i * S + k0 + j];
            nx2_omp_numerov8(lane[0], lane[1], lane[2], lane[3], lane[4], nn, lo);
            for (int j = 0; j < 8; j++)
                for (int i = 0; i < 6; i++)
                    o[i * S + k0 + j] = lo[j][i];
        }
    }
    for (int64_t k = 0; k < nq; k++) {
        const int64_t e = queue[k];
        const double ra = rho[e], h = o[3 * S + k], c = o[4 * S + k], e2 = o[5 * S + k];
        G[e * L1] = o[k];
        dG[e * L1] = ((1.0 + 2.0 * c * (1.0 - e2 / (ra + h))) * o[2 * S + k]
                      - (1.0 + 2.0 * c * (1.0 - e2 / (ra - h))) * o[S + k]) / (2.0 * h);
    }
    free(queue);
    free(cb);
    free(nb);
    /* G_L upward, F'_L/F_L from the continued fraction, F by the Wronskian */
    for (int64_t e = 0; e < E; e++) {
        if (active && !active[e])
            continue;
        const double r = rho[e], et = eta[e];
        double *g = G + e * L1, *dg = dG + e * L1;
        for (int64_t L = 1; L <= lmax; L++) {
            const double dl = (double)L;
            const double S = (1.0 / r) * dl + et / dl;
            const double qq = et / dl;
            const double R = sqrt(1.0 + qq * qq);
            g[L] = (S * g[L - 1] - dg[L - 1]) / R;
            dg[L] = R * g[L - 1] - S * g[L];
        }
        double sign;
        double *f = F + e * L1; /* F'_L/F_L first, then F_L in place */
        nx2_omp_cf1(et, r, lmax + (int64_t)r + 60, L1, f, &sign);
        for (int64_t L = 0; L <= lmax; L++) {
            const double fl = f[L];
            const double FL = 1.0 / (fl * g[L] - dg[L]);
            F[e * L1 + L] = FL;
            dF[e * L1 + L] = fl * FL;
        }
    }
    return 0;
}

int nx2_omp_coulomb(int64_t E, int64_t L1, const double *eta, const double *rho, double *F,
                    double *dF, double *G, double *dG)
{
    return nx2_omp_coulomb_cols(E, L1, eta, rho, NULL, F, dF, G, dG);
}

/* ------------------------------------------------------------------------ one channel solve */
/* numpy's Smith division a / b */
static void nx2_omp_cdiv(double ar, double ai, double br, double bi, double *qr, double *qi)
{
    const double abr = fabs(br), abi = fabs(bi);
    if (abr >= abi) {
        if (abr == 0.0 && abi == 0.0) {
            *qr = ar / abr;
            *qi = ai / abi;
            return;
        }
        const double rat = bi / br, scl = 1.0 / (br + bi * rat);
        *qr = (ar + ai * rat) * scl;
        *qi = (ai - ar * rat) * scl;
    } else {
        const double rat = br / bi, scl = 1.0 / (bi + br * rat);
        *qr = (ar * rat + ai) * scl;
        *qi = (ai * rat - ar) * scl;
    }
}

/* The modified Numerov of `_integrate_ecis` for rows l0..l1 of one energy, ism steps: u_am (at
 * r = (ism - 1) h) and u_ap (at (ism + 1) h), 2 doubles per (row, j). cent: L(L+1)/n^2 per
 * (L, n - 1), R nodes per row. st: 6 per (row, j). The (row, j) recurrences of one step are one
 * branch-free loop; the matching values are copied out at their two steps. */
static void nx2_omp_radial(int64_t ism, const double *sor, const double *soi, const double *cer,
                           const double *cei, double kh, double mhh, int64_t l0, int64_t l1,
                           int64_t NJ, const double *ls2, const double *cent, int64_t R,
                           double *st, double *uam, double *uap)
{
    const int64_t T = (l1 - l0 + 1) * NJ;
    double *pr = st, *pi = st + T, *cr = st + 2 * T, *ci = st + 3 * T, *abq = st + 4 * T,
           *lsq = st + 5 * T;
    for (int64_t q = 0; q < T; q++) {
        pr[q] = pi[q] = ci[q] = 0.0;
        cr[q] = 1.0;
        lsq[q] = ls2[l0 * NJ + q];
        uam[2 * q] = uam[2 * q + 1] = uap[2 * q] = uap[2 * q + 1] = 0.0;
    }
    const int64_t im1 = ism - 1;
    for (int64_t n = 1; n <= ism; n++) {
        const int64_t r = n - 1;
        const double s_r = sor[r], s_i = soi[r], c_re = cer[r], c_im = cei[r];
        if (n == im1)
            for (int64_t q = 0; q < T; q++) {
                uam[2 * q] = cr[q];
                uam[2 * q + 1] = ci[q];
            }
        for (int64_t l = l0; l <= l1; l++) {
            const double ab = kh - cent[l * R + r];
            for (int64_t j = 0; j < NJ; j++)
                abq[(l - l0) * NJ + j] = ab;
        }
        for (int64_t q = 0; q < T; q++) {
            const double ls = lsq[q];
            const double gr = abq[q] - (s_r * ls + c_re) * mhh;
            const double gi = 0.0 - (s_i * ls + c_im) * mhh;
            const double xa = gr - (gr * gr - gi * gi) / 12.0;
            const double xb = gi - (gr * gi + gi * gr) / 12.0;
            const double u_r = cr[q], u_i = ci[q];
            const double nr = (2.0 * u_r - pr[q]) - fma(xa, u_r, -(xb * u_i));
            const double ni = (2.0 * u_i - pi[q]) - fma(xa, u_i, xb * u_r);
            pr[q] = u_r;
            pi[q] = u_i;
            cr[q] = nr;
            ci[q] = ni;
        }
        if (n == ism)
            for (int64_t q = 0; q < T; q++) {
                uap[2 * q] = cr[q];
                uap[2 * q + 1] = ci[q];
            }
        if (n % 25 == 0) {
            for (int64_t q = 0; q < T; q++) {
                double s = hypot(cr[q], ci[q]);
                if (!(s != s) && s < 1.0e-300)
                    s = 1.0e-300;
                const double scl = 1.0 / s;
                pr[q] = pr[q] * scl;
                pi[q] = pi[q] * scl;
                cr[q] = cr[q] * scl;
                ci[q] = ci[q] * scl;
                if (im1 <= n) {
                    uam[2 * q] = uam[2 * q] * scl;
                    uam[2 * q + 1] = uam[2 * q + 1] * scl;
                }
                if (ism + 1 <= n + 1) {
                    uap[2 * q] = uap[2 * q] * scl;
                    uap[2 * q + 1] = uap[2 * q + 1] * scl;
                }
            }
        }
    }
}

/* tlnc's matching of rows l0..l1 of one energy: T_lj into trow (3 per l, from l0) and the
 * (2j+1)/(2s+1)-weighted sums of T, 1 - Re S and |1 - S|^2 into acc[0..2]; returns the weighted
 * T sum of row l1. */
static double nx2_omp_match(int64_t ism, double h, double k, double eta, const double *F,
                            const double *dF, const double *G, const double *dG, int64_t l0,
                            int64_t l1, int64_t NJ, double spin, const double *uam,
                            const double *uap, double *trow, double acc[3])
{
    double last = 0.0;
    const double b1c = h * h / 48.0;
    for (int64_t l = l0; l <= l1; l++) {
        const double cll = (double)l * ((double)l + 1.0);
        double av[5], c1 = (double)(ism - 1) * h;
        for (int i = 0; i < 5; i++) {
            av[i] = b1c * (2.0 * k * eta / c1 - k * k + cll / (c1 * c1));
            c1 = c1 + 0.5 * h;
        }
        double a1 = (1 - av[1]) / (2 + 10 * av[1]);
        double b1 = (1 - av[3]) / (2 + 10 * av[3]);
        double a2 = a1 * (1 - av[0]) / (1 - 4 * av[0]);
        double b2 = b1 * (1 - av[4]) / (1 - 4 * av[4]);
        c1 = (2 + 10 * av[2]) - (1 - av[2]) * (a1 + b1);
        a1 = (16 - 144 * av[1]) / (2 + 10 * av[1]);
        b1 = (16 - 144 * av[3]) / (2 + 10 * av[3]);
        const double c2 = (7 + a1 * (1 - av[0])) / (1 - 4 * av[0]);
        const double d2 = (7 + b1 * (1 - av[4])) / (1 - 4 * av[4]);
        const double d1 = (b1 - a1) * (1 - av[2]);
        a1 = a2 * d2 + b2 * c2;
        b1 = (c1 * d2 + d1 * b2) / a1;
        b2 = 30.0 * h * b2 * k / a1;
        const double fam1 = b1 * F[l] - b2 * dF[l];
        const double fam3 = b1 * G[l] - b2 * dG[l];
        b1 = (c2 * c1 - a2 * d1) / a1;
        a2 = -30.0 * h * a2 * k / a1;
        const double fam2 = b1 * F[l] - a2 * dF[l];
        const double fam4 = b1 * G[l] - a2 * dG[l];
        double rowsum = 0.0;
        for (int64_t j = 0; j < NJ; j++) {
            const double jv = (double)l + ((double)j - spin);
            const double lo = fabs((double)l - spin);
            const int64_t q = (l - l0) * NJ + j;
            if (trow)
                trow[3 * (l - l0) + j] = 0.0;
            if (!(jv >= lo - 1.0e-9))
                continue;
            const double amr = uam[2 * q], ami = uam[2 * q + 1];
            const double apr = uap[2 * q], api = uap[2 * q + 1];
            const double Ar = amr * fam4 - fam3 * apr, Ai = ami * fam4 - fam3 * api;
            const double Br = amr * fam2 - fam1 * apr, Bi = ami * fam2 - fam1 * api;
            const double Dr = Ar - Bi, Di = Ai + Br;
            const double w = (2.0 * jv + 1.0) / (2.0 * spin + 1.0);
            double t = 0.0, Sr = 1.0, Si = 0.0;
            if (isfinite(Dr) && isfinite(Di) && hypot(Dr, Di) > 0.0) {
                double Cr, Ci;
                nx2_omp_cdiv(-Br, -Bi, Dr, Di, &Cr, &Ci);
                t = 4.0 * (Ci - Cr * Cr - Ci * Ci);
                if (!(t >= 0.0))
                    t = t != t ? t : 0.0;
                Sr = 1.0 - 2.0 * Ci;
                Si = 2.0 * Cr;
            }
            if (trow)
                trow[3 * (l - l0) + j] = t;
            const double m = hypot(1.0 - Sr, 0.0 - Si);
            rowsum += w * t;
            acc[1] += w * (1.0 - Sr);
            acc[2] += w * (m * m);
        }
        acc[0] += rowsum;
        last = rowsum;
    }
    return last;
}

/* the per-energy solve of `nx2_omp_job` on its buffers (kin: 8 per energy, see below) */
static void nx2_omp_energies(int64_t E, int64_t L1, int64_t NJ, double spin, double zprod,
                             double am3, const double *q, const double *kin, const int64_t *ism,
                             const double *fg, const double *ls2, const int64_t *cap,
                             const int64_t *active, int64_t tail, int64_t max_ism, double *pot,
                             double *st, double *ua, double *trow, double *tjl, double *sig)
{
    const double e2z = OMP_CHB / OMP_CZ * zprod;
    const int64_t P = max_ism + 1;
    double *sor = pot, *soi = pot + P, *cer = pot + 2 * P, *cei = pot + 3 * P, *cent = pot + 4 * P;
    for (int64_t l = 0; l < L1; l++)
        for (int64_t n = 1; n <= P; n++) {
            const double Ld = (double)l, nd = (double)n;
            cent[l * P + n - 1] = (Ld * (Ld + 1.0)) / (nd * nd);
        }
    for (int64_t e = 0; e < E; e++) {
        for (int i = 0; i < 3; i++)
            sig[3 * e + i] = 0.0;
        if (!active[e])
            continue;
        const double h = kin[8 * e + 4], k = kin[8 * e + 1], mu = kin[8 * e + 3];
        const double eta = kin[8 * e + 2];
        const int64_t is = ism[e];
        /* potentials on r_n = n h, n = 1..ism (wosa; `optical_potential`) */
        double R[6], a[6];
        for (int p = 0; p < 6; p++) {
            R[p] = q[(3 * p + 1) * E + e] * am3;
            a[p] = q[(3 * p + 2) * E + e];
            a[p] = a[p] != a[p] ? a[p] : (a[p] < 1.0e-6 ? 1.0e-6 : a[p]);
        }
        const double V = q[e], W = q[3 * E + e], Vd = q[6 * E + e], Wd = q[9 * E + e];
        const double Vso = q[12 * E + e], Wso = q[15 * E + e];
        const double rcr = q[18 * E + e] * am3;
        const double rcc = rcr != rcr ? rcr : (rcr < 1.0e-6 ? 1.0e-6 : rcr);
        for (int64_t n = 1; n <= is; n++) {
            const double r = h * (double)n;
            double f[6], g[6];
            for (int p = 0; p < 6; p++) {
                const double xx = (r - R[p]) / a[p];
                f[p] = 1.0 / (1.0 + exp(xx));
                g[p] = f[p] * (1.0 - f[p]);
            }
            const double re = -V * f[0] - 4.0 * Vd * g[2];
            const double im = -W * f[1] - 4.0 * Wd * g[3];
            const double dvso = -g[4] / a[4] / r;
            const double dwso = -g[5] / a[5] / r;
            double coul = 0.0;
            if (zprod != 0.0) {
                const double rr = r / rcc;
                coul = r < rcr ? e2z / (2.0 * rcc) * (3.0 - rr * rr) : e2z / r;
            }
            sor[n - 1] = 2.0 * (Vso * dvso);
            soi[n - 1] = 2.0 * (Wso * dwso);
            cer[n - 1] = re + coul;
            cei[n - 1] = im;
        }
        const double kh = k * k * h * h, mhh = mu * h * h;
        const int64_t top = cap[e] < L1 - 1 ? cap[e] : L1 - 1;
        double acc[3] = {0.0, 0.0, 0.0};
        const double *Fe = fg + e * L1, *dFe = fg + (E + e) * L1, *Ge = fg + (2 * E + e) * L1,
                     *dGe = fg + (3 * E + e) * L1;
        if (top >= 0) {
            nx2_omp_radial(is, sor, soi, cer, cei, kh, mhh, 0, top, NJ, ls2, cent, P, st, ua,
                           ua + 2 * L1 * NJ);
            const double last = nx2_omp_match(is, h, k, eta, Fe, dFe, Ge, dGe, 0, top, NJ, spin,
                                              ua, ua + 2 * L1 * NJ, trow, acc);
            for (int64_t l = 0; l <= top; l++)
                for (int64_t j = 0; j < NJ; j++)
                    tjl[(e * L1 + l) * 3 + j] = trow[3 * l + j];
            if (tail && top < L1 - 1 && !(last <= 1.0e-14 * acc[0])) {
                nx2_omp_radial(is, sor, soi, cer, cei, kh, mhh, top + 1, L1 - 1, NJ, ls2, cent, P, st,
                               ua, ua + 2 * L1 * NJ);
                nx2_omp_match(is, h, k, eta, Fe, dFe, Ge, dGe, top + 1, L1 - 1, NJ, spin, ua,
                              ua + 2 * L1 * NJ, NULL, acc);
            }
        }
        const double fac = OMP_PI / (k * k) * 10.0;
        sig[3 * e] = fac * acc[0];
        sig[3 * e + 1] = 2.0 * fac * acc[1];
        sig[3 * e + 2] = fac * acc[2];
    }
}

int nx2_omp_job(int64_t E, int64_t L1, int64_t NJ, double spin, double zprod, double m_proj,
                double m_targ, int64_t rounding, const double *e_lab, const double *cols,
                const int64_t *cap, const int64_t *active, int64_t tail, double *tjl, double *sig)
{
    const double m1 = (rounding & 1) ? nx2_omp_value(m_proj) : m_proj;
    const double m2 = (rounding & 1) ? nx2_omp_value(m_targ) : m_targ;
    const size_t En = (size_t)(E > 0 ? E : 1), LJ = (size_t)(L1 * NJ);
    double *q = malloc(sizeof(double) * OMP_NCOL * En);
    double *kin = malloc(sizeof(double) * 8 * En);
    int64_t *ism = malloc(sizeof(int64_t) * En);
    double *fg = malloc(sizeof(double) * 4 * En * (size_t)L1);
    double *ls2 = malloc(sizeof(double) * LJ);
    double *eta = malloc(sizeof(double) * En), *rho = malloc(sizeof(double) * En);
    double *st = malloc(sizeof(double) * 6 * LJ), *ua = malloc(sizeof(double) * 4 * LJ);
    double *trow = malloc(sizeof(double) * 3 * (size_t)L1);
    double *pot = NULL;
    int rc = -1;
    if (q && kin && ism && fg && ls2 && eta && rho && st && ua && trow) {
        for (int64_t i = 0; i < OMP_NCOL * E; i++)
            q[i] = (rounding & 2) ? nx2_omp_value(cols[i]) : cols[i];
        const double am3 = pow(m2, 1.0 / 3.0);
        const double ck = 2.0 * OMP_CM / pow(OMP_CHB, 2.0);
        const double ccz = OMP_CHB / OMP_CZ;
        const double s12 = m1 + m2, dm = pow(pow(m1, 2.0) - pow(m2, 2.0), 2.0);
        /* `ecis_kinematics` (lecl, khco) and `ecis_grid`; kin: ecm, k, eta, mu, h, rm, rho */
        int64_t max_ism = 0;
        for (int64_t e = 0; e < E; e++) {
            const double el = (rounding & 1) ? nx2_omp_energy(e_lab[e]) : e_lab[e];
            const double ecm = OMP_CM * (sqrt(pow(s12, 2.0) + 2.0 * m2 * el / OMP_CM) - m1 - m2);
            const double x = ecm / OMP_CM;
            const double amr = x + m1 + m2;
            const double k2 = 0.125 * ck * ecm * (x + 2.0 * m1 + 2.0 * m2) * (x + 2.0 * m1)
                              * (x + 2.0 * m2) / (amr * amr);
            const double k = sqrt(fabs(k2));
            const double amrd = (pow(amr, 4.0) - dm) / (4.0 * (amr * amr * amr));
            kin[8 * e] = ecm;
            kin[8 * e + 1] = k;
            kin[8 * e + 2] = OMP_CM * ccz * amrd * zprod / k / pow(OMP_CHB, 2.0);
            kin[8 * e + 3] = ck * amrd;
            nx2_omp_grid1(q, E, e, am3, k, ecm, &kin[8 * e + 4], &ism[e], &kin[8 * e + 5]);
            kin[8 * e + 6] = k * kin[8 * e + 5];
            eta[e] = kin[8 * e + 2];
            rho[e] = kin[8 * e + 6];
            if (active[e] && ism[e] > max_ism)
                max_ism = ism[e];
        }
        for (int64_t l = 0; l < L1; l++)
            for (int64_t j = 0; j < NJ; j++) {
                const double jv = (double)l + ((double)j - spin);
                ls2[l * NJ + j] = jv * (jv + 1.0) - (double)l * ((double)l + 1.0)
                                  - spin * (spin + 1.0);
            }
        pot = malloc(sizeof(double) * (size_t)((4 + L1) * (max_ism + 1)));
        if (pot && !nx2_omp_coulomb_cols(E, L1, eta, rho, active, fg, fg + E * L1,
                                         fg + 2 * E * L1, fg + 3 * E * L1)) {
            nx2_omp_energies(E, L1, NJ, spin, zprod, am3, q, kin, ism, fg, ls2, cap, active, tail,
                             max_ism, pot, st, ua, trow, tjl, sig);
            rc = 0;
        }
    }
    free(q);
    free(kin);
    free(ism);
    free(fg);
    free(ls2);
    free(eta);
    free(rho);
    free(st);
    free(ua);
    free(trow);
    free(pot);
    return rc;
}
