/* CENGFIS (ROUTE100 WP7): fission barrier level densities, the bin-ladder transmission and the
 * primary compound nucleus's barrier sums in C, off the autograd graph.
 *
 *   ceng_fis_log_table   the logarithms of a density table (nx2_ld2.c's log_table), taken once per
 *                        table by the caller instead of once per grid
 *   ceng_fis_grid        densprepare.f90:399-441 and t1barrier.f90:151-168 in one pass for one
 *                        barrier: the `eintfis` grid, the tabulated density at each point
 *                        (density.f90's table branch) and the two slopes of the logarithmic
 *                        integration of every triple, without storing `rhofis`; a parity column
 *                        equal to the other in the table is copied, not recomputed
 *   ceng_fis_weights     nx2_fis2_ladder_weights with the WKB table index walked down the triples
 *                        (the energy above each triple's centre falls monotonically) instead of
 *                        searched
 *   ceng_fis_bins        tfission.f90's hump combination of up to three barriers at every energy of
 *                        a ladder, then compound.f90:120-147's logarithmic integration of the
 *                        (down, centre, up) triple over each mother bin
 *   ceng_fis_combine     the hump combination at one energy (the primary compound nucleus)
 *
 * The +, -, *, / are the numpy/torch expressions' own (`fission.fis2_nx2`, `fission_batch_ladder`,
 * `transmission.fission_transmission`) in their order, with contraction off. The slopes are
 * bit-identical to nx2_ld2_table_grid + nx2_fis2_coef, the weights to nx2_fis2_ladder_weights;
 * libm's log against numpy's in the bin integration and matrix-product sums may move last bits,
 * so the kernels are held to closeness (tests/hf/test_cengfis.py).
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
#define TRANSEPS 1.0e-8 /* input_numerics.f90:80 */

void ceng_fis_log_table(const double *ldtable, int64_t m, double *lg)
{
    for (int64_t k = 0; k < m; k++)
        lg[k] = ldtable[k] > 1.0 ? log(ldtable[k]) : 0.0;
}

/* nx2_ld2.c's table_index */
static int64_t table_index(const double *edens, int64_t nendens, double edensmax, double x)
{
    int64_t idx;
    if (x == edens[0]) {
        idx = 0;
    } else if (x == edens[nendens]) {
        idx = nendens - 1;
    } else {
        int64_t lo = 0, hi = nendens + 1;
        while (lo < hi) {
            int64_t mid = lo + (hi - lo) / 2;
            if (edens[mid] <= x)
                lo = mid + 1;
            else
                hi = mid;
        }
        idx = lo - 1;
    }
    if (!(x <= edensmax))
        idx = nendens - 1;
    if (idx < 0)
        idx = 0;
    if (idx > nendens - 1)
        idx = nendens - 1;
    return idx;
}

/* one grid point: val[c] = the shifted density the triple reads (edge: rho (1 + eps) + eps,
 * centre: rho + eps) and lg[c] = log(val[c]), c over (J index jidx[b], parity) row-major. The
 * values are the table branch of density.f90 as nx2_ld2_table_grid computes them; the log() is
 * taken once per distinct value where it can be seen to repeat without comparing floats of
 * different origin: a spin whose table index repeats the previous one's, the second parity when
 * both table entries equal the first's, and the 1e-30 floor (floorlg: log of the floored edge and
 * centre values). */
static void point(const double *edens, int64_t nendens, double edensmax, const double *ldtable,
                  const double *lgtable, int64_t nj, double ct, double pt, double eex,
                  const int64_t *jidx, int64_t nJ, int edge, const double *floorv,
                  const double *floorlg, double *val, double *lg)
{
    double eshift = eex - pt;
    int valid = (eex >= 0.0) && (eshift > 0.0);
    double x = valid ? eshift : 1.0;
    int64_t i = table_index(edens, nendens, edensmax, x);
    double eb = edens[i], ee = edens[i + 1];
    double frac = (x - eb) / (ee - eb);
    double expo = ct * sqrt(valid ? eshift : 0.0);
    if (expo > 80.0)
        expo = 80.0;
    double enh = exp(expo);
    for (int64_t b = 0; b < nJ; b++) {
        if (b > 0 && jidx[b] == jidx[b - 1]) { /* the spin index capped at numJ - 1 */
            for (int64_t c = 0; c < 2; c++) {
                val[b * 2 + c] = val[(b - 1) * 2 + c];
                lg[b * 2 + c] = lg[(b - 1) * 2 + c];
            }
            continue;
        }
        for (int64_t c = 0; c < 2; c++) {
            int64_t kb = (i * nj + jidx[b]) * 2 + c;
            int64_t ke = ((i + 1) * nj + jidx[b]) * 2 + c;
            int64_t o = b * 2 + c;
            double ldb = ldtable[kb], lde = ldtable[ke];
            if (c == 1 && ldb == ldtable[kb - 1] && lde == ldtable[ke - 1]) {
                val[o] = val[o - 1];
                lg[o] = lg[o - 1];
                continue;
            }
            double t;
            if (ldb > 1.0 && lde > 1.0) {
                double lb = lgtable[kb], le = lgtable[ke];
                t = exp(lb + frac * (le - lb));
            } else {
                t = ldb + frac * (lde - ldb);
            }
            double rho = valid ? enh * t : 0.0;
            if (rho < 1.0e-30) {
                val[o] = floorv[edge];
                lg[o] = floorlg[edge];
                continue;
            }
            double v = edge ? rho * (1.0 + EPS_FIS) + EPS_FIS : rho + EPS_FIS;
            val[o] = v;
            lg[o] = log(v);
        }
    }
}

