/* NATIVEX2 lever `ld2`: the tabulated level density of density.f90 (ldmodel >= 4 and every
 * fission-barrier table), off the autograd graph.
 *
 *   nx2_ld2_table_density   density.f90's table branch: rho(Ex, J, parity) from ldtable
 *                           (densitytable.f90) by locate.f90 on edens and log-linear
 *                           interpolation, times exp(ctable sqrt(Ex - ptable)), per (Ex, J) pair
 *   nx2_ld2_table_grid      the same on the outer product of an energy column and a spin row for
 *                           both parities, the two logs of the table taken once per call
 *                           (densprepare.f90:399-441, the fission-barrier grid)
 *   nx2_ld2_table_rhogrid   exgrid.f90:241-285 for a tabulated nucleus: rho at every bin's
 *                           bottom, centre and top for both parities, integrated over the bin
 *
 * The +, -, *, / are the torch expressions' own (`density.models._table_interp`, `density`,
 * `core.grids.integrated_density`), in their order, with contraction off; only libm's exp/log may
 * move a last bit against torch's, so the kernels are held to closeness (tests/hf/test_nx2_ld2.py).
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md. */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>

#ifdef __clang__
#pragma STDC FP_CONTRACT OFF
#endif

/* locate.f90 on edens(0..nendens) as core.numerics.locate(xx, x, 0, nendens), then
 * _table_interp's Edensmax and [0, nendens-1] clamps */
static int64_t table_index(const double *edens, int64_t nendens, double edensmax, double x)
{
    int64_t idx;
    if (x == edens[0]) {
        idx = 0;
    } else if (x == edens[nendens]) {
        idx = nendens - 1;
    } else {
        int64_t cnt = 0; /* entries of edens(0..nendens) <= x (the table ascends) */
        int64_t lo = 0, hi = nendens + 1;
        while (lo < hi) {
            int64_t mid = lo + (hi - lo) / 2;
            if (edens[mid] <= x)
                lo = mid + 1;
            else
                hi = mid;
        }
        cnt = lo;
        idx = cnt - 1;
    }
    if (!(x <= edensmax))
        idx = nendens - 1;
    if (idx < 0)
        idx = 0;
    if (idx > nendens - 1)
        idx = nendens - 1;
    return idx;
}

/* one energy: the index, frac and the exp(ctable sqrt(eshift)) factor; returns validity */
static int energy_setup(const double *edens, int64_t nendens, double edensmax, double ct,
                        double pt, double eex, int64_t *idx, double *frac, double *enh)
{
    double eshift = eex - pt;
    int valid = (eex >= 0.0) && (eshift > 0.0);
    double x = valid ? eshift : 1.0;
    int64_t i = table_index(edens, nendens, edensmax, x);
    double eb = edens[i], ee = edens[i + 1];
    *idx = i;
    *frac = (x - eb) / (ee - eb);
    double expo = ct * sqrt(valid ? eshift : 0.0);
    if (expo > 80.0)
        expo = 80.0;
    *enh = exp(expo);
    return valid;
}

static double interp(double ldb, double lde, double frac)
{
    if (ldb > 1.0 && lde > 1.0) {
        double lb = log(ldb), le = log(lde);
        return exp(lb + frac * (le - lb));
    }
    return ldb + frac * (lde - ldb);
}

static double finish(int valid, double enh, double ldtab)
{
    double out = valid ? enh * ldtab : 0.0;
    return out < 1.0e-30 ? 1.0e-30 : out;
}

/* out[k] = density(eex[k], J with table spin index jj[k], parity column pi) for k < n;
 * ldtable is (nendens+1, nj, 2) row-major. */
int nx2_ld2_table_density(const double *edens, int64_t nendens, double edensmax,
                          const double *ldtable, int64_t nj, double ct, double pt,
                          const double *eex, const int64_t *jj, int64_t n, int64_t pi, double *out)
{
    for (int64_t k = 0; k < n; k++) {
        int64_t i;
        double frac, enh;
        int valid = energy_setup(edens, nendens, edensmax, ct, pt, eex[k], &i, &frac, &enh);
        int64_t j = jj[k];
        if (j < 0 || j >= nj)
            return -1;
        double ldb = ldtable[(i * nj + j) * 2 + pi];
        double lde = ldtable[((i + 1) * nj + j) * 2 + pi];
        out[k] = finish(valid, enh, interp(ldb, lde, frac));
    }
    return 0;
}

/* log of every entry of ldtable(0..nendens, nj, 2); only entries > 1 are ever read back */
static double *log_table(const double *ldtable, int64_t nendens, int64_t nj)
{
    int64_t m = (nendens + 1) * nj * 2;
    double *lg = (double *)malloc((size_t)m * sizeof(double));
    if (lg == NULL)
        return NULL;
    for (int64_t k = 0; k < m; k++)
        lg[k] = ldtable[k] > 1.0 ? log(ldtable[k]) : 0.0;
    return lg;
}

