/* NATIVEX2 lever `fis2`: the continuum fission transmission through one barrier at a set of
 * excitation energies, off the autograd graph.
 *
 *   nx2_fis2_coef      t1barrier.f90:151-168: the `eintfis` triples of a barrier and the two
 *                      slopes of the logarithmic integration of its level density, taken once per
 *                      grid (`fission_batch_ladder._coefficients`)
 *   nx2_fis2_barrier   t1barrier.f90:1 without a rotational band: the level density integrated
 *                      over each triple (clipped at the energy) times the penetrability at the
 *                      triple's centre, summed per (J, parity), at every energy; the Hill-Wheeler
 *                      magnitude histograms tfisA/rhofisA for one energy on request. The
 *                      penetrability is twkbint.f90 (log-linear interpolation of the WKB table)
 *                      or thill.f90.
 *   nx2_fis2_ladder_weights  the same sum for a whole bin ladder, split as the torch code splits
 *                      it: the (energy, triple) weights in C, the two contractions with the slopes
 *                      as matrix products by the caller
 *
 * The +, -, *, / are the torch expressions' own (`fission.barriers`, `fission.wkb._wkb_interp`,
 * `core.numerics.pol1`) in their order, with contraction off; libm's exp/log may move a last bit
 * against torch's, and the sums over triples run in triple order, so the kernels are held to
 * closeness (tests/hf/test_nx2_fis2.py).
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md. */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifdef __clang__
#pragma STDC FP_CONTRACT OFF
#endif

#define EPS_FIS 1.0e-10 /* t1barrier.f90:158-160 */

/* the triples i = 1, 3, ..., nb-2 of eintfis(0..nb) and rhofis(0..nb, nj2) (nj2 = (maxj+1)*2):
 * elow/emid/eup (S) and A, B (S, nj2); returns S. The top row of a triple is the bottom row of
 * the next one with the same (1 + eps) and eps, so its logarithm is taken once. */
int64_t nx2_fis2_coef(const double *e, const double *rhofis, int64_t nb, int64_t nj2,
                      double *elow, double *emid, double *eup, double *A, double *B)
{
    double *lbuf = (double *)malloc((size_t)(2 * nj2) * sizeof(double));
    if (lbuf == NULL)
        return -1;
    double *lo_row = lbuf, *hi_row = lbuf + nj2; /* log rho1 of this triple, log rho3 of it */
    int64_t s = 0;
    for (int64_t i = 1; i < nb - 1; i += 2, s++) {
        elow[s] = e[i];
        emid[s] = e[i + 1];
        eup[s] = e[i + 2];
        const double *r1p = rhofis + i * nj2;
        const double *r2p = rhofis + (i + 1) * nj2;
        const double *r3p = rhofis + (i + 2) * nj2;
        for (int64_t c = 0; c < nj2; c++) {
            double rho1 = r1p[c] * (1.0 + EPS_FIS) + EPS_FIS;
            double rho2 = r2p[c] + EPS_FIS;
            double rho3 = r3p[c] * (1.0 + EPS_FIS) + EPS_FIS;
            double l1 = s == 0 ? log(rho1) : lo_row[c];
            double l2 = log(rho2), l3 = log(rho3);
            hi_row[c] = l3;
            if (l2 != l1 && l2 != l3) {
                A[s * nj2 + c] = (rho1 - rho2) / (l1 - l2);
                B[s * nj2 + c] = (rho2 - rho3) / (l2 - l3);
            } else {
                A[s * nj2 + c] = rho2;
                B[s * nj2 + c] = rho2;
            }
        }
        double *t = lo_row;
        lo_row = hi_row;
        hi_row = t;
    }
    free(lbuf);
    return s;
}

/* locate.f90 on an ascending uwkb(0..nbins) as core.numerics.locate(uwkb, e, 0, nbins), clamped
 * to [0, nbins-1] */
static int64_t wkb_index(const double *u, int64_t nbins, double x)
{
    int64_t j;
    if (x == u[0]) {
        j = 0;
    } else if (x == u[nbins]) {
        j = nbins - 1;
    } else {
        int64_t lo = 0, hi = nbins + 1;
        while (lo < hi) {
            int64_t mid = lo + (hi - lo) / 2;
            if (u[mid] <= x)
                lo = mid + 1;
            else
                hi = mid;
        }
        j = lo - 1;
    }
    if (j < 0)
        j = 0;
    if (j > nbins - 1)
        j = nbins - 1;
    return j;
}

/* twkbint.f90 as fission.wkb._wkb_interp(uwkb, tab, e, True) */
static double twkbint(const double *u, const double *tab, int64_t nbins, double e)
{
    /* tab holds the table (0..nbins) followed by its logarithms log(max(t, 1e-300)) */
    int64_t n = wkb_index(u, nbins, e);
    double ea = u[n], eb = u[n + 1], ta = tab[n], tb = tab[n + 1];
    int flat = ea == eb;
    double sb = flat ? eb + 1.0 : eb;
    double fac = (e - ea) / (sb - ea);
    double out;
    if (ta > 0 && tb > 0) {
        double la = tab[nbins + 1 + n], lb = tab[nbins + 2 + n];
        out = exp(la + fac * (lb - la));
    } else {
        out = ta + fac * (tb - ta);
    }
    if (flat)
        out = ta;
    if (e > u[nbins])
        out = 1.0;
    return out;
}

