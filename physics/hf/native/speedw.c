/* SPEEDW: compiled kernels of the whole-run speed work. Loader: physics/hf/native/speedw.py;
 * build: scripts/build_speedw_native.sh (lib/libspeedw.so, gitignored).
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * 1. sw_dwba_numerov -- ecis.dwba.distorted_waves's Numerov loop, BIT-IDENTICAL to the torch loop.
 *    TALYS routine: ecist.f:18285 (inri). What the torch operations compute there (probed on the
 *    loop's own inputs, 12 DWBA calls of Fe-56 / Eu-145 / Ca-40, every element equal):
 *      complex a*b, both contiguous: plain (ar*br - ai*bi, ar*bi + ai*br) on the first N - N%4
 *                                    elements of the (NK, NLJ) result, the fma form on the rest;
 *      complex a*b, a a strided view (y[:, :, i-1]): the fma form on every element;
 *      complex a/b:                  Smith's division with the fma form on every element;
 *      a real scalar times a complex array, and complex +/-: exact componentwise.
 *    The elements never mix, so the kernel runs each (k, lj) row over all radial steps in turn
 *    (cache-friendly) instead of each radial step over all rows, which changes no operation.
 *
 * 2. sw_mpe_bin -- multipreeq2.f90 for one mother bin (preeq/multi.py's loop). NOT bit-identical
 *    to the torch loop (see below). TALYS routines: multipreeq2.f90:1 (multipreeq2),
 *    phdens2.f90:1 (phdens2), finitewell.f90:1 (finitewell, the surfwell = .false. branch),
 *    preeqinit.f90:1 (Apauli2, nfac).
 *
 * The statement order is `multiple_preequilibrium`'s, which is TALYS's. The arithmetic is the
 * same IEEE operations in the same order, with two exceptions that make this path differ from
 * the torch one in the last bits (and only at Einc >= emulpre, where multipreeq2 runs at all):
 *   - pow() is glibc's; torch's CPU pow takes a SIMD kernel for arrays of 8 elements or more;
 *   - a sum over a row is left to right; torch.sum accumulates in lanes.
 * Build with scripts/build_mpe_native.sh (no FMA contraction, no reassociation, no vectorised
 * reductions), so one build gives one set of bits.
 */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define NUMZPH 4
#define NUMNPH 8
#define NFACN 26
#define FEED_MIN_MB 1.0e-10
#define PHDENS_FLOOR 1.0e-10

static double NFAC[NFACN];
static int nfac_ready = 0;

static void nfac_init(void) {
    if (nfac_ready) return;
    for (int n = 0; n < NFACN; n++) {
        double out = 1.0;
        for (int i = 2; i <= n; i++) out *= (double)i;
        NFAC[n] = out;
    }
    nfac_ready = 1;
}

static double fact(int64_t n) {
    if (n < 0) n = 0;
    if (n > NFACN - 1) n = NFACN - 1;
    return NFAC[n];
}

/* ((-1)^k) * ncomb(h, k), as particle_hole._signed_ncomb_table builds it */
static double coef(int64_t k, int64_t h) {
    if (h > NFACN - 1) h = NFACN - 1;
    double sign = (k % 2) ? -1.0 : 1.0;
    double nc = (k < 0 || k > h) ? 0.0 : NFAC[h] / (NFAC[k] * NFAC[h - k]);
    return sign * nc;
}

