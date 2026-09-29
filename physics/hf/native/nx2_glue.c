/* NATIVEX2 lever `glue`: densprepare's Lagrange interpolation of the emission-grid transmission
 * coefficients onto a residual's rows.
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * TALYS: densprepare.f90:1 (densprepare)
 * Python side: physics/hf/compound/prepare.py (densprepare); test: tests/hf/test_nx2_glue.py.
 *
 * The numpy expressions of compound/prepare.py:densprepare element by element, in their order,
 * with floating-point contraction off: the same numbers to the bit. */
#include <stdint.h>

#ifdef __clang__
#pragma STDC FP_CONTRACT OFF
#endif

/* For rows i < nex: w1, w2, w3 at eout[i] over the nodes (ea, eb, ec)[i], then
 * Tjl(i, l, k) = ((w1 tjl[na] + w2 tjl[nb]) + w3 tjl[nc]) for l <= lm[i], else 0; zero below
 * `transeps`; times `fn`. Tl the same when `tl` is not null. tjl (R, L, 3) and tl (R, L)
 * contiguous; out_tjl (nex, L, 3), out_tl (nex, L). Returns 0. */
int nx2_glue_interp(int64_t nex, int64_t L, const double *eout, const double *ea,
                    const double *eb, const double *ec, const int64_t *na, const int64_t *nb,
                    const int64_t *nc, const int64_t *lm, const double *tjl, const double *tl,
                    double transeps, double fn, double *out_tjl, double *out_tl)
{
    for (int64_t i = 0; i < nex; i++) {
        double e = eout[i], a = ea[i], b = eb[i], c = ec[i];
        double w1 = (e - b) * (e - c) / ((a - b) * (a - c));
        double w2 = (e - a) * (e - c) / ((b - a) * (b - c));
        double w3 = (e - a) * (e - b) / ((c - a) * (c - b));
        const double *ja = tjl + na[i] * L * 3, *jb = tjl + nb[i] * L * 3,
                     *jc = tjl + nc[i] * L * 3;
        for (int64_t l = 0; l < L; l++) {
            int keep = l <= lm[i];
            for (int64_t k = 0; k < 3; k++) {
                int64_t q = l * 3 + k;
                double v = keep ? (w1 * ja[q] + w2 * jb[q]) + w3 * jc[q] : 0.0;
                out_tjl[(i * L + l) * 3 + k] = (v < transeps ? 0.0 : v) * fn;
            }
            if (tl) {
                const double *ta = tl + na[i] * L, *tb = tl + nb[i] * L, *tc = tl + nc[i] * L;
                double u = keep ? (w1 * ta[l] + w2 * tb[l]) + w3 * tc[l] : 0.0;
                out_tl[i * L + l] = (u < transeps ? 0.0 : u) * fn;
            }
        }
    }
    return 0;
}
