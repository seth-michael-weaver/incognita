/* GLUEFINISH: TALYS's `population.f90` inner loop -- the pre-equilibrium (plus giant-resonance)
 * spectra folded onto each binary residual's excitation grid -- as one C call per residual type.
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * `compound.population.population` was, on the default chart path, the largest remaining
 * pure-numeric stage still entirely in Python (5.26 CPU-s of a 264 CPU-s whole-chart pass,
 * 9,640 calls, no native content at all -- docs/results/hf-gluefinish.md). Its cost is not in
 * the arithmetic but in the count of Python steps: ~5.0 M `_p1` calls, ~2.5 M `_cut` calls and
 * ~38 k `_mulpre_bin` calls a chart, each of them a few flops.
 *
 * `nx2_pop_type` is that loop for one ejectile type, statement for statement:
 *   * the bin-edge nodes of `_bin_nodes_many` (a float32 `searchsorted(..., "right")` over
 *     egrid[ib..ie] with locate's two tie rules) when that grid is strictly increasing in float32
 *     and no node falls off the array, and `_bin_nodes`' float32 bisection (`locate_scalar`)
 *     otherwise -- the same all-or-nothing choice the Python makes for the whole type;
 *   * `ea = egrid[na]` is taken with numpy's negative-index wrap, which is what the Python reads
 *     when a bin edge sits below egrid[ib] (`na = ib - 1 = -1`) before `max(na1, 0)` clamps the
 *     index the spectrum is read at;
 *   * `pol1` and the 1e-30 cut in the order `population.f90` has them, so every stored bin is the
 *     Python path's bit;
 *   * multiple pre-equilibrium (`_mulpre_bin`, live only at Einc >= emulpre = 20 MeV) with its
 *     one- and two-component particle-hole ladders.
 * The renormalisation that follows (population.f90:246-268) stays in Python: it is one numpy
 * `sum` and one in-place multiply per type, and numpy's pairwise summation is not reproduced
 * here.
 *
 * pespinmodel >= 3 (`preeqpop`) is not handled: the wrapper keeps the Python path for it. An
 * incident-neutron run never sets it (input_preeqmodel.f90:76-80).
 *
 * TALYS: population.f90:1 (population), locate.f90:1 (locate), pol1.f90:1 (pol1)
 * Test: tests/hf/test_nx2_pop.py */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>

#define POP_XS_MIN 1.0e-30 /* population.f90:168 */

static inline double pop_cut(double x)
{
    return x < POP_XS_MIN ? 0.0 : x; /* signed, and NaN falls through, as numpy's `where` does */
}

static inline double pop_p1(double x1, double x2, double y1, double y2, double x)
{
    return y1 + (x - x1) / (x2 - x1) * (y2 - y1); /* pol1 */
}

static inline double pop_spec(const double *xspreeq, const double *xsgr, int64_t i)
{
    return xsgr == NULL ? xspreeq[i] : xspreeq[i] + xsgr[i];
}

/* `locate_scalar(egrid, ib, ie, x)`: the float32 bisection of locate.f90 */
static int64_t pop_locate(const double *eg, int64_t ib, int64_t ie, double x)
{
    const float xf = (float)x;
    const float xib = (float)eg[ib], xie = (float)eg[ie];
    int64_t jl = ib - 1, ju = ie + 1;
    const int ascend = xie >= xib;
    if (ib > ie)
        return 0;
    while (ju - jl > 1) {
        const int64_t jm = (ju + jl) >> 1;
        const float xm = (float)eg[jm];
        if (ascend == (xf >= xm))
            jl = jm;
        else
            ju = jm;
    }
    if (xf == xib)
        return ib;
    if (xf == xie)
        return ie - 1;
    return jl;
}

/* `_bin_nodes_many`'s node for one edge: ib - 1 + searchsorted(egrid[ib..ie], v, "right"), with
 * NaN put back at ib - 1 and locate's ties at ib and ie. */
static int64_t pop_node_many(const double *eg, int64_t ib, int64_t ie, float v)
{
    int64_t lo = 0, hi = ie - ib + 1; /* number of seg entries <= v */
    if (isnan((double)v))
        return ib - 1;
    while (lo < hi) {
        const int64_t mid = (lo + hi) >> 1;
        if ((float)eg[ib + mid] <= v)
            lo = mid + 1;
        else
            hi = mid;
    }
    int64_t jl = ib - 1 + lo;
    if (v == (float)eg[ie])
        jl = ie - 1;
    if (v == (float)eg[ib])
        jl = ib;
    return jl;
}

/* egrid[na] with numpy's wrap for na < 0 */
static inline double pop_eg_at(const double *eg, int64_t neg, int64_t na)
{
    return eg[na < 0 ? neg + na : na];
}

/* The two edges of bin `nexout`, as `_bin_nodes_many` / `_bin_nodes` give them. */
typedef struct {
    int64_t na1, nb1, na2, nb2;
    double ea1, eb1, ea2, eb2, elow, ehigh, dex;
} pop_bin;