static double apauli2(int64_t pp, int64_t hp, int64_t pn, int64_t hn, double gsp, double gsn) {
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

/* finitewell(p, h, Eex, Ewell, surfwell = .false.) */
static double finitewell_plain(int64_t p, int64_t h, double eex, double ew) {
    int64_t n = p + h;
    double nm1 = (double)(n - 1);
    double acc = 1.0;
    for (int64_t k = 1; k <= h; k++) {
        double ek = eex - (double)k * ew;
        int ok = (ek > 0.0) && (h >= k) && (eex > 0.0);
        double safe = eex > 0.0 ? eex : 1.0;
        double ratio = ok ? ek / safe : 1.0;
        double term = coef(k, h) * pow(ratio, nm1);
        if (!ok) term = 0.0;
        acc = acc + term;
    }
    if ((eex <= ew) || (h == 1 && n == 1)) acc = 1.0;
    return acc;
}

static double phdens2(int64_t ppi, int64_t hpi, int64_t pnu, int64_t hnu, double gsp,
                      double gsn, double ex, double ew, double ap2) {
    double ppf = (double)ppi, hpf = (double)hpi, pnf = (double)pnu, hnf = (double)hnu;
    double factorn = (pnf * pnf + hnf * hnf + pnf + hnf) / (4.0 * gsn);
    double factorp = (ppf * ppf + hpf * hpf + ppf + hpf) / (4.0 * gsp);
    int64_t n = ppi + hpi + pnu + hnu;
    int64_t p = ppi + pnu;
    int64_t h = hpi + hnu;
    double n1 = (double)(n - 1);
    int ok = ppi >= 0 && hpi >= 0 && pnu >= 0 && hnu >= 0 && n != 0 &&
             (ap2 + factorn + factorp < ex);
    double fac1 = fact(ppi) * fact(hpi) * fact(pnu) * fact(hnu) * fact(n - 1);
    double factor = pow(gsp, (double)(ppi + hpi)) * pow(gsn, (double)(pnu + hnu)) / fac1;
    double u = ok ? ex - ap2 : 1.0;
    double dens = factor * pow(u, n1);
    dens = dens * finitewell_plain(p, h, ex, ew);
    if (!ok) dens = 0.0;
    if (dens < PHDENS_FLOOR) dens = 0.0;
    return dens;
}

int64_t sw_version(void) { return 1; }

#if !defined(__aarch64__)
static inline void cmul_plain(double ar, double ai, double br, double bi, double *r, double *i)
{
    *r = ar * br - ai * bi;
    *i = ar * bi + ai * br;
}

static inline void cmul_fma(double ar, double ai, double br, double bi, double *r, double *i)
{
    *r = fma(ar, br, -(ai * bi));
    *i = fma(ar, bi, ai * br);
}

static inline void cdiv_fma(double ar, double ai, double br, double bi, double *r, double *i)
{
    if (fabs(br) >= fabs(bi)) {
        const double rat = bi / br, scl = 1.0 / fma(bi, rat, br);
        *r = fma(ai, rat, ar) * scl;
        *i = fma(-ar, rat, ai) * scl;
    } else {
        const double rat = br / bi, scl = 1.0 / fma(br, rat, bi);
        *r = fma(ar, rat, ai) * scl;
        *i = fma(ai, rat, -ar) * scl;
    }
}

#endif

/* distorted_waves: f (NLJ, n+1, 2), k2 (NK, 2), c = h*h/12, y1 (NLJ,) = h**(l+1); y out
 * (NK, NLJ, n+1, 2), every element written. */
#if defined(__aarch64__)
/* COREX (arm64 only; NOT bit-identical to the torch loop): the same recurrence
 *   y(i+1) = (2 y(i) (1 + 5c f(i)) - y(i-1) (1 - c f(i-1))) / (1 - c f(i+1)),  f = fval - k2,
 * with every coefficient computed first (they carry no state) and the division replaced by a
 * product with conj(D) / |D|^2, so the recurrences carry only multiplies; eight rows are stepped
 * side by side, which the out-of-order core runs in parallel. Rows agree with the bit-identical
 * loop to ~1e-9 relative (tests/hf/test_corex.py). */
enum { SW_ROWS = 8 };

void sw_dwba_numerov(int64_t NK, int64_t NLJ, int64_t n, const double *f, const double *k2,
                     double c, const double *y1, double *y)
{
    const int64_t N = NK * NLJ, S = n + 1;
    const double c5 = 5.0 * c;
    double *co = malloc(sizeof(double) * 6 * (size_t)(SW_ROWS * S));
    if (co == NULL)
        abort();
    for (int64_t q0 = 0; q0 < N; q0 += SW_ROWS) {
        const int r = (int)(N - q0 < SW_ROWS ? N - q0 : SW_ROWS);
        for (int j = 0; j < r; j++) {
            const int64_t q = q0 + j, kk = q / NLJ, lj = q % NLJ;
            const double *fr = f + 2 * (lj * S);
            const double kr = k2[2 * kk], ki = k2[2 * kk + 1];
            double *cq = co + 6 * (j * S);
            for (int64_t i = 0; i < S; i++) {
                const double gr = fr[2 * i] - kr, gi = fr[2 * i + 1] - ki;
                const double dr = 1.0 - c * gr, di = -c * gi;
                const double s = 1.0 / (dr * dr + di * di);
                cq[6 * i] = 1.0 + c5 * gr;  /* the y(i) factor at i */
                cq[6 * i + 1] = c5 * gi;
                cq[6 * i + 2] = dr;         /* the y(i-1) factor when i - 1 is this node */
                cq[6 * i + 3] = di;
                cq[6 * i + 4] = dr * s;     /* 1 / D when i + 1 is this node */
                cq[6 * i + 5] = -di * s;
            }
            double *yq = y + 2 * (q * S);
            yq[0] = 0.0;
            yq[1] = 0.0;
            yq[2] = y1[lj];
            yq[3] = 0.0;
        }
        for (int64_t i = 1; i < n; i++) {
            const int64_t im = i > 1 ? i - 1 : 1; /* fval(0) is fval(1) at the first step */
            for (int j = 0; j < r; j++) {
                const double *cq = co + 6 * (j * S);
                double *yq = y + 2 * ((q0 + j) * S);
                const double ar = 2.0 * yq[2 * i], ai = 2.0 * yq[2 * i + 1];
                const double br = cq[6 * i], bi = cq[6 * i + 1];
                const double cr = cq[6 * im + 2], ci = cq[6 * im + 3];
                const double y0r = yq[2 * (i - 1)], y0i = yq[2 * (i - 1) + 1];
                const double tr = (ar * br - ai * bi) - (y0r * cr - y0i * ci);
                const double ti = (ar * bi + ai * br) - (y0r * ci + y0i * cr);
                const double wr = cq[6 * (i + 1) + 4], wi = cq[6 * (i + 1) + 5];
                yq[2 * (i + 1)] = tr * wr - ti * wi;
                yq[2 * (i + 1) + 1] = tr * wi + ti * wr;
            }
        }
    }
    free(co);
}
#else
void sw_dwba_numerov(int64_t NK, int64_t NLJ, int64_t n, const double *f, const double *k2,
                     double c, const double *y1, double *y)
{
    const int64_t N = NK * NLJ, S = n + 1, TAIL = N - N % 4;
    const double c5 = 5.0 * c;
    for (int64_t q = 0; q < N; q++) {
        const int64_t kk = q / NLJ, lj = q % NLJ;
        const int tail = q >= TAIL;
        const double *fr = f + 2 * (lj * S);
        const double kr = k2[2 * kk], ki = k2[2 * kk + 1];
        double *yq = y + 2 * (q * S);
        yq[0] = 0.0;
        yq[1] = 0.0;
        yq[2] = y1[lj];
        yq[3] = 0.0;
        double fmr = fr[2] - kr, fmi = fr[3] - ki;  /* fval(1) */
        double f0r = fmr, f0i = fmi;
        for (int64_t i = 1; i < n; i++) {
            const double fpr = fr[2 * (i + 1)] - kr, fpi = fr[2 * (i + 1) + 1] - ki;
            const double ar = 2.0 * yq[2 * i], ai = 2.0 * yq[2 * i + 1];
            const double br = 1.0 + c5 * f0r, bi = 0.0 + c5 * f0i;
            double ur, ui;
            if (tail)
                cmul_fma(ar, ai, br, bi, &ur, &ui);
            else
                cmul_plain(ar, ai, br, bi, &ur, &ui);
            const double cr = 1.0 - c * fmr, ci = 0.0 - c * fmi;
            double vr, vi;
            cmul_fma(yq[2 * (i - 1)], yq[2 * (i - 1) + 1], cr, ci, &vr, &vi);
            const double dr = 1.0 - c * fpr, di = 0.0 - c * fpi;
            cdiv_fma(ur - vr, ui - vi, dr, di, &yq[2 * (i + 1)], &yq[2 * (i + 1) + 1]);
            fmr = f0r;
            fmi = f0i;
            f0r = fpr;
            f0i = fpi;
        }
    }
}
#endif

/* One mother bin. Shapes: mother (P1^4, in: entry state, out: exit state), d_* (2,) and
 * (2, b), jw (2, b, nj1). Outputs: scal = [summpe, sumtype_tot(1), sumtype_tot(2), mulpre(1),
 * mulpre(2)], term_tot (2, b) and xspop_add (2, b, nj1) zero on entry; the daughters' particle-
 * hole additions as `keys` (cap, 5) = (type, ipp, ihp, ipn, ihn) in first-touch order with their
 * rows in `dpop` (cap, b). `key_of` (2 P1^4) and `term` (2 b) are scratch. Returns the number of keys, -1 if `cap`
 * was too small. */
int64_t sw_mpe_bin(int64_t P, int64_t b, int64_t nj1, double *mother, double exinc, double dexinc,
                double gsp0, double gsn0, double gp_cn0, double gn_cn0, double ef,
                const int64_t *d_type, const int64_t *d_zix, const int64_t *d_nix,
                const int64_t *d_nlast, const int64_t *d_nexmax, const int64_t *d_parskip,
                const double *d_s, const double *d_gp, const double *d_gn, const double *d_ex,
                const double *d_dex, const double *d_tsw, const double *jw, double *scal,
                double *term_tot, double *xspop_add, int64_t *key_of, int64_t *keys,
                double *dpop, int64_t cap, double *term) {
    nfac_init();
    const int64_t P1 = P + 1;
    const int64_t P4 = P1 * P1 * P1 * P1;
    for (int64_t i = 0; i < 2 * P4; i++) key_of[i] = -1;
    int64_t nkeys = 0;
    double gsp_state = gsp0, gsn_state = gsn0;
    double summpe = 0.0, sumtype_tot[2] = {0.0, 0.0};
    int mulpre[2] = {0, 0};
    int64_t last_nlast = d_nlast[0];
    static const int64_t PARZ[3] = {0, 0, 1}, PARN[3] = {0, 1, 0};

    for (int64_t ipp = 0; ipp <= P; ipp++)
    for (int64_t ihp = 0; ihp <= P; ihp++)
    for (int64_t ipn = 0; ipn <= P; ipn++) {
        int64_t ip = ipp + ipn;
        if (ip == 0 || ip > P) continue;
        for (int64_t ihn = 0; ihn <= P; ihn++) {
            int64_t ih = ihp + ihn;
            if (ih == 0 || ih > P) continue;
            double feedph = mother[((ipp * P1 + ihp) * P1 + ipn) * P1 + ihn];
            if (feedph <= FEED_MIN_MB) continue;
            double ap = apauli2(ipp, ihp, ipn, ihn, gp_cn0, gn_cn0);
            double omegaph = phdens2(ipp, ihp, ipn, ihn, gsp_state, gsn_state, exinc, ef, ap);
            int live_om = omegaph > 0.0;
            memset(term, 0, (size_t)(2 * b) * sizeof(double));
            double sumtype[2] = {0.0, 0.0};
            double sumterm = 0.0;
            for (int di = 0; di < 2; di++) {
                int64_t t = d_type[di], ti = t - 1;
                if (d_parskip[di]) continue;
                last_nlast = d_nlast[di];
                if (d_zix[di] > NUMZPH || d_nix[di] > NUMNPH) continue;
                int64_t zej = PARZ[t], nej = PARN[t];
                if (ipp - zej < 0 || ipn - nej < 0) continue;
                int64_t lo = d_nlast[di] + 1, hi = d_nexmax[di];
                if (hi < lo) continue;
                double *tr = term + ti * b;
                if (live_om) {
                    double gsp_o = d_gp[di], gsn_o = d_gn[di];
                    gsp_state = gsp_o;
                    gsn_state = gsn_o;
                    const double *ex = d_ex + di * b, *dex = d_dex + di * b, *tsw = d_tsw + di * b;
                    double ap1 = apauli2(ipp - zej, ihp, ipn - nej, ihn, gp_cn0, gn_cn0);
                    double ap1p = apauli2(zej, 0, nej, 0, gp_cn0, gn_cn0);
                    double exm = exinc + 0.5 * dexinc - d_s[di];
                    double exmin = ex[hi] - 0.5 * dex[hi];
                    double rsum = 0.0;
                    for (int64_t j = lo; j <= hi; j++) {
                        double omegap1h = phdens2(ipp - zej, ihp, ipn - nej, ihn, gsp_o, gsn_o,
                                                  ex[j], ef, ap1);
                        double omega1p = phdens2(zej, 0, nej, 0, gsp_o, gsn_o, exinc - ex[j],
                                                 ef, ap1p);
                        double proba = omega1p * omegap1h / omegaph / (double)(ipp + ipn);
                        double pescape = proba * tsw[j];
                        double dj = (j == hi) ? exm - exmin : dex[j];
                        double row = feedph * pescape * dj;
                        tr[j] = row;
                        rsum = rsum + row;
                    }
                    sumterm = sumterm + rsum;
                }
                double s = 0.0;
                for (int64_t j = lo; j <= hi; j++) s = s + tr[j];
                sumtype[ti] = sumtype[ti] + s;
            }
            if (sumterm > feedph) {
                double scale = feedph / sumterm;
                for (int di = 0; di < 2; di++) {
                    int64_t ti = d_type[di] - 1;
                    int64_t lo = last_nlast + 1, hi = d_nexmax[di];
                    if (hi >= lo) {
                        double *tr = term + ti * b;
                        for (int64_t j = lo; j <= hi; j++) tr[j] = tr[j] * scale;
                    }
                    sumtype[ti] = sumtype[ti] * scale;
                }
            }
            double sumph = 0.0;
            for (int di = 0; di < 2; di++) {
                int64_t t = d_type[di], ti = t - 1;
                if (d_parskip[di] || d_zix[di] > NUMZPH || d_nix[di] > NUMNPH) continue;
                int64_t zej = PARZ[t], nej = PARN[t];
                if (ipp - zej < 0 || ipn - nej < 0) continue;
                int64_t lo = d_nlast[di] + 1, hi = d_nexmax[di];
                if (hi >= lo) {
                    const double *tr = term + ti * b;
                    int64_t kidx = ti * P4 + (((ipp - zej) * P1 + ihp) * P1 + (ipn - nej)) * P1 + ihn;
                    int64_t slot = key_of[kidx];
                    if (slot < 0) {
                        if (nkeys >= cap) return -1;
                        slot = nkeys++;
                        key_of[kidx] = slot;
                        keys[slot * 5] = t;
                        keys[slot * 5 + 1] = ipp - zej;
                        keys[slot * 5 + 2] = ihp;
                        keys[slot * 5 + 3] = ipn - nej;
                        keys[slot * 5 + 4] = ihn;
                        double *dr = dpop + slot * b;
                        for (int64_t j = 0; j < b; j++) dr[j] = 0.0;
                        for (int64_t j = lo; j <= hi; j++) dr[j] = tr[j];
                    } else {
                        double *dr = dpop + slot * b;
                        for (int64_t j = lo; j <= hi; j++) dr[j] = dr[j] + tr[j];
                    }
                    double *tt = term_tot + ti * b;
                    for (int64_t j = lo; j <= hi; j++) {
                        tt[j] = tt[j] + tr[j];
                        double *xa = xspop_add + (ti * b + j) * nj1;
                        const double *w = jw + (ti * b + j) * nj1;
                        for (int64_t J = 0; J < nj1; J++) xa[J] = xa[J] + tr[j] * w[J];
                    }
                }
                sumph = sumph + sumtype[ti];
                summpe = summpe + sumtype[ti];
                sumtype_tot[ti] = sumtype_tot[ti] + sumtype[ti];
                if (sumtype[ti] != 0.0) mulpre[ti] = 1;
            }
            if (ip <= P - 1 && ih <= P - 1) {
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
    scal[0] = summpe;
    scal[1] = sumtype_tot[0];
    scal[2] = sumtype_tot[1];
    scal[3] = mulpre[0];
    scal[4] = mulpre[1];
    return nkeys;
}