/* interp with the two logs looked up instead of taken */
static double interp_lg(double ldb, double lde, double lb, double le, double frac)
{
    if (ldb > 1.0 && lde > 1.0)
        return exp(lb + frac * (le - lb));
    return ldb + frac * (lde - ldb);
}

/* out (ne, njout, np) row-major = density(e[a], J with table spin index jj[b], parity column
 * pcol[c]) for every (a, b, c): the outer product `density(ld, e[:, None], J[None, :], parity)`
 * for up to two parities, with the energy work done once per energy. */
int nx2_ld2_table_grid(const double *edens, int64_t nendens, double edensmax,
                       const double *ldtable, int64_t nj, double ct, double pt, const double *e,
                       int64_t ne, const int64_t *jj, int64_t njout, const int64_t *pcol,
                       int64_t np, double *out)
{
    for (int64_t b = 0; b < njout; b++)
        if (jj[b] < 0 || jj[b] >= nj)
            return -1;
    for (int64_t c = 0; c < np; c++)
        if (pcol[c] < 0 || pcol[c] > 1)
            return -1;
    double *lg = log_table(ldtable, nendens, nj);
    if (lg == NULL)
        return -2;
    for (int64_t a = 0; a < ne; a++) {
        int64_t i;
        double frac, enh;
        int valid = energy_setup(edens, nendens, edensmax, ct, pt, e[a], &i, &frac, &enh);
        for (int64_t b = 0; b < njout; b++) {
            for (int64_t c = 0; c < np; c++) {
                int64_t kb = (i * nj + jj[b]) * 2 + pcol[c];
                int64_t ke = ((i + 1) * nj + jj[b]) * 2 + pcol[c];
                out[(a * njout + b) * np + c] =
                    finish(valid, enh, interp_lg(ldtable[kb], ldtable[ke], lg[kb], lg[ke], frac));
            }
        }
    }
    free(lg);
    return 0;
}

/* rho(J) for J = j + rodd, j = 0..numj, at one energy, both parities: r[j*2 + p]. density.f90's
 * table spin index min(int(J), jcap) is min(j, jcap) for rodd in {0, 1/2}. */
static void rho_rows(const double *edens, int64_t nendens, double edensmax, const double *ldtable,
                     const double *lg, int64_t nj, int64_t jcap, double ct, double pt, double eex,
                     int64_t numj, double *r)
{
    int64_t i;
    double frac, enh;
    int valid = energy_setup(edens, nendens, edensmax, ct, pt, eex, &i, &frac, &enh);
    for (int64_t j = 0; j <= numj; j++) {
        int64_t jt = j < jcap ? j : jcap;
        for (int p = 0; p < 2; p++) {
            int64_t kb = (i * nj + jt) * 2 + p, ke = ((i + 1) * nj + jt) * 2 + p;
            r[j * 2 + p] =
                finish(valid, enh, interp_lg(ldtable[kb], ldtable[ke], lg[kb], lg[ke], frac));
        }
    }
}

/* exgrid.f90:241-285 for a tabulated nucleus: out (n, numj+1, 2) row-major, zero on entry, filled
 * for the bins with sel[k] != 0 up to maxj[k]. */
int nx2_ld2_table_rhogrid(const double *edens, int64_t nendens, double edensmax,
                          const double *ldtable, int64_t nj, int64_t jcap, double ct, double pt,
                          const double *ex, const double *dex, const int64_t *maxj,
                          const uint8_t *sel, int64_t n, int64_t numj, double *out)
{
    double r1[256], r2[256], r3[256];
    if (numj + 1 > 128 || jcap < 0 || jcap >= nj)
        return -1;
    double *lg = log_table(ldtable, nendens, nj);
    if (lg == NULL)
        return -2;
    int64_t nout = numj + 1;
    for (int64_t k = 0; k < n; k++) {
        if (!sel[k])
            continue;
        double e = ex[k], dx = dex[k];
        rho_rows(edens, nendens, edensmax, ldtable, lg, nj, jcap, ct, pt, e - 0.5 * dx, numj, r1);
        rho_rows(edens, nendens, edensmax, ldtable, lg, nj, jcap, ct, pt, e, numj, r2);
        rho_rows(edens, nendens, edensmax, ldtable, lg, nj, jcap, ct, pt, e + 0.5 * dx, numj, r3);
        int64_t top = maxj[k];
        for (int64_t j = 0; j < nout && j <= top; j++) {
            for (int p = 0; p < 2; p++) {
                double a2 = r2[j * 2 + p];
                double q1 = r1[j * 2 + p] * (1.0 + 1.0e-10);
                double q3 = r3[j * 2 + p] * (1.0 + 1.0e-10);
                double v = dx * a2;
                if (q1 > 0 && a2 > 0 && q3 > 0) {
                    double l1 = log(q1), l2 = log(a2), l3 = log(q3);
                    if (l2 != l1 && l2 != l3)
                        v = 0.5 * dx * ((q1 - a2) / (l1 - l2) + (a2 - q3) / (l2 - l3));
                }
                out[(k * nout + j) * 2 + p] = v;
            }
        }
    }
    free(lg);
    return 0;
}