/* One barrier's grid (fis2_nx2.level_densities) and triple slopes (nx2_fis2_coef).
 * nJ = maxj + 1, nj2 = 2 nJ. Outputs elow/emid/eup (smax) and A, B (smax, nj2). Returns S, the
 * number of triples (0 when the grid has fewer than 3 points), or -1 when smax is too small.
 * exfis <= 0: TALYS keeps nbintfis = numbinfis/2 over an all-zero grid, whose triples add exactly
 * zero; one zero triple stands for them (t1barrier still counts the energy as integrated). */
int64_t ceng_fis_grid(const double *edens, int64_t nendens, double edensmax,
                      const double *ldtable, const double *lgtable, int64_t nj, double ct,
                      double pt, double elowest, double exfis_top, const int64_t *jidx,
                      int64_t nJ, double dexmin, int64_t numbinfis, double *elow, double *emid,
                      double *eup, double *A, double *B, int64_t smax)
{
    int64_t nj2 = 2 * nJ;
    double exfis = exfis_top - elowest;
    int64_t nbin = numbinfis / 2;
    if (exfis <= 0.0) {
        if (nbin < 2)
            return 0;
        if (smax < 1)
            return -1;
        elow[0] = emid[0] = eup[0] = 0.0;
        memset(A, 0, (size_t)nj2 * sizeof(double));
        memset(B, 0, (size_t)nj2 * sizeof(double));
        return 1;
    }
    double dex = exfis / (double)nbin;
    if (dex < dexmin) {
        nbin = (int64_t)(exfis / dexmin);
        if (nbin < 1)
            nbin = 1;
        dex = exfis / (double)nbin;
    }
    int64_t S = nbin - 1; /* triples i = 1, 3, ..., 2 nbin - 3 */
    if (S <= 0)
        return 0;
    if (S > smax)
        return -1;
    double *buf = (double *)malloc((size_t)(6 * nj2) * sizeof(double));
    if (buf == NULL)
        return -1;
    double *v1 = buf, *l1 = buf + nj2, *v2 = buf + 2 * nj2, *l2 = buf + 3 * nj2;
    double *v3 = buf + 4 * nj2, *l3 = buf + 5 * nj2;
    double half = 0.5 * dex;
    double floorv[2] = {1.0e-30 + EPS_FIS, 1.0e-30 * (1.0 + EPS_FIS) + EPS_FIS};
    double floorlg[2] = {log(floorv[0]), log(floorv[1])};
    /* e[2k+1] = elowest + dex k, e[2k+2] = e[2k+1] + dex/2, e[2 nbin] = exfis + elowest */
    double e_edge = elowest + dex * 0.0;
    point(edens, nendens, edensmax, ldtable, lgtable, nj, ct, pt, e_edge, jidx, nJ, 1, floorv, floorlg, v1, l1);
    for (int64_t s = 0; s < S; s++) {
        double e1 = elowest + dex * (double)s;
        double e2 = e1 + half;
        double e3 = elowest + dex * (double)(s + 1); /* e[2 nbin], moved to the top, is never read */
        elow[s] = e1;
        emid[s] = e2;
        eup[s] = e3;
        point(edens, nendens, edensmax, ldtable, lgtable, nj, ct, pt, e2, jidx, nJ, 0, floorv, floorlg, v2, l2);
        point(edens, nendens, edensmax, ldtable, lgtable, nj, ct, pt, e3, jidx, nJ, 1, floorv, floorlg, v3, l3);
        double *a = A + s * nj2, *bb = B + s * nj2;
        for (int64_t c = 0; c < nj2; c++) {
            if (l2[c] != l1[c] && l2[c] != l3[c]) {
                a[c] = (v1[c] - v2[c]) / (l1[c] - l2[c]);
                bb[c] = (v2[c] - v3[c]) / (l2[c] - l3[c]);
            } else {
                a[c] = v2[c];
                bb[c] = v2[c];
            }
        }
        double *t = v1;
        v1 = v3;
        v3 = t;
        t = l1;
        l1 = l3;
        l3 = t;
    }
    free(buf);
    return S;
}

