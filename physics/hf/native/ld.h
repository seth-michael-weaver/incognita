/* CENGLD (ROUTE100 WP6): the level-density helpers shared by `nx2_ld.c` (NATIVEX2's kernels,
 * moved here unchanged) and `ld.c` (CENGLD's): the LDNucleus scalar layout, ignatyuk, spincut,
 * fermi, densitytot (ldmodel 1 without collective enhancement), match.f90's condition and rho(J)
 * at one energy. `static inline`: every translation unit compiles its own copy, and with
 * contraction off the arithmetic is the same in each.
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md. */
#ifndef HF_NATIVE_LD_H
#define HF_NATIVE_LD_H
#include <math.h>
#include <stdint.h>

#ifdef __clang__
#pragma STDC FP_CONTRACT OFF
#endif

/* The scalars of one LDNucleus the kernels read (density/ld_nx2.py `_par` fills them). */
enum {
    P_DELTA = 0,  /* delta_mev[0]: ignatyuk's and spincut's U, densitytot's fermi P */
    P_ALIMIT,     /* alimit */
    P_GAMMALD,    /* gammald */
    P_DW,         /* deltaW_mev[0] */
    P_COLLDAMP,   /* flagcolldamp (0/1) */
    P_ALDLOW,     /* A / 13 */
    P_UFERMI,     /* Ufermi_mev[0] */
    P_CFERMI,     /* cfermi_mev[0] */
    P_SCUTCONST,  /* spincut's energy-independent scalars (parameters._sc_floats) */
    P_EM,
    P_ED,
    P_SDISC,
    P_S2M,
    P_COLLD_ON,
    P_COLLD,
    P_MODEL1,     /* spincutmodel == 1 */
    P_T,          /* T_mev[0], E0_mev[0], Exmatch_mev[0] */
    P_E0,
    P_EXMATCH,
    P_CTABLE,     /* ctable[0], ptable_mev[0] */
    P_PTABLE,
    P_PAIR,       /* pair_mev: the P of the Fermi-gas tables */
    P_N
};

/* ignatyuk.f90, as parameters._ignatyuk_f */
static inline double ignatyuk(const double *p, double eex)
{
    double U = eex - p[P_DELTA];
    double damp;
    if (U > 0.0) {
        double expo = p[P_GAMMALD] * U;
        double fU = fabs(expo) <= 80.0 ? 1.0 - exp(-expo) : 1.0;
        damp = 1.0 + fU * p[P_DW] / U;
    } else {
        damp = 1.0 + p[P_DW] * p[P_GAMMALD];
    }
    double aldlim = p[P_ALIMIT];
    if (p[P_COLLDAMP] != 0.0) {
        double e = (U - p[P_UFERMI]) / p[P_CFERMI];
        double q = e > -80.0 ? 1.0 / (1.0 + exp(-(e > -80.0 ? e : -80.0))) : 0.0;
        aldlim = p[P_ALDLOW] * q + aldlim * (1.0 - q);
    }
    double v = aldlim * damp;
    return v < 1.0 ? 1.0 : v;
}

/* spincut.f90 (ibar 0, ipop 0), as parameters._spincut_fast */
static inline double spincut(const double *p, double ald, double eex)
{
    double Em = p[P_EM], Ed = p[P_ED], sdisc = p[P_SDISC];
    double below;
    if (Em != Ed && eex > Ed)
        below = sdisc + (eex - Ed) / (Em - Ed) * (p[P_S2M] - sdisc);
    else
        below = sdisc;
    double U = eex - p[P_DELTA];
    double above;
    if (U > 0.0)
        above = p[P_MODEL1] != 0.0 ? p[P_SCUTCONST] * sqrt(ald * U)
                                   : p[P_SCUTCONST] * sqrt(U / ald);
    else
        above = sdisc;
    double sc = eex <= Em ? below : above;
    if (p[P_COLLD_ON] != 0.0)
        sc = p[P_COLLD] * sc;
    return sc < sdisc ? sdisc : sc;
}

/* fermi.f90, with its spin cutoff returned through *sc */
static inline double fermi(const double *p, double ald, double eex, double P, double *sc)
{
    double U = eex - P;
    *sc = spincut(p, ald, eex);
    if (!(U > 0.0))
        return 1.0;
    double factor = 2.0 * sqrt(ald * U);
    if (factor > 700.0)
        factor = 700.0;
    double sigma = sqrt(*sc);
    double denom = 12.0 * sqrt(2.0) * sigma * pow(ald, 0.25) * pow(U, 1.25);
    return exp(factor) / denom;
}

/* densitytot.f90 for ldmodel 1 without collective enhancement (Kcoll = 1), with the spin cutoff
 * at (ignatyuk(eex), eex) returned through *sc */
static inline double densitytot(const double *p, double eex, double *sc)
{
    double eshift = eex - p[P_PTABLE];
    int valid = (eex >= 0.0) && (eshift > 0.0);
    double ald = ignatyuk(p, eex);
    double T = p[P_T];
    double Ts = T != 0.0 ? T : 1.0;
    double dens;
    if (eex > p[P_EXMATCH]) {
        dens = fermi(p, ald, eex, p[P_DELTA], sc);
    } else {
        double a = (eex - p[P_E0]) / Ts;
        if (a > 300.0)
            a = 300.0;
        dens = exp(a) / Ts;
        *sc = spincut(p, ald, eex);
    }
    double expo = p[P_CTABLE] * sqrt(valid ? eshift : 0.0);
    if (expo > 80.0)
        expo = 80.0;
    double out = valid ? exp(expo) * dens : 0.0;
    return out < 1.0e-30 ? 1.0e-30 : out;
}

/* match.f90's condition at one energy, as matching_fast.match_vec */
static inline double match1(const double *logrho, const double *temprho, int64_t n, double x,
                     double E0save, double NLo, double NP, double EL, double EP, double sentinel)
{
    int64_t i = (int64_t)((float)x / (float)0.1f);
    if (i < 1)
        i = 1;
    if (i > n - 2)
        i = n - 2;
    double dEx = (double)0.1f;
    double x1 = (double)i * dEx;
    double x2 = (double)(i + 1) * dEx;
    double fac = (x - x1) / (x2 - x1);
    double t1 = temprho[i], t2 = temprho[i + 1];
    double temp = t1 + fac * (t2 - t1);
    if (!(temp > 0.0))
        return 0.0;
    double l1 = logrho[i], l2 = logrho[i + 1];
    double rhof = exp(l1 + fac * (l2 - l1));
    if (E0save == sentinel) {
        double factor1 = exp(-x / temp);
        double factor2 = exp(EP / temp);
        if (EL != 0.0)
            factor2 = factor2 - exp(EL / temp);
        double term = temp * rhof * factor1 * factor2;
        if (term > 1.0e30)
            term = 1.0e30;
        return term + NLo - NP;
    }
    return x - temp * log(temp * rhof) - E0save;
}

/* rho(J) for J = rodd + 0..numj at one energy (density.f90 for the analytical model) */
static inline void rho_row(const double *p, double eex, double rodd, int64_t numj, double *r)
{
    double sc;
    double dt = densitytot(p, eex, &sc);
    double sigma22 = 2.0 * sc;
    for (int64_t j = 0; j <= numj; j++) {
        double J = (double)j + rodd;
        double h = J + 0.5;
        double sd = (2.0 * J + 1.0) / sigma22 * exp(-(h * h) / sigma22);
        double v = eex < 0.0 ? 0.0 : dt * 0.5 * sd;
        r[j] = v < 1.0e-30 ? 1.0e-30 : v;
    }
}

#endif
