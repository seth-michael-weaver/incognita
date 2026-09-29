/* NATIVEX2: the photon strength function fstrength and the photon transmission rows built on it
 * (compound/psf_nx2.py), for many (Efs, Egamma) at once.
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * TALYS routines: fstrength.f90:1 (fstrength), locate.f90:1 (locate), densprepare.f90:1
 * (densprepare, the Tgam rows). The formulas are compound/psf_fast.py's `fstrength_np`, which
 * repeats gamma/strength.py's `fstrength_gp` operation by operation: standard Lorentzians, the
 * tabulated E1 (SMLO) with its temperature interpolation, the pygmy/scissors terms and the upbend.
 * Double precision with libm's pow/log10/exp/sqrt, so held to closeness, not to bits.
 *
 * Parameter block `par`, per (irad, l) at q = irad * L + l, 16 doubles:
 *   [0] ngr  [1..3] sgr, egr, ggr of i = 1  [4..6] of i = 2
 *   [7..9] tpr, epr, gpr of i = 1  [10..12] of i = 2  [13..15] upbend C, eta, F
 * Integers ip: [0] L (= gammax + 1)  [1] qrpa E1 table present  [2] flagupbend  [3] strengthM1
 *   [4] zix + nix  [5] n_tqrpa  [6] ie (table length - 1)  [7] NUMGAMQRPA  [8] n_t columns
 * Doubles dp: [0] S_k0  [1] delta  [2] alev  [3] beta2  [4] pi2h2c2
 */
#include <math.h>
#include <stdint.h>

#define PQ(irad, l) (16 * ((irad) * L + (l)))
#define LN10 2.302585092994045684

/* x**n for a small integer n, by products (libm pow was a third of the kernel) */
static double ipow(double x, int n) {
    double r = 1.0;
    for (int k = n < 0 ? -n : n; k > 0; k--)
        r *= x;
    return n < 0 ? 1.0 / r : r;
}

/* locate.f90 verbatim on xx(0:ie), which need not be monotone (the wtable stretch) */
static int64_t locate_f90(const double *xx, int64_t ie, double x) {
    int64_t jl = -1, ju = ie + 1;
    int ascend = xx[ie] >= xx[0];
    while (ju - jl > 1) {
        int64_t jm = (ju + jl) / 2;
        int64_t jc = jm < 0 ? 0 : (jm > ie ? ie : jm);
        int up = (x >= xx[jc]) == ascend;
        if (up)
            jl = jm;
        else
            ju = jm;
    }
    if (x == xx[0])
        return 0;
    if (x == xx[ie])
        return ie - 1;
    return jl;
}

/* psf_fast._interp with the table's log10 values given: log10-linear when both ends > 0 (the
 * exponent is returned through *lg for the temperature interpolation), else linear (*lg = NAN) */
static double interp_lg(double e, double eb, double ee, double gamb, double game, double lb,
                        double le, double *lg) {
    double frac = (e - eb) / (ee - eb);
    if (gamb > 0.0 && game > 0.0) {
        *lg = lb + frac * (le - lb);
        return exp(*lg * LN10);
    }
    *lg = NAN;
    return gamb + frac * (game - gamb);
}

/* psf_fast._table_strength for one point (the E1 table, irad = 1, l = 1); `lftab` is
 * log10(ftab) wherever ftab > 0 */
static double table_strength(const int64_t *ip, const double *dp, const double *etab,
                             const double *ftab, const double *lftab, const double *tq, double efs,
                             double eg) {
    int64_t n_t0 = ip[5], ie = ip[6], nq = ip[7], ncol = ip[8];
    double tnuc = 0.0, tb = 0.0, te = 0.0;
    int64_t n_t = 1;
    int itemp = 1;
    if (n_t0 > 1) {
        double e = (efs < 20.0 ? efs : 20.0) + dp[0] - dp[1] - eg;
        double alev = dp[2];
        tnuc = (e > 0.0 && alev > 0.0) ? sqrt(e / alev) : 0.0;
        int64_t cnt = 0;
        for (int64_t k = 0; k < n_t0; k++)
            cnt += tq[k] <= tnuc;
        n_t = cnt < n_t0 ? cnt : n_t0;
        tb = tq[(n_t > 1 ? n_t : 1) - 1];
        te = n_t < n_t0 ? tq[n_t < n_t0 - 1 ? n_t : n_t0 - 1] : tb;
        itemp = 2;
    }
    int inside = eg <= etab[nq];
    int64_t nen = nq - 1;
    if (inside) {
        nen = locate_f90(etab, ie, eg);
        if (nen < 0)
            nen = 0;
        if (nen > nq - 1)
            nen = nq - 1;
    }
    double fv[2] = {0.0, 0.0}, lg[2] = {NAN, NAN};
    for (int it = 1; it <= itemp; it++) {
        int64_t jt = it == 1 ? n_t : n_t + 1;
        if (jt > n_t0)
            jt = n_t0;
        double et = it == 1 ? tb : te;
        double eb = etab[nen], ee = etab[nen + 1];
        int64_t col = jt - 1;
        int64_t qb = (inside && !(eb <= et)) ? nen * ncol : nen * ncol + col;
        int64_t qe = (inside && !(ee <= et)) ? (nen + 1) * ncol : (nen + 1) * ncol + col;
        fv[it - 1] = interp_lg(eg, eb, ee, ftab[qb], ftab[qe], lftab[qb], lftab[qe], &lg[it - 1]);
    }
    double f2 = fv[itemp - 1];
    if (n_t0 > 1 && te - tb != 0.0) {
        double l0 = isnan(lg[0]) && fv[0] > 0.0 ? log10(fv[0]) : lg[0];
        double l1 = isnan(lg[1]) && fv[1] > 0.0 ? log10(fv[1]) : lg[1];
        double dummy;
        f2 = interp_lg(tnuc, tb, te, fv[0], fv[1], l0, l1, &dummy);
    }
    return f2;
}