/* nx2_fis2.c's twkbint at WKB index n */
static double twkbint_at(const double *u, const double *tab, int64_t nbins, int64_t n, double e)
{
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

static double thill(double e, double b, double w, double twopi)
{
    double expo = twopi * (e - b) / w;
    if (!(expo > -80.0))
        return 0.0;
    return 1.0 / (1.0 + exp(-expo));
}

/* W1 = dE1 T keep, W2 = dE2 T keep (n, S) as nx2_fis2_ladder_weights */
int ceng_fis_weights(const double *elow, const double *e1, const double *e2, int64_t S,
                     double fecont, const double *eex, int64_t n, int64_t mode, double bfis,
                     double wfis, double twopi, const double *uwkb, const double *twkb,
                     int64_t nbins, double *W1, double *W2)
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
        int64_t m = nbins; /* largest index with u[m] <= ee, walked down as ee falls */
        for (int64_t s = 0; s < S; s++) {
            if (!(elow[s] <= x))
                break; /* elow ascends */
            double emid = e1[s] < x ? e1[s] : x;
            double eup = e2[s] < x ? e2[s] : x;
            double ee = x - emid;
            double t1;
            if (mode == 1) {
                while (m >= 0 && !(uwkb[m] <= ee))
                    m--;
                int64_t j;
                if (ee == uwkb[0])
                    j = 0;
                else if (ee == uwkb[nbins])
                    j = nbins - 1;
                else
                    j = m;
                if (j < 0)
                    j = 0;
                if (j > nbins - 1)
                    j = nbins - 1;
                t1 = twkbint_at(uwkb, twkb, nbins, j, ee);
            } else {
                t1 = thill(ee, bfis, wfis, twopi);
            }
            w1[s] = (emid - elow[s]) * t1;
            w2[s] = (eup - emid) * t1;
        }
    }
    return 0;
}

/* tfission.f90's combination of nb barrier transmissions t[b] (n, nj2) into tf (n, nj2), times
 * fnorm, as fission_batch_ladder.ladder_transmission */
static void combine(int64_t nb, const double *t1, const double *t2, const double *t3, int64_t n,
                    double fnorm, double *tf)
{
    for (int64_t k = 0; k < n; k++) {
        double a = t1[k], v;
        if (nb == 1) {
            v = a;
        } else if (nb == 2) {
            double b = t2[k];
            int live = (a >= TRANSEPS) && (b >= TRANSEPS);
            double denom = live ? a + b : 1.0;
            v = live ? a * b / denom : 0.0;
        } else {
            double b = t2[k], c = t3[k];
            int live = (a >= TRANSEPS) && (b >= TRANSEPS) && (c >= TRANSEPS);
            double d12 = live ? a + b : 1.0;
            double tf12 = a * b / d12;
            double tsum = tf12 + c;
            v = live ? tf12 * c / (live ? tsum : 1.0) : 0.0;
        }
        tf[k] = v * fnorm;
    }
}

int ceng_fis_combine(int64_t nb, const double *t1, const double *t2, const double *t3, int64_t n,
                     double fnorm, double *tf)
{
    if (nb < 1 || nb > 3)
        return -1;
    combine(nb, t1, t2, t3, n, fnorm, tf);
    return 0;
}

/* The ladder's barrier transmissions t[b] (3m, nj2) at (lo, ex, hi) of m mother bins, combined,
 * floored at transeps and integrated over each bin into fis (m, nj2), as
 * fission_batch_ladder.ladder_bin_widths. */
int ceng_fis_bins(int64_t nb, const double *t1, const double *t2, const double *t3, int64_t m,
                  int64_t nj2, double fnorm, const double *ex, const double *dex, double exmax,
                  double *fis)
{
    if (nb < 1 || nb > 3)
        return -1;
    int64_t n = 3 * m * nj2;
    double *tf = (double *)malloc((size_t)n * sizeof(double));
    if (tf == NULL)
        return -1;
    combine(nb, t1, t2, t3, n, fnorm, tf);
    for (int64_t b = 0; b < m; b++) {
        double lo = ex[b] - 0.5 * dex[b];
        double exmin = lo > 0.0 ? lo : 0.0;
        double hi = ex[b] + 0.5 * dex[b];
        double explus = exmax < hi ? exmax : hi;
        double de1 = ex[b] - exmin, de2 = explus - ex[b];
        const double *d = tf + b * nj2, *c = tf + (m + b) * nj2, *u = tf + (2 * m + b) * nj2;
        double *out = fis + b * nj2;
        for (int64_t j = 0; j < nj2; j++) {
            double tfd = d[j] > TRANSEPS ? d[j] : TRANSEPS;
            double tfc = c[j] > TRANSEPS ? c[j] : TRANSEPS;
            double tfu = u[j] > TRANSEPS ? u[j] : TRANSEPS;
            double logd = log(tfc) - log(tfd);
            double logu = log(tfu) - log(tfc);
            double c1 = logd == 0 ? tfc * de1 : (tfc - tfd) / logd * de1;
            double c2 = logu == 0 ? tfc * de2 : (tfu - tfc) / logu * de2;
            double v = (c1 + c2) / (explus - exmin);
            out[j] = ((explus <= exmin) || (v <= 10.0 * TRANSEPS)) ? 0.0 : v;
        }
    }
    free(tf);
    return 0;
}
