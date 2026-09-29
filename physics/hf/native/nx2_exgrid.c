/* MERGED2: TALYS's `exgrid.f90` excitation-energy bins of one residual -- `Ex(0:maxex)` and
 * `deltaEx` -- as one C call.
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * `core.grids.excitation_energies` was, on the merged2 default chart path, the largest remaining
 * pure-numeric function with no native content at all (3.42 CPU-s of a 256 CPU-s whole-chart
 * pass, 109,375 calls -- docs/results/hf-merged2.md). Its cost is numpy's per-call overhead on
 * a dozen tiny float32 array operations, not arithmetic.
 *
 * `nx2_exgrid` is that function statement for statement, in float32 exactly as the numpy body
 * has it: the discrete levels 0..top (stopping at the first level at or above Exmax), their
 * half-widths, then `nexbins` equidistant continuum bins. Every float32 operation is its own
 * statement so no compiler may contract a product and a sum into one fused step.
 *
 * Not handled (returns -1, the wrapper keeps the Python body): the logarithmic bins
 * (`equidistant n` with Ex(NL) > 0, whose float32 `np.log`/`np.exp` bits are numpy's own), and
 * any grid that does not fit (0:numex), where the Python body raises.
 *
 * TALYS: exgrid.f90:1 (exgrid)
 * Test: tests/hf/test_nx2_exgrid.py */
#include <stdint.h>

/*   edis      : (nedis,) edis(0:) of the residual, float64 holding the values to be rounded
 *   nlast     : NL; exmax: Exmax; nbins: nbins; aix: Zix + Nix; flagequi: equidistant
 *   has_etot  : store Etotal (etot) in Ex(maxex + 1) (the compound nucleus)
 *   numex     : NUMEX
 *   ex, dex   : outputs of capacity cap_ex / cap_dex, zero-filled up to maxex + 1 / maxex here
 * Returns maxex, or -1 for the Python body. */
int64_t nx2_exgrid(const double *edis, int64_t nedis, int64_t nlast, double exmax, int64_t nbins,
                   int64_t aix, int64_t flagequi, int64_t has_etot, double etot, int64_t numex,
                   double *ex, int64_t cap_ex, double *dex, int64_t cap_dex)
{
    if (nlast < 0 || nlast > numex)
        return -1;
    /* ed = zeros(max(len, nlast + 2, 2), f32); ed[:len] = edis -- only ed(0:NL+1) is read */
    const int64_t ned = nlast + 2;
    float edbuf[1024];
    if (ned > 1024)
        return -1;
    for (int64_t k = 0; k < ned; k++)
        edbuf[k] = k < nedis ? (float)edis[k] : 0.0f;
    const float *ed = edbuf;
    const float emax = (float)exmax, half = 0.5f;
    int64_t top = nlast, stopped = 0;
    for (int64_t k = 1; k <= nlast; k++)
        if (ed[k] >= emax) {
            top = k - 1;
            stopped = 1;
            break;
        }
    if (stopped) {
        const int64_t maxex = top;
        if (maxex + 2 > cap_ex || maxex + 1 > cap_dex)
            return -1;
        for (int64_t k = 0; k <= top; k++)
            ex[k] = ed[k];
        ex[top + 1] = 0.0;
        dex[0] = half * ed[1];
        for (int64_t k = 1; k <= top; k++) {
            const int64_t kp = nlast < k + 1 ? nlast : k + 1;
            const float d = ed[kp] - ed[k - 1];
            dex[k] = half * d;
        }
        return maxex;
    }
    int64_t nexbins;
    if (aix <= 4) {
        nexbins = nbins;
    } else if (aix <= 8) {
        const float tenth = 0.1f * (float)(aix - 4);
        const float frac = 1.0f - tenth;
        const float prod = frac * (float)nbins;
        nexbins = (int64_t)prod;
    } else {
        /* Python's floor division */
        nexbins = nbins >= 0 ? nbins / 2 : -((-nbins + 1) / 2);
    }
    if (nexbins < 2)
        nexbins = 2;
    const int64_t maxex = nlast + nexbins;
    /* the Python body's slice assignments raise past (0:numex) */
    if (maxex > numex || maxex + 2 > cap_ex || maxex + 1 > cap_dex)
        return -1;
    const float eb = ed[nlast];
    if (!(flagequi || eb == 0.0f))
        return -1;
    const float ebp = eb + 0.001f;
    const float ee = ebp > emax ? ebp : emax;
    const float span = ee - eb;
    const float nf = (float)nexbins;
    for (int64_t k = 0; k <= nlast; k++)
        ex[k] = ed[k];
    dex[0] = half * ed[1];
    for (int64_t k = 1; k <= nlast; k++) {
        const int64_t kp = nlast < k + 1 ? nlast : k + 1;
        const float d = ed[kp] - ed[k - 1];
        dex[k] = half * d;
    }
    float lo = eb; /* eup[0] */
    {
        const float q = 0.0f / nf;
        const float s = q * span;
        lo = eb + s;
    }
    for (int64_t i = 1; i <= nexbins; i++) {
        const float q = (float)i / nf;
        const float s = q * span;
        const float hi = eb + s;
        const float sum = lo + hi;
        ex[nlast + i] = half * sum;
        const float w = hi - lo;
        dex[nlast + i] = w;
        lo = hi;
    }
    ex[maxex + 1] = has_etot ? (double)(float)etot : 0.0;
    return maxex;
}
