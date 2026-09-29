/* NATIVEX2 lever `ld`: the level-density set-up of one residual nucleus and its rhogrid, off the
 * autograd graph, for the analytical constant-temperature + Fermi-gas model (ldmodel 1) without
 * collective enhancement -- every nucleus with A <= 215 under TALYS's defaults.
 *
 *   nx2_ld_fermi_tables  densitymatch.f90:118-160  logrho, temprho (descending fill) and Nstart
 *   nx2_ld_match_root    matching.f90 + zbrak.f90 + rtbis.f90 + match.f90  the CTM matching roots
 *   nx2_ld_ncum          densitycum.f90:130-150  Ncum(index) from densitytot at level midpoints
 *   nx2_ld_rhogrid       exgrid.f90:241-285 with density.f90, densitytot.f90, gilcam.f90,
 *                        fermi.f90, ignatyuk.f90, spincut.f90, spindis.f90: rhogrid of a bin set
 *
 * The +, -, *, / are the Python/torch expressions' own, in their order, with contraction off, so
 * only libm's exp/log/pow can move a last bit against torch's; held to closeness
 * (tests/hf/test_nx2_ld.py). The float32 table index of match.f90 is evaluated in float32.
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md. */
#include <math.h>
#include <stdint.h>

/* no a*b+c fusion: clang honours the pragma; gcc with -std=c11 does not contract by default (and
 * warns about the pragma under -Wall) */
#ifdef __clang__
#pragma STDC FP_CONTRACT OFF
#endif

#include "ld.h"

/* logrho(0..nEx+1), temprho(0..nEx+1) of densitymatch.f90:118-160; returns Nstart. */
int64_t nx2_ld_fermi_tables(const double *p, int64_t nEx, double dEx, double *logrho,
                            double *temprho)
{
    double sc;
    double prev = 0.0;
    for (int64_t k = 0; k < nEx + 2; k++) {
        logrho[k] = 0.0;
        temprho[k] = 0.0;
    }
    /* raw(k) = dEx / (l(+1/2) - l(-1/2)) at k = nEx..1, filled in descending order */
    for (int64_t k = nEx; k >= 1; k--) {
        double col[3];
        for (int j = -1; j <= 1; j++) {
            double eex = dEx * ((double)k + 0.5 * j);
            double U = eex - p[P_PAIR];
            double ald = ignatyuk(p, eex);
            double val = log(fermi(p, ald, eex, p[P_PAIR], &sc));
            col[j + 1] = U > 0.0 ? val : 0.0;
        }
        logrho[k] = col[1];
        double raw = col[2] != col[0] ? dEx / (col[2] - col[0]) : 0.0;
        temprho[k] = raw <= 0.1 ? prev : raw;
        prev = temprho[k];
    }
    int64_t nstart = 1;
    for (int64_t k = nEx - 1; k >= 1; k--) {
        if (temprho[k] >= temprho[k + 1]) {
            nstart = k + 1;
            break;
        }
    }
    return nstart;
}

/* zbrak on [x1, x2] in nseg steps (at most 2 brackets), then rtbis to xacc in each: the roots go
 * to roots[0..nb-1]; returns nb. */
int64_t nx2_ld_match_root(const double *logrho, const double *temprho, int64_t n, double x1,
                          double x2, int64_t nseg, double E0save, double NLo, double NP, double EL,
                          double EP, double sentinel, double xacc, double *roots)
{
    double dx = (x2 - x1) / (double)nseg;
    double xprev = x1;
    double fprev = match1(logrho, temprho, n, xprev, E0save, NLo, NP, EL, EP, sentinel);
    int64_t nb = 0;
    double lo[2] = {0.0, 0.0}, hi[2] = {0.0, 0.0};
    for (int64_t k = 1; k <= nseg && nb < 2; k++) {
        double x = xprev + dx;
        double f = match1(logrho, temprho, n, x, E0save, NLo, NP, EL, EP, sentinel);
        if (f * fprev < 0.0) {
            lo[nb] = xprev;
            hi[nb] = x;
            nb++;
        }
        xprev = x;
        fprev = f;
    }
    for (int64_t b = 0; b < nb; b++) {
        double f = match1(logrho, temprho, n, lo[b], E0save, NLo, NP, EL, EP, sentinel);
        double root, d;
        if (f < 0.0) {
            root = lo[b];
            d = hi[b] - lo[b];
        } else {
            root = hi[b];
            d = lo[b] - hi[b];
        }
        for (int it = 0; it < 40; it++) {
            d = d * 0.5;
            double xmid = root + d;
            double fmid = match1(logrho, temprho, n, xmid, E0save, NLo, NP, EL, EP, sentinel);
            if (fmid <= 0.0)
                root = xmid;
            if (fabs(d) < xacc || fmid == 0.0)
                break;
        }
        roots[b] = root;
    }
    return nb;
}

/* Ncum(index) of densitycum.f90:130-150 from densitytot at the level midpoints of edis(0..). */
double nx2_ld_ncum(const double *p, const double *edis, int64_t NL, int64_t index)
{
    double ncum = 0.0;
    double sc;
    for (int64_t i = 1; i <= index; i++) {
        if (edis[i] == 0.0)
            continue;
        double mid = 0.5 * (edis[i] + edis[i - 1]);
        double d = densitytot(p, mid, &sc);
        ncum = ncum + d * (edis[i] - edis[i - 1]);
        if (i == NL)
            ncum = (double)NL;
    }
    return ncum;
}

/* exgrid.f90:241-285: out[k, j, 0..1] (row-major, (n, numj+1, 2), zero on entry) for the bins
 * k with sel[k] != 0, the level density integrated over the bin (core.grids.integrated_density)
 * from rho at its bottom, centre and top; zero above maxj[k]. Both parity columns get the same
 * value (the analytical model's 1/2 pardis). */
int nx2_ld_rhogrid(const double *p, const double *ex, const double *dex, const int64_t *maxj,
                   const uint8_t *sel, int64_t n, int64_t numj, double rodd, double *out)
{
    double r1[128], r2[128], r3[128];
    if (numj + 1 > 128)
        return -1;
    int64_t nj = numj + 1;
    for (int64_t k = 0; k < n; k++) {
        if (!sel[k])
            continue;
        double e = ex[k], dx = dex[k];
        rho_row(p, e - 0.5 * dx, rodd, numj, r1);
        rho_row(p, e, rodd, numj, r2);
        rho_row(p, e + 0.5 * dx, rodd, numj, r3);
        int64_t top = maxj[k];
        for (int64_t j = 0; j < nj && j <= top; j++) {
            double a2 = r2[j];
            double q1 = r1[j] * (1.0 + 1.0e-10);
            double q3 = r3[j] * (1.0 + 1.0e-10);
            double v = dx * a2;
            if (q1 > 0 && a2 > 0 && q3 > 0) {
                double l1 = log(q1), l2 = log(a2), l3 = log(q3);
                if (l2 != l1 && l2 != l3)
                    v = 0.5 * dx * ((q1 - a2) / (l1 - l2) + (a2 - q3) / (l2 - l3));
            }
            out[(k * nj + j) * 2] = v;
            out[(k * nj + j) * 2 + 1] = v;
        }
    }
    return 0;
}
