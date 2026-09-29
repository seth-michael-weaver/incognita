/* NATIVEX2 lever `emit`: the array work of binary.f90 for one ejectile's residual nucleus.
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * TALYS: binary.f90:1 (binary), spindis.f90:1 (spindis)
 * Python side: physics/hf/emission/emit_nx2.py; test: tests/hf/test_nx2_emit.py.
 *
 * Every cell sees the operations of emission/binary.py:binary in their order; the Wigner spin
 * distribution uses libm exp (torch's on the torch path), so it is held to closeness. */
#include <math.h>
#include <stdint.h>

/* One type of `binary` in place: the direct discrete addend into pop (rows 0..nl) and pex, then,
 * when `do_pe`, the pre-equilibrium addend on rows nl+1..nmax (sfactor written into both `sfac`
 * and the run-scoped `sfglobal`, spread with sfactor or the Wigner distribution times `pardis`).
 * pop (N, J, 2), pex, dd, jdis, parlev, spincut, ppx (N,), sfglobal and sfac (>= nmax+1, J, 2),
 * all contiguous; sfac holds a copy of sfglobal's rows 0..nmax on entry. Returns 0, or -1 for a
 * level spin index outside 0..J-1 (after Python's negative wrap), with nothing written. */
int nx2_emit_binary_type(int64_t N, int64_t J, int64_t nl, int64_t nmax, int64_t mj,
                         int64_t do_pe, int64_t pespinmodel, double popepsA, double pardis,
                         double *pop, double *pex, const double *dd, const double *jdis,
                         const int64_t *parlev, const double *spincut, const double *ppx,
                         double *sfglobal, double *sfac)
{
    for (int64_t lv = 0; lv <= nl; lv++) {
        if (dd[lv] == 0.0) continue;
        int64_t j = (int64_t)jdis[lv]; /* int(jdis): truncation */
        if (j < 0) j += J;
        if (j < 0 || j >= J) return -1;
    }
    /* direct discrete addend (binary.f90:194-216): one (J, parity) cell per level */
    for (int64_t lv = 0; lv <= nl; lv++) {
        double term = dd[lv];
        if (term != 0.0) {
            int64_t j = (int64_t)jdis[lv];
            if (j < 0) j += J;
            int64_t p = parlev[lv] == -1 ? 0 : 1;
            int64_t c = (lv * J + j) * 2 + p;
            pop[c] = pop[c] + term;
            pex[lv] = pex[lv] + term;
        } else {
            pex[lv] = pex[lv] + 0.0;
        }
    }
    if (!do_pe) return 0;
    /* pre-equilibrium addend (binary.f90:222-257) */
    int64_t jt = mj < J ? mj : J;
    for (int64_t r = nl + 1; r <= nmax; r++) {
        double pr = pex[r];
        int has = pr > popepsA;
        double den = pr > 0.0 ? pr : 1.0;
        double sigma22 = 2.0 * spincut[r];
        for (int64_t j = 0; j < jt; j++) {
            double rj = (double)j;
            double wig = (2.0 * rj + 1.0) / sigma22 * exp(-((rj + 0.5) * (rj + 0.5)) / sigma22)
                * pardis;
            for (int64_t p = 0; p < 2; p++) {
                int64_t c = (r * J + j) * 2 + p;
                double nw = has ? pop[c] / den : sfac[c];
                sfac[c] = nw;
                sfglobal[c] = nw;
                double spread = (pespinmodel == 1 && nw > 0.0) ? nw : wig;
                pop[c] = pop[c] + spread * ppx[r];
            }
        }
        pex[r] = pex[r] + ppx[r];
    }
    return 0;
}