/* thill.f90 */
static double thill(double e, double b, double w, double twopi)
{
    double expo = twopi * (e - b) / w;
    if (!(expo > -80.0))
        return 0.0;
    return 1.0 / (1.0 + exp(-expo));
}

/* trfis (n, nj2) and, when not NULL, rhof (n, nj2) at the energies eex[0..n-1]; zero where
 * eex < fecont. With tfisA/rhofisA (nj2, numhill+1) not NULL, n must be 1 and the histograms
 * are accumulated into them (zero on entry) as t1barrier's collect_hill branch. mode 1: WKB
 * table (uwkb 0..nbins; twkb 0..nbins then its logarithms, 2 (nbins+1) values); mode 0:
 * Hill-Wheeler (bfis, wfis). */
int nx2_fis2_barrier(const double *elow, const double *e1, const double *e2, const double *A,
                     const double *B, int64_t S, int64_t nj2, double fecont, const double *eex,
                     int64_t n, int64_t mode, double bfis, double wfis, double twopi,
                     const double *uwkb, const double *twkb, int64_t nbins, double *trfis,
                     double *rhof, double *tfisA, double *rhofisA, int64_t numhill)
{
    if ((tfisA != NULL || rhofisA != NULL) && n != 1)
        return -1;
    if (mode == 1 && (uwkb == NULL || twkb == NULL || nbins < 1))
        return -1;
    int64_t nh = numhill + 1;
    int active = 0;
    for (int64_t k = 0; k < n; k++) {
        double *tr = trfis + k * nj2;
        double *rf = rhof != NULL ? rhof + k * nj2 : NULL;
        memset(tr, 0, (size_t)nj2 * sizeof(double));
        if (rf != NULL)
            memset(rf, 0, (size_t)nj2 * sizeof(double));
        double x = eex[k];
        if (!(x >= fecont) || S < 1)
            continue;
        active = 1;
        for (int64_t s = 0; s < S; s++) {
            if (!(elow[s] <= x))
                continue;
            double emid = e1[s] < x ? e1[s] : x;
            double eup = e2[s] < x ? e2[s] : x;
            double de1 = emid - elow[s], de2 = eup - emid;
            double ee = x - emid;
            double t1 = mode == 1 ? twkbint(uwkb, twkb, nbins, ee) : thill(ee, bfis, wfis, twopi);
            int64_t ihill = (int64_t)(numhill * t1) + 1;
            if (ihill > numhill)
                ihill = numhill;
            const double *a = A + s * nj2, *b = B + s * nj2;
            for (int64_t c = 0; c < nj2; c++) {
                double rho = a[c] * de1 + b[c] * de2;
                double rt = rho * t1;
                tr[c] += rt;
                if (rf != NULL)
                    rf[c] += rho;
                if (tfisA != NULL) {
                    tfisA[c * nh + ihill] += rt;
                    tfisA[c * nh] += rt;
                }
                if (rhofisA != NULL)
                    rhofisA[c * nh + ihill] += rho;
            }
        }
    }
    if (tfisA != NULL && active) { /* t1barrier clamps only when the continuum was integrated */
        for (int64_t c = 0; c < nj2; c++)
            if (tfisA[c * nh] < 1.0e-30)
                tfisA[c * nh] = 1.0e-30;
    }
    return 0;
}

/* fission_batch_ladder._barrier's two (energy, triple) weight matrices: W1 = dE1 * T * keep and
 * W2 = dE2 * T * keep, zero rows where eex < fecont; the transmission is then W1 . A + W2 . B,
 * which the caller takes as two matrix products as the torch code does. */
int nx2_fis2_ladder_weights(const double *elow, const double *e1, const double *e2, int64_t S,
                            double fecont, const double *eex, int64_t n, int64_t mode,
                            double bfis, double wfis, double twopi, const double *uwkb,
                            const double *twkb, int64_t nbins, double *W1, double *W2)
{
    if (mode == 1 && (uwkb == NULL || twkb == NULL || nbins < 1))
        return -1;
    for (int64_t k = 0; k < n; k++) {
        double *w1 = W1 + k * S, *w2 = W2 + k * S;
        double x = eex[k];
        memset(w1, 0, (size_t)S * sizeof(double));
        memset(w2, 0, (size_t)S * sizeof(double));
        if (!(x >= fecont))
            continue;
        for (int64_t s = 0; s < S; s++) {
            if (!(elow[s] <= x))
                continue;
            double emid = e1[s] < x ? e1[s] : x;
            double eup = e2[s] < x ? e2[s] : x;
            double ee = x - emid;
            double t1 = mode == 1 ? twkbint(uwkb, twkb, nbins, ee) : thill(ee, bfis, wfis, twopi);
            w1[s] = (emid - elow[s]) * t1;
            w2[s] = (eup - emid) * t1;
        }
    }
    return 0;
}