static void pop_edges(const double *eg, int64_t neg, int64_t ib, int64_t ie, double etop,
                      double emax, const double *ex, const double *dex_arr, int64_t nexout,
                      int use_many, pop_bin *b)
{
    const double dex = dex_arr[nexout];
    const double eout = emax - ex[nexout];
    b->dex = dex;
    b->elow = eout - 0.5 * dex;
    b->ehigh = eout + 0.5 * dex;
    if (use_many) {
        b->na1 = pop_node_many(eg, ib, ie, (float)b->elow);
        b->na2 = pop_node_many(eg, ib, ie, (float)b->ehigh);
    } else {
        b->na1 = pop_locate(eg, ib, ie, b->elow);
        b->na2 = pop_locate(eg, ib, ie, b->ehigh);
    }
    b->nb1 = b->na1 + 1;
    b->nb2 = b->na2 + 1;
    b->ea1 = pop_eg_at(eg, neg, b->na1);
    b->ea2 = pop_eg_at(eg, neg, b->na2);
    /* a node at `neg` is what makes `_bin_nodes_many` give up; the caller checks and the value is
     * never used, so do not read past the array for it */
    const double e1 = b->nb1 < neg ? pop_eg_at(eg, neg, b->nb1) : 0.0;
    const double e2 = b->nb2 < neg ? pop_eg_at(eg, neg, b->nb2) : 0.0;
    b->eb1 = etop < e1 ? etop : e1;
    b->eb2 = etop < e2 ? etop : e2;
}

/* `_mulpre_bin`'s `integ` on one particle-hole row */
static inline double pop_integ(const double *row, const pop_bin *b)
{
    const double a = pop_p1(b->ea1, b->eb1, row[b->na1], row[b->nb1], b->elow);
    const double c = pop_p1(b->ea2, b->eb2, row[b->na2], row[b->nb2], b->ehigh);
    return pop_cut(0.5 * (a + c) * b->dex);
}

/* One residual type's bin loop. Returns 1 when it ran, 0 when the caller must use Python
 * (a node off the end of a step array). `popex` is (maxex+1,) and already zeroed. */
int64_t nx2_pop_type(const double *eg, int64_t neg, int64_t ib, int64_t ie, double etotal,
                     double sep, const double *ex, const double *dex_arr, int64_t nlast,
                     int64_t maxex, const double *xspreeq, const double *xsgr,
                     int64_t nspec, double *popex,
                     int64_t mulpre, int64_t flag2comp, int64_t maxpar, int64_t p0, int64_t ppi0,
                     int64_t pnu0, int64_t parA, int64_t parZ, int64_t parN,
                     const double *xsstep, const double *xsstep2, int64_t nstep, double *popph,
                     double *popph2)
{
    const int64_t lo = nlast + 1, hi = maxex + 1;
    const double etop = etotal - sep;
    const double emax = etotal - sep; /* `_bin_nodes_many`'s `emax`, the same value */
    int use_many = 1;

    if (hi <= lo || ib > ie)
        return 1; /* nothing to do; `_bin_nodes_many` would have returned None */

    /* `_bin_nodes_many` is used only when egrid[ib..ie] is strictly increasing in float32 ... */
    for (int64_t i = ib; i < ie; i++) {
        if (!((float)eg[i + 1] > (float)eg[i])) {
            use_many = 0;
            break;
        }
    }
    /* ... and no node of any bin (not only the bins the loop keeps) falls off the array */
    if (use_many) {
        for (int64_t nexout = lo; nexout < hi; nexout++) {
            pop_bin b;
            pop_edges(eg, neg, ib, ie, etop, emax, ex, dex_arr, nexout, 1, &b);
            if (b.nb1 >= neg || b.nb2 >= neg) {
                use_many = 0;
                break;
            }
        }
    }

    const int64_t mp1 = maxpar + 1;
    for (int64_t nexout = lo; nexout < hi; nexout++) {
        pop_bin b;
        const double eout = emax - ex[nexout];
        if (eout < eg[ib])
            continue;
        pop_edges(eg, neg, ib, ie, etop, emax, ex, dex_arr, nexout, use_many, &b);
        int64_t na1 = b.na1 > 0 ? b.na1 : 0; /* max(na1, 0), after `ea1` was read */
        /* the spectrum is only eend(type) long, shorter than egrid; the Python would raise here */
        if (b.nb1 >= neg || b.nb2 >= neg || b.nb1 >= nspec || b.nb2 >= nspec || b.na2 < 0)
            return 0;
        const double xslow = pop_p1(b.ea1, b.eb1, pop_spec(xspreeq, xsgr, na1),
                                    pop_spec(xspreeq, xsgr, b.nb1), b.elow);
        const double xshigh = pop_p1(b.ea2, b.eb2, pop_spec(xspreeq, xsgr, b.na2),
                                     pop_spec(xspreeq, xsgr, b.nb2), b.ehigh);
        popex[nexout] = pop_cut(0.5 * (xslow + xshigh) * b.dex);
        if (!mulpre)
            continue;
        /* population.f90:180-236, with `_mulpre_bin`'s own (na1, nb1) -- not the clamped one */
        if (b.nb1 >= nstep || b.nb2 >= nstep || b.na1 < 0)
            return 0;
        if (!flag2comp) {
            for (int64_t pc = p0; pc <= maxpar; pc++) {
                const int64_t p = pc - parA, h = pc - p0;
                if (p < 0 || h < 0)
                    continue;
                popph[(nexout * mp1 + p) * mp1 + h] = pop_integ(xsstep + pc * nstep, &b);
            }
            continue;
        }
        for (int64_t pcpi = ppi0; pcpi <= maxpar; pcpi++) {
            const int64_t ppi = pcpi - parZ, hpi = pcpi - ppi0;
            if (ppi < 0 || hpi < 0)
                continue;
            for (int64_t pcnu = pnu0; pcnu <= maxpar; pcnu++) {
                const int64_t pnu = pcnu - parN, hnu = pcnu - pnu0;
                if (pnu < 0 || hnu < 0)
                    continue;
                const double *row = xsstep2 + (pcpi * mp1 + pcnu) * nstep;
                popph2[(((nexout * mp1 + ppi) * mp1 + hpi) * mp1 + pnu) * mp1 + hnu] =
                    pop_integ(row, &b);
            }
        }
    }
    return 1;
}