/* psf_fast.fstrength_np for one point */
static double fstrength1(const int64_t *ip, const double *dp, const double *par, const double *etab,
                         const double *ftab, const double *lftab, const double *tq, double efs,
                         double eg, int irad, int l) {
    int64_t L = ip[0];
    const double *pq = par + PQ(irad, l);
    int qrpa = (int)ip[1];
    int flag_m1 = irad == 0 && l == 1, flag_e1 = irad == 1 && l == 1;
    double out = 0.0, egam2 = eg * eg;
    double k = dp[4] / (2 * l + 1.0);
    double pw = ipow(eg, 3 - 2 * l);
    int ngr = (int)pq[0];
    int slo = !qrpa || l != 1 || irad != 1;
    for (int i = 0; i < ngr; i++) {
        if (slo) {
            double sgr = pq[1 + 3 * i], egr = pq[2 + 3 * i], ggr = pq[3 + 3 * i];
            double d = egam2 - egr * egr;
            double denom = d * d + egam2 * ggr * ggr;
            if (eg > 0.001)
                out += k * sgr * (ggr * ggr * pw) / denom;
        }
        if (qrpa && flag_e1)
            out = table_strength(ip, dp, etab, ftab, lftab, tq, efs, eg);
    }
    for (int i = 0; i < 2; i++) {
        double tpr = pq[7 + 3 * i];
        if (tpr <= 0.0)
            continue;
        double epr = pq[8 + 3 * i], gpr = pq[9 + 3 * i];
        double d = egam2 - epr * epr;
        double denom = d * d + egam2 * gpr * gpr;
        if (eg > 0.001)
            out += k * tpr * (gpr * gpr * pw) / denom;
    }
    if (ip[2]) {
        double upc = pq[13], upe = pq[14], upf = pq[15];
        if ((ip[3] == 8 || ip[3] == 10) && flag_m1 && ip[4] >= 105)
            upf = upf * 0.0;
        if (flag_e1) {
            double e = (efs < 20.0 ? efs : 20.0) + dp[0];
            if (e > 1.0)
                out += upc * e / (1.0 + exp(eg - upe));
        }
        if (irad == 0)
            out += upc * exp(-upe * eg) * exp(-upf * fabs(dp[3]));
    }
    return out;
}

/* Tgam at `np` points: out[p * L * 2 + l * 2 + irad] = twopi eg^(2l+1) fn1 f(efs, eg, irad, l)
 * for l = 1..L-1 (l = 0 stays as given). */
int nx2_psf_points(const int64_t *ip, const double *dp, const double *par, const double *etab,
                   const double *ftab, const double *lftab, const double *tq, int64_t np,
                   const double *efs, const double *eg, double twopi_fn1, double *out) {
    int64_t L = ip[0];
    for (int64_t p = 0; p < np; p++)
        for (int l = 1; l < L; l++) {
            double fac = twopi_fn1 * ipow(eg[p], 2 * l + 1);
            for (int irad = 0; irad < 2; irad++)
                out[p * L * 2 + l * 2 + irad] =
                    fac * fstrength1(ip, dp, par, etab, ftab, lftab, tq, efs[p], eg[p], irad, l);
        }
    return 0;
}

/* widths_native._photon: tg[b, k, l, irad] for mother bins b (Ex = exinc[b], Efs = Ex - S_n) to
 * daughter rows k <= nexmax0[b] with Egamma = Ex - ex0[k] > 0; zero elsewhere. */
int nx2_psf_photon(const int64_t *ip, const double *dp, const double *par, const double *etab,
                   const double *ftab, const double *lftab, const double *tq, int64_t m,
                   const double *exinc, int64_t n, const double *ex0, const int64_t *nexmax0,
                   double s_n, double twopi_fn1, double *tg) {
    int64_t L = ip[0];
    for (int64_t b = 0; b < m; b++) {
        double efs = exinc[b] - s_n;
        for (int64_t kk = 0; kk < n; kk++) {
            double *row = tg + ((b * n + kk) * L) * 2;
            for (int64_t q = 0; q < 2 * L; q++)
                row[q] = 0.0;
            if (kk > nexmax0[b])
                continue;
            double eg = exinc[b] - ex0[kk];
            if (!(eg > 0.0))
                continue;
            for (int l = 1; l < L; l++) {
                double fac = twopi_fn1 * ipow(eg, 2 * l + 1);
                for (int irad = 0; irad < 2; irad++)
                    row[l * 2 + irad] =
                        fac * fstrength1(ip, dp, par, etab, ftab, lftab, tq, efs, eg, irad, l);
            }
        }
    }
    return 0;
}
