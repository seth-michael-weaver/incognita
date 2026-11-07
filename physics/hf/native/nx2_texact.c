/* PERFHF: fission/wkb.py's `_t_exact_vec` transfer loop (IDEA_EXACTFIS, Incognita extension) in C.
 *
 * The loop runs the staircase from the right edge to the left one, at every energy at once:
 *
 *     er = exp(1j*kr*x); psi = a*er + b/er
 *     g  = (1j*kr*(a*er - b/er) / M[j+1]) * M[j] / (1j*kl)
 *     el = exp(1j*kl*x); a, b = 0.5*(psi + g)/el, 0.5*(psi - g)*el
 *
 * numpy evaluated it one ufunc at a time (~24 calls per staircase edge, 400-1200 edges per hump), so the
 * per-call overhead, not the arithmetic, set the time. Here every operation is numpy's own, operand for
 * operand, so the result is bit-identical (tests/hf/test_perfhf_gate.py holds it to the numpy twin):
 *   complex multiply  numpy's SIMD `simd_cmul` (AVX2/AVX-512 fmaddsub):
 *                     re = fma(ar, br, -(ai*bi)), im = fma(ar, bi, ai*br), a the left operand
 *   complex divide    numpy's loops.c Smith rule (no contraction)
 *   real operands     promoted to (x, 0) first, as numpy promotes a float64 to complex128
 *   exp               libm's cexp, which numpy's npy_cexp calls
 * The build keeps -ffp-contract=off, so the only fused operations are the explicit fma() calls.
 *
 * k: (nedge + 1, ne) complex128 row-major (interleaved re, im); M: nedge + 1; edges: nedge.
 * a_out: ne complex128 (the final `a`). Returns 0.
 */
#include <complex.h>
#include <math.h>
#include <stdint.h>

typedef struct { double re, im; } cx;

#if defined(__x86_64__) && defined(__GNUC__)
#define TX_FMA __attribute__((target("fma")))
#else
#define TX_FMA
#endif

static inline TX_FMA cx cmul(cx a, cx b)
{
    cx r;
    r.re = fma(a.re, b.re, -(a.im * b.im));
    r.im = fma(a.re, b.im, a.im * b.re);
    return r;
}

static inline cx cdiv(cx n, cx d)
{
    double ar = fabs(d.re), ai = fabs(d.im);
    cx r;
    if (ar >= ai) {
        if (ar == 0 && ai == 0) {
            r.re = n.re / ar;
            r.im = n.im / ar;
        } else {
            double rat = d.im / d.re;
            double scl = 1.0 / (d.re + d.im * rat);
            r.re = (n.re + n.im * rat) * scl;
            r.im = (n.im - n.re * rat) * scl;
        }
    } else {
        double rat = d.re / d.im;
        double scl = 1.0 / (d.im + d.re * rat);
        r.re = (n.re * rat + n.im) * scl;
        r.im = (n.im * rat - n.re) * scl;
    }
    return r;
}

static inline cx cexp_(cx z)
{
    double complex w = cexp(CMPLX(z.re, z.im));
    cx r = {creal(w), cimag(w)};
    return r;
}

static inline cx cadd(cx a, cx b) { cx r = {a.re + b.re, a.im + b.im}; return r; }
static inline cx csub(cx a, cx b) { cx r = {a.re - b.re, a.im - b.im}; return r; }

int nx2_fis_texact(int64_t ne, int64_t nedge, const double *edges, const double *M, const double *k,
                   double *a_out)
{
    const cx IU = {0.0, 1.0}, HALF = {0.5, 0.0};
    for (int64_t e = 0; e < ne; e++) {
        cx a = {1.0, 0.0}, b = {0.0, 0.0};
        for (int64_t j = nedge - 1; j >= 0; j--) {
            cx x = {edges[j], 0.0};
            cx kr = {k[2 * ((j + 1) * ne + e)], k[2 * ((j + 1) * ne + e) + 1]};
            cx kl = {k[2 * (j * ne + e)], k[2 * (j * ne + e) + 1]};
            cx ikr = cmul(IU, kr);
            cx er = cexp_(cmul(ikr, x));
            cx ae = cmul(a, er), be = cdiv(b, er);
            cx psi = cadd(ae, be);
            cx Mr = {M[j + 1], 0.0}, Ml = {M[j], 0.0};
            cx g = cdiv(cmul(cdiv(cmul(ikr, csub(ae, be)), Mr), Ml), cmul(IU, kl));
            cx el = cexp_(cmul(cmul(IU, kl), x));
            a = cdiv(cmul(HALF, cadd(psi, g)), el);
            b = cmul(cmul(HALF, csub(psi, g)), el);
        }
        a_out[2 * e] = a.re;
        a_out[2 * e + 1] = a.im;
    }
    return 0;
}
