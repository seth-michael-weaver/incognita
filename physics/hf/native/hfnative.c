/* SPEEDT3: compiled kernels for the transmission-coefficient stages of the TALYS port.
 *
 * Every kernel repeats, element by element and in the same order, the floating-point operations
 * of the Python/numpy/torch loop it replaces, so its results are bit-identical to that loop
 * (tests/hf/test_native.py). Build with scripts/build_native.sh; the flags there
 * (-O2 -fno-fast-math -ffp-contract=off -fno-tree-vectorize) keep every expression as written:
 * no contraction to FMA, no reassociation, no vectorised reductions. Where torch itself fuses a
 * multiply-add (the scalar tail of its complex product), the kernel calls fma() explicitly.
 *
 * What the torch operations compute, as established on x86-64 (probes in the SPEEDT3 report):
 *   complex a*b, contiguous:  re = ar*br - ai*bi, im = ar*bi + ai*br on the first n - n%4
 *                             elements, re = fma(ar, br, -(ai*bi)), im = fma(ar, bi, ai*br) on the
 *                             last n%4 (its SIMD loop and scalar tail);
 *   complex a*b, strided a:   the fma form on every element;
 *   complex |z|:              hypot(re, im);
 *   complex z / real s:       numpy's Smith division with d = 0 (rat = 0/s, scl = 1/(s + 0*rat));
 *   batched matmul, N**3 < 400: torch's own triple loop, acc = 0 + sum_k (plain product);
 *   batched matmul, larger:   one zgemm per matrix (operands swapped for row-major order);
 *   linalg.solve:             zgetrf + zgetrs('N') per matrix on column-major copies;
 *   linalg.qr:                zgeqrf + zungqr per matrix, workspace from a size query;
 *   solve_triangular(left=False, upper): ztrsm('R', 'U', 'N', 'N') per matrix;
 *   tensordot(w[:, 1:top+1], H, dims=1): zgemm(M x 3 = H(M x top) * w(top x 3), lda = npts);
 *   sum over a leading axis:  0 + a0 + a1 + ...
 * The LAPACK/BLAS routines are torch's own (MKL inside libtorch_cpu), handed over by address, so
 * they are the same code torch runs. They are called at one thread only (the Python side checks).
 */

#if defined(__x86_64__)
#include <immintrin.h>
#define HF_X86 1
#elif defined(__aarch64__)
#include <arm_neon.h>
#define HF_X86 0
#define HF_NEON 1
#else
#define HF_X86 0 /* CCFAST2: arm64 (the Mac) builds the scalar paths; its bits are not x86's anyway */
#endif
#ifndef HF_NEON
#define HF_NEON 0
#endif
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef void (*zgemm_t)(const char *, const char *, const int *, const int *, const int *,
                        const double *, const double *, const int *, const double *, const int *,
                        const double *, double *, const int *);
typedef void (*zgetrf_t)(const int *, const int *, double *, const int *, int *, int *);
typedef void (*zgetrs_t)(const char *, const int *, const int *, const double *, const int *,
                         const int *, double *, const int *, int *);
typedef void (*zgeqrf_t)(const int *, const int *, double *, const int *, double *, double *,
                         const int *, int *);
typedef void (*zungqr_t)(const int *, const int *, const int *, double *, const int *,
                         const double *, double *, const int *, int *);
typedef void (*ztrsm_t)(const char *, const char *, const char *, const char *, const int *,
                        const int *, const double *, const double *, const int *, double *,
                        const int *);

static zgemm_t zgemm_p;
static zgetrf_t zgetrf_p;
static zgetrs_t zgetrs_p;
static zgeqrf_t zgeqrf_p;
static zungqr_t zungqr_p;
static ztrsm_t ztrsm_p;

int hf_version(void) { return 1; }

void hf_set_lapack(void *zgemm, void *zgetrf, void *zgetrs, void *zgeqrf, void *zungqr,
                   void *ztrsm)
{
    zgemm_p = (zgemm_t)zgemm;
    zgetrf_p = (zgetrf_t)zgetrf;
    zgetrs_p = (zgetrs_t)zgetrs;
    zgeqrf_p = (zgeqrf_t)zgeqrf;
    zungqr_p = (zungqr_t)zungqr;
    ztrsm_p = (ztrsm_t)ztrsm;
}

/* ------------------------------------------------------------------------------ Coulomb, real */

/* schrodinger._numerov_inward_many. The columns never mix, so they run four at a time on AVX2
 * lanes (add, sub, mul and div are exact per lane; nothing is fused). 1 - 2 eta / x is evaluated
 * once per node and shared by C at step i and A at step i + 1, as the numpy version does: x1 at
 * i + 1 is the same expression as x0 at i. A lane past its last step is frozen by a blend. */
static void numerov_scalar(const double ee, const double ra, const double r_b, const double gb,
                           const double gb1, const int64_t nn, double *out)
{
    const double h = (r_b - ra) / (double)nn;
    const double c = h * h / 12.0;
    const double c5 = 5.0 * c;
    const double e2 = 2.0 * ee;
    double u2 = gb, u1 = gb1, prev = 0.0;
    double q1 = 1.0 - e2 / (r_b - (double)1 * h);
    for (int64_t i = 2; i < nn + 2; i++) {
        const double x1 = r_b - (double)(i - 1) * h;
        const double x0 = r_b - (double)i * h;
        const double q0 = 1.0 - e2 / x0;
        const double A = 2.0 * (1.0 - c5 * q1);
        const double B = 1.0 + c * (1.0 - e2 / (x1 + h));
        const double C = 1.0 + c * q0;
        double t = A * u1;
        const double b = B * u2;
        t = t - b;
        u2 = u1;
        u1 = t / C;
        q1 = q0;
        if (i == nn - 1)
            prev = u1;
    }
    out[0] = u2;
    out[1] = u1;
    out[2] = prev;
    out[3] = h;
    out[4] = c;
    out[5] = e2;
}

#if HF_X86
__attribute__((target("avx2")))
static void numerov_lanes(const double *ee, const double *ra, const double *rb, const double *gb,
                          const double *gb1, const int64_t *nn, double out[4][6])
{
    double hh[4], cc[4], c55[4], ee2[4], nend[4], nprev[4];
    int64_t big = 0;
    for (int k = 0; k < 4; k++) {
        hh[k] = (rb[k] - ra[k]) / (double)nn[k];
        cc[k] = hh[k] * hh[k] / 12.0;
        c55[k] = 5.0 * cc[k];
        ee2[k] = 2.0 * ee[k];
        nend[k] = (double)(nn[k] + 1);
        nprev[k] = (double)(nn[k] - 1);
        if (nn[k] > big)
            big = nn[k];
    }
    const __m256d h = _mm256_loadu_pd(hh), c = _mm256_loadu_pd(cc), c5 = _mm256_loadu_pd(c55);
    const __m256d e2 = _mm256_loadu_pd(ee2), r_b = _mm256_loadu_pd(rb);
    const __m256d ne = _mm256_loadu_pd(nend), np_ = _mm256_loadu_pd(nprev);
    const __m256d one = _mm256_set1_pd(1.0), two = _mm256_set1_pd(2.0);
    __m256d u2 = _mm256_loadu_pd(gb), u1 = _mm256_loadu_pd(gb1), prev = _mm256_setzero_pd();
    __m256d q1 = _mm256_sub_pd(one, _mm256_div_pd(e2, _mm256_sub_pd(r_b, _mm256_mul_pd(_mm256_set1_pd(1.0), h))));
    for (int64_t i = 2; i < big + 2; i++) {
        const __m256d di = _mm256_set1_pd((double)i);
        const __m256d x1 = _mm256_sub_pd(r_b, _mm256_mul_pd(_mm256_set1_pd((double)(i - 1)), h));
        const __m256d x0 = _mm256_sub_pd(r_b, _mm256_mul_pd(di, h));
        const __m256d q0 = _mm256_sub_pd(one, _mm256_div_pd(e2, x0));
        const __m256d A = _mm256_mul_pd(two, _mm256_sub_pd(one, _mm256_mul_pd(c5, q1)));
        const __m256d B = _mm256_add_pd(one, _mm256_mul_pd(c, _mm256_sub_pd(one, _mm256_div_pd(e2, _mm256_add_pd(x1, h)))));
        const __m256d C = _mm256_add_pd(one, _mm256_mul_pd(c, q0));
        const __m256d t = _mm256_sub_pd(_mm256_mul_pd(A, u1), _mm256_mul_pd(B, u2));
        const __m256d un = _mm256_div_pd(t, C);
        const __m256d live = _mm256_cmp_pd(di, ne, _CMP_LE_OQ);
        u2 = _mm256_blendv_pd(u2, u1, live);
        u1 = _mm256_blendv_pd(u1, un, live);
        q1 = q0;
        prev = _mm256_blendv_pd(prev, u1, _mm256_cmp_pd(di, np_, _CMP_EQ_OQ));
    }
    double a[4], b[4], p[4];
    _mm256_storeu_pd(a, u2);
    _mm256_storeu_pd(b, u1);
    _mm256_storeu_pd(p, prev);
    for (int k = 0; k < 4; k++) {
        out[k][0] = a[k];
        out[k][1] = b[k];
        out[k][2] = p[k];
        out[k][3] = hh[k];
        out[k][4] = cc[k];
        out[k][5] = ee2[k];
    }
}

#endif

#if HF_NEON
/* COREX (arm64 only; NOT bit-identical to the scalar loop): eight columns of one step count on
 * four NEON vectors of two, stepped side by side so the out-of-order core runs the eight
 * recurrences in parallel. B takes 1 - 2 eta / x of the node two steps back instead of
 * re-dividing at x1 + h (the same node up to rounding), so a step divides twice, not three
 * times. Columns agree with the scalar loop to ~1e-12 relative (tests/hf/test_corex.py). */
static void numerov_neon8(const double *ee, const double *ra, const double *rb, const double *gb,
                          const double *gb1, const int64_t nn, double out[8][6])
{
    double hh[8], cc[8], c55[8], ee2[8], q2i[8], q1i[8];
    for (int k = 0; k < 8; k++) {
        hh[k] = (rb[k] - ra[k]) / (double)nn;
        cc[k] = hh[k] * hh[k] / 12.0;
        c55[k] = 5.0 * cc[k];
        ee2[k] = 2.0 * ee[k];
        q2i[k] = 1.0 - ee2[k] / ((rb[k] - hh[k]) + hh[k]);
        q1i[k] = 1.0 - ee2[k] / (rb[k] - hh[k]);
    }
    float64x2_t h[4], c[4], c5[4], e2[4], r_b[4], u1[4], u2[4], q1[4], q2[4], prev[4];
    for (int v = 0; v < 4; v++) {
        h[v] = vld1q_f64(hh + 2 * v);
        c[v] = vld1q_f64(cc + 2 * v);
        c5[v] = vld1q_f64(c55 + 2 * v);
        e2[v] = vld1q_f64(ee2 + 2 * v);
        r_b[v] = vld1q_f64(rb + 2 * v);
        u2[v] = vld1q_f64(gb + 2 * v);
        u1[v] = vld1q_f64(gb1 + 2 * v);
        q2[v] = vld1q_f64(q2i + 2 * v);
        q1[v] = vld1q_f64(q1i + 2 * v);
        prev[v] = vdupq_n_f64(0.0);
    }
    const float64x2_t one = vdupq_n_f64(1.0), two = vdupq_n_f64(2.0);
    for (int64_t i = 2; i < nn + 2; i++) {
        const float64x2_t di = vdupq_n_f64((double)i);
        for (int v = 0; v < 4; v++) {
            const float64x2_t x0 = vsubq_f64(r_b[v], vmulq_f64(di, h[v]));
            const float64x2_t q0 = vsubq_f64(one, vdivq_f64(e2[v], x0));
            const float64x2_t A = vmulq_f64(two, vsubq_f64(one, vmulq_f64(c5[v], q1[v])));
            const float64x2_t B = vaddq_f64(one, vmulq_f64(c[v], q2[v]));
            const float64x2_t C = vaddq_f64(one, vmulq_f64(c[v], q0));
            const float64x2_t t = vsubq_f64(vmulq_f64(A, u1[v]), vmulq_f64(B, u2[v]));
            u2[v] = u1[v];
            u1[v] = vdivq_f64(t, C);
            q2[v] = q1[v];
            q1[v] = q0;
        }
        if (i == nn - 1)
            for (int v = 0; v < 4; v++)
                prev[v] = u1[v];
    }
    double a[2], b[2], p[2];
    for (int v = 0; v < 4; v++) {
        vst1q_f64(a, u2[v]);
        vst1q_f64(b, u1[v]);
        vst1q_f64(p, prev[v]);
        for (int j = 0; j < 2; j++) {
            const int k = 2 * v + j;
            out[k][0] = a[j];
            out[k][1] = b[j];
            out[k][2] = p[j];
            out[k][3] = hh[k];
            out[k][4] = cc[k];
            out[k][5] = ee2[k];
        }
    }
}
#endif

void hf_numerov_inward(int64_t m, const double *ee, const double *ra, const double *rb,
                       const double *gb, const double *gb1, const int64_t *n, double *ga,
                       double *u1o, double *prevo, double *ho, double *co, double *e2o)
{
    double *outs[6] = {ga, u1o, prevo, ho, co, e2o};
    int64_t k = 0;
#if HF_NEON
    {
        /* groups of eight columns of equal step count, in first-seen order; the rest scalar */
        int64_t *idx = malloc(sizeof(int64_t) * (size_t)(m > 0 ? m : 1));
        char *done = calloc((size_t)(m > 0 ? m : 1), 1);
        if (idx && done) {
            for (int64_t a = 0; a < m; a++) {
                if (done[a])
                    continue;
                int64_t cnt = 0;
                for (int64_t b = a; b < m && cnt < 8; b++)
                    if (!done[b] && n[b] == n[a]) {
                        idx[cnt++] = b;
                        done[b] = 1;
                    }
                if (cnt < 8) {
                    for (int64_t j = 0; j < cnt; j++) {
                        double o[6];
                        const int64_t c = idx[j];
                        numerov_scalar(ee[c], ra[c], rb[c], gb[c], gb1[c], n[c], o);
                        for (int f = 0; f < 6; f++)
                            outs[f][c] = o[f];
                    }
                    continue;
                }
                double lee[8], lra[8], lrb[8], lgb[8], lgb1[8], o[8][6];
                for (int j = 0; j < 8; j++) {
                    const int64_t c = idx[j];
                    lee[j] = ee[c];
                    lra[j] = ra[c];
                    lrb[j] = rb[c];
                    lgb[j] = gb[c];
                    lgb1[j] = gb1[c];
                }
                numerov_neon8(lee, lra, lrb, lgb, lgb1, n[a], o);
                for (int j = 0; j < 8; j++)
                    for (int f = 0; f < 6; f++)
                        outs[f][idx[j]] = o[j][f];
            }
            free(idx);
            free(done);
            return;
        }
        free(idx);
        free(done);
    }
#endif
#if HF_X86
    if (__builtin_cpu_supports("avx2")) {
        /* lanes of equal step count first (every column of one call shares its count) */
        int64_t *idx = malloc(sizeof(int64_t) * (size_t)(m > 0 ? m : 1));
        char *done = calloc((size_t)(m > 0 ? m : 1), 1);
        if (idx && done) {
            for (int64_t a = 0; a < m; a++) {
                if (done[a])
                    continue;
                int64_t cnt = 0;
                for (int64_t b = a; b < m && cnt < 4; b++)
                    if (!done[b] && n[b] == n[a]) {
                        idx[cnt++] = b;
                        done[b] = 1;
                    }
                if (cnt < 4) {
                    for (int64_t j = 0; j < cnt; j++) {
                        double o[6];
                        const int64_t c = idx[j];
                        numerov_scalar(ee[c], ra[c], rb[c], gb[c], gb1[c], n[c], o);
                        for (int f = 0; f < 6; f++)
                            outs[f][c] = o[f];
                    }
                    continue;
                }
                double lee[4], lra[4], lrb[4], lgb[4], lgb1[4], o[4][6];
                int64_t ln[4];
                for (int j = 0; j < 4; j++) {
                    const int64_t c = idx[j];
                    lee[j] = ee[c];
                    lra[j] = ra[c];
                    lrb[j] = rb[c];
                    lgb[j] = gb[c];
                    lgb1[j] = gb1[c];
                    ln[j] = n[c];
                }
                numerov_lanes(lee, lra, lrb, lgb, lgb1, ln, o);
                for (int j = 0; j < 4; j++)
                    for (int f = 0; f < 6; f++)
                        outs[f][idx[j]] = o[j][f];
            }
            free(idx);
            free(done);
            return;
        }
        free(idx);
        free(done);
    }
#endif
    for (; k < m; k++) {
        double o[6];
        numerov_scalar(ee[k], ra[k], rb[k], gb[k], gb1[k], n[k], o);
        for (int f = 0; f < 6; f++)
            outs[f][k] = o[f];
    }
}

static inline double np_sign(double d)
{
    if (d > 0.0)
        return 1.0;
    if (d < 0.0)
        return -1.0;
    if (d == 0.0)
        return 0.0;
    return d; /* nan */
}

/* schrodinger._cf1_many, one column at a time: out is (m, width), written at orders < width. */
void hf_cf1(int64_t m, const double *eta, const double *rho, const int64_t *ltop, int64_t width,
            double *out, double *sign)
{
#if HF_NEON
    /* COREX (arm64 only): eight columns' backward recurrences stepped side by side (each joins
     * at its own top order), which the out-of-order core runs in parallel; every column's
     * operations are its own and in its order, so the values are the scalar loop's. */
    for (int64_t k0 = 0; k0 < m; k0 += 8) {
        const int g = (int)(m - k0 < 8 ? m - k0 : 8);
        double ir[8], et[8], f[8], sg[8];
        int64_t big = 0;
        for (int j = 0; j < g; j++) {
            const int64_t k = k0 + j;
            ir[j] = 1.0 / rho[k];
            et[j] = eta[k];
            const double Li = (double)(ltop[k] + 1);
            f[j] = Li * ir[j] + et[j] / Li;
            sg[j] = 1.0;
            if (ltop[k] > big)
                big = ltop[k];
        }
        for (int64_t L = big; L > 0; L--) {
            const double dl = (double)L;
            for (int j = 0; j < g; j++) {
                const int64_t k = k0 + j;
                if (L > ltop[k])
                    continue;
                const double S = dl * ir[j] + et[j] / dl;
                const double q = et[j] / dl;
                const double R2 = 1.0 + q * q;
                double d = S + f[j];
                if (fabs(d) < 1.0e-290)
                    d = 1.0e-290;
                sg[j] = sg[j] * np_sign(d);
                f[j] = S - R2 / d;
                if (L - 1 < width)
                    out[k * width + L - 1] = f[j];
            }
        }
        for (int j = 0; j < g; j++)
            sign[k0 + j] = sg[j];
    }
    return;
#endif
    for (int64_t k = 0; k < m; k++) {
        const double ir = 1.0 / rho[k];
        const double et = eta[k];
        const int64_t top = ltop[k];
        const double Li = (double)(top + 1);
        double f = Li * ir + et / Li;
        double sg = 1.0;
        double *o = out + k * width;
        for (int64_t L = top; L > 0; L--) {
            const double dl = (double)L;
            const double S = dl * ir + et / dl;
            const double q = et / dl;
            const double R2 = 1.0 + q * q;
            double d = S + f;
            if (fabs(d) < 1.0e-290)
                d = 1.0e-290;
            sg = sg * np_sign(d);
            f = S - R2 / d;
            if (L - 1 < width)
                o[L - 1] = f;
        }
        sign[k] = sg;
    }
}

/* ---------------------------------------------------------------- spherical ECIS radial loop */

/* numpy's (and torch's) complex division by the real s, i.e. by s + 0i */
static inline void cdiv_real(double a, double b, double s, double *r, double *i)
{
    const double c = s, d = 0.0;
    if (fabs(c) >= fabs(d)) {
        if (fabs(c) == 0.0 && fabs(d) == 0.0) {
            *r = a / fabs(c);
            *i = b / fabs(c);
        } else {
            const double rat = d / c;
            const double scl = 1.0 / (c + d * rat);
            *r = (a + b * rat) * scl;
            *i = (b - a * rat) * scl;
        }
    } else {
        const double rat = c / d;
        const double scl = 1.0 / (d + c * rat);
        *r = (a * rat + b) * scl;
        *i = (b * rat - a) * scl;
    }
}

/* torch's complex |z| on a contiguous, 64-byte-aligned tensor: its vector-math hypot (Sleef,
 * u05 accuracy, AVX2 ABI) on the first n - n%4 elements, glibc hypot on the tail. */
#if HF_X86
typedef __m256d (*vhypot_t)(__m256d, __m256d);
static vhypot_t vhypot_p;

void hf_set_vhypot(void *f) { vhypot_p = (vhypot_t)f; }

__attribute__((target("avx2")))
static void torch_cabs(int64_t n, const double *re, const double *im, double *out)
{
    int64_t i = 0;
    for (; i + 4 <= n; i += 4) {
        __m256d r = vhypot_p(_mm256_loadu_pd(re + i), _mm256_loadu_pd(im + i));
        _mm256_storeu_pd(out + i, r);
    }
    for (; i < n; i++)
        out[i] = hypot(re[i], im[i]);
}
#else
/* CCFAST2: no Sleef vector hypot outside x86; libm's hypot (to rounding, not to torch's bits) */
void hf_set_vhypot(void *f) { (void)f; }

static void torch_cabs(int64_t n, const double *re, const double *im, double *out)
{
    for (int64_t i = 0; i < n; i++)
        out[i] = hypot(re[i], im[i]);
}
#endif

/* schrodinger._integrate_ecis_many's radial loop for one job: x is (E, LJ, R) complex, the
 * outputs u(ism - 1) and u(ism + 1) are (E, LJ) complex. The elements never mix except through
 * the position of their |u| in the array, so each element runs 25 steps at a time (keeping its
 * row of x in cache) and the normalisation runs over all of them in array order. */
int hf_ecis_radial(int64_t E, int64_t LJ, int64_t R, int64_t nmax, const double *x,
                   const int64_t *ism, double *uam, double *uap)
{
    const int64_t T = E * LJ;
    double *st = malloc(sizeof(double) * (size_t)(T * 5));
    if (!st)
        return -1;
    double *pr = st, *pi = st + T, *cr = st + 2 * T, *ci = st + 3 * T, *s = st + 4 * T;
    for (int64_t q = 0; q < T; q++) {
        pr[q] = 0.0;
        pi[q] = 0.0;
        cr[q] = 1.0;
        ci[q] = 0.0;
        uam[2 * q] = uam[2 * q + 1] = uap[2 * q] = uap[2 * q + 1] = 0.0;
    }
    for (int64_t n0 = 1; n0 <= nmax; n0 += 25) {
        const int64_t n1 = n0 + 24 < nmax ? n0 + 24 : nmax;
        for (int64_t e = 0; e < E; e++) {
            const int64_t im1 = ism[e] - 1, is = ism[e];
            for (int64_t k = 0; k < LJ; k++) {
                const int64_t q = e * LJ + k;
                const double *xr = x + 2 * (q * R);
                double p_r = pr[q], p_i = pi[q], c_r = cr[q], c_i = ci[q];
                for (int64_t n = n0; n <= n1; n++) {
                    /* u_next = 2.0 * u_cur - u_prev - x[..., n - 1] * u_cur */
                    double tr = 2.0 * c_r - 0.0 * c_i;
                    double ti = 2.0 * c_i + 0.0 * c_r;
                    tr = tr - p_r;
                    ti = ti - p_i;
                    const double xa = xr[2 * (n - 1)], xb = xr[2 * (n - 1) + 1];
                    const double mr = fma(xa, c_r, -(xb * c_i));
                    const double mi = fma(xa, c_i, xb * c_r);
                    const double nr = tr - mr, ni = ti - mi;
                    if (n == im1) {
                        uam[2 * q] = c_r;
                        uam[2 * q + 1] = c_i;
                    }
                    if (n == is) {
                        uap[2 * q] = nr;
                        uap[2 * q + 1] = ni;
                    }
                    p_r = c_r;
                    p_i = c_i;
                    c_r = nr;
                    c_i = ni;
                }
                pr[q] = p_r;
                pi[q] = p_i;
                cr[q] = c_r;
                ci[q] = c_i;
            }
        }
        if (n1 % 25 == 0) {
            const int64_t n = n1;
            torch_cabs(T, cr, ci, s);
            for (int64_t e = 0; e < E; e++) {
                const int64_t im1 = ism[e] - 1, ip1 = ism[e] + 1;
                for (int64_t k = 0; k < LJ; k++) {
                    const int64_t q = e * LJ + k;
                    double sq = s[q];
                    if (!(sq != sq) && sq < 1.0e-300)
                        sq = 1.0e-300;
                    cdiv_real(pr[q], pi[q], sq, &pr[q], &pi[q]);
                    cdiv_real(cr[q], ci[q], sq, &cr[q], &ci[q]);
                    if (im1 <= n)
                        cdiv_real(uam[2 * q], uam[2 * q + 1], sq, &uam[2 * q], &uam[2 * q + 1]);
                    if (ip1 <= n + 1)
                        cdiv_real(uap[2 * q], uap[2 * q + 1], sq, &uap[2 * q], &uap[2 * q + 1]);
                }
            }
        }
    }
    free(st);
    return 0;
}

/* schrodinger._ecis_setup's x (its no-grad expression) and _integrate_ecis_many's radial loop
 * for one job, x built per element as it is needed instead of as an (E, L, J, R) array:
 *   g = so * ls2; g += central; g += coul; g *= mu h h; g = (k2 h h - L(L+1)/n**2) - g;
 *   x = g - (g * g) / 12,  with g * g following torch's contiguous rule on the flat (E, L, J, R)
 *   position (R = the potentials' radial length, at least nmax). so, central (E, R) complex; coul (E, R); ls2 (L, J); L (L,); kh, mhh (E,). */
#if !HF_NEON
static inline void ecis_x(double sor, double soi, double cer, double cei, double cl, double ls,
                          double f, double ab, int tail, double *xr, double *xi)
{
    double gr = sor * ls - soi * 0.0, gi = sor * 0.0 + soi * ls;
    gr = gr + cer;
    gi = gi + cei;
    gr = gr + cl;
    gi = gi + 0.0;
    double tr = gr * f - gi * 0.0, ti = gr * 0.0 + gi * f;
    gr = ab - tr;
    gi = 0.0 - ti;
    double sr, si;
    if (!tail) {
        sr = gr * gr - gi * gi;
        si = gr * gi + gi * gr;
    } else {
        sr = fma(gr, gr, -(gi * gi));
        si = fma(gr, gi, gi * gr);
    }
    const double rat = 0.0 / 12.0;
    const double scl = 1.0 / (12.0 + 0.0 * rat);
    const double dr = (sr + si * rat) * scl, di = (si - sr * rat) * scl;
    *xr = gr - dr;
    *xi = gi - di;
}
#endif

int hf_ecis_job(int64_t E, int64_t NL, int64_t NJ, int64_t R, int64_t nmax, const double *so,
                const double *central, const double *coul, const double *ls2, const double *Lv,
                const double *kh, const double *mhh, const int64_t *ism, double *uam, double *uap)
{
    const int64_t LJ = NL * NJ, T = E * LJ;
    if (nmax > R)
        return -2;
    const int64_t total = T * R, limit = total - total % 4;
    double *st = malloc(sizeof(double) * (size_t)(T * 5 + NL * R));
    if (!st)
        return -1;
    double *pr = st, *pi = st + T, *cr = st + 2 * T, *ci = st + 3 * T, *s = st + 4 * T;
    double *cent = st + 5 * T; /* (L, R): L(L+1) / n**2 */
    for (int64_t l = 0; l < NL; l++)
        for (int64_t n = 1; n <= R; n++) {
            const double nd = (double)n;
            cent[l * R + n - 1] = (Lv[l] * (Lv[l] + 1.0)) / (nd * nd);
        }
    for (int64_t q = 0; q < T; q++) {
        pr[q] = 0.0;
        pi[q] = 0.0;
        cr[q] = 1.0;
        ci[q] = 0.0;
        uam[2 * q] = uam[2 * q + 1] = uap[2 * q] = uap[2 * q + 1] = 0.0;
    }
    for (int64_t n0 = 1; n0 <= nmax; n0 += 25) {
        const int64_t n1 = n0 + 24 < nmax ? n0 + 24 : nmax;
#if HF_NEON
        (void)limit;
        /* COREX (arm64 only; to rounding, not to the x86 bits): every (l, j) row of one energy
         * steps side by side, radial step outermost, so the out-of-order core runs the rows'
         * recurrences in parallel; x = g - g^2/12 is evaluated directly (no tail/fma split). */
        for (int64_t e = 0; e < E; e++) {
            const int64_t im1 = ism[e] - 1, is = ism[e];
            const double *soe = so + 2 * e * R, *cee = central + 2 * e * R, *cle = coul + e * R;
            const double f = mhh[e];
            for (int64_t n = n0; n <= n1; n++) {
                const int64_t r = n - 1;
                const double sor = soe[2 * r], soi = soe[2 * r + 1];
                const double cer = cee[2 * r] + cle[r], cei = cee[2 * r + 1];
                for (int64_t l = 0; l < NL; l++) {
                    const double ab = kh[e] - cent[l * R + r];
                    for (int64_t j = 0; j < NJ; j++) {
                        const int64_t q = e * LJ + l * NJ + j;
                        const double ls = ls2[l * NJ + j];
                        const double gr = ab - (sor * ls + cer) * f;
                        const double gi = 0.0 - (soi * ls + cei) * f;
                        const double xa = gr - (gr * gr - gi * gi) / 12.0;
                        const double xb = gi - (gr * gi + gi * gr) / 12.0;
                        const double c_r = cr[q], c_i = ci[q];
                        const double nr = (2.0 * c_r - pr[q]) - fma(xa, c_r, -(xb * c_i));
                        const double ni = (2.0 * c_i - pi[q]) - fma(xa, c_i, xb * c_r);
                        if (n == im1) {
                            uam[2 * q] = c_r;
                            uam[2 * q + 1] = c_i;
                        }
                        if (n == is) {
                            uap[2 * q] = nr;
                            uap[2 * q + 1] = ni;
                        }
                        pr[q] = c_r;
                        pi[q] = c_i;
                        cr[q] = nr;
                        ci[q] = ni;
                    }
                }
            }
        }
#else
        for (int64_t e = 0; e < E; e++) {
            const int64_t im1 = ism[e] - 1, is = ism[e];
            const double *soe = so + 2 * e * R, *cee = central + 2 * e * R, *cle = coul + e * R;
            for (int64_t l = 0; l < NL; l++)
                for (int64_t j = 0; j < NJ; j++) {
                    const int64_t q = e * LJ + l * NJ + j;
                    const double ls = ls2[l * NJ + j];
                    double p_r = pr[q], p_i = pi[q], c_r = cr[q], c_i = ci[q];
                    for (int64_t n = n0; n <= n1; n++) {
                        const int64_t r = n - 1;
                        double xa, xb;
                        ecis_x(soe[2 * r], soe[2 * r + 1], cee[2 * r], cee[2 * r + 1], cle[r], ls,
                               mhh[e], kh[e] - cent[l * R + r], q * R + r >= limit, &xa, &xb);
                        /* u_next = 2.0 * u_cur - u_prev - x[..., n - 1] * u_cur */
                        double tr = 2.0 * c_r - 0.0 * c_i;
                        double ti = 2.0 * c_i + 0.0 * c_r;
                        tr = tr - p_r;
                        ti = ti - p_i;
                        const double mr = fma(xa, c_r, -(xb * c_i));
                        const double mi = fma(xa, c_i, xb * c_r);
                        const double nr = tr - mr, ni = ti - mi;
                        if (n == im1) {
                            uam[2 * q] = c_r;
                            uam[2 * q + 1] = c_i;
                        }
                        if (n == is) {
                            uap[2 * q] = nr;
                            uap[2 * q + 1] = ni;
                        }
                        p_r = c_r;
                        p_i = c_i;
                        c_r = nr;
                        c_i = ni;
                    }
                    pr[q] = p_r;
                    pi[q] = p_i;
                    cr[q] = c_r;
                    ci[q] = c_i;
                }
        }
#endif
        if (n1 % 25 == 0) {
            const int64_t n = n1;
            torch_cabs(T, cr, ci, s);
            for (int64_t e = 0; e < E; e++) {
                const int64_t im1 = ism[e] - 1, ip1 = ism[e] + 1;
                for (int64_t k = 0; k < LJ; k++) {
                    const int64_t q = e * LJ + k;
                    double sq = s[q];
                    if (!(sq != sq) && sq < 1.0e-300)
                        sq = 1.0e-300;
                    cdiv_real(pr[q], pi[q], sq, &pr[q], &pi[q]);
                    cdiv_real(cr[q], ci[q], sq, &cr[q], &ci[q]);
                    if (im1 <= n)
                        cdiv_real(uam[2 * q], uam[2 * q + 1], sq, &uam[2 * q], &uam[2 * q + 1]);
                    if (ip1 <= n + 1)
                        cdiv_real(uap[2 * q], uap[2 * q + 1], sq, &uap[2 * q], &uap[2 * q + 1]);
                }
            }
        }
    }
    free(st);
    return 0;
}

/* ------------------------------------------------------------- coupled channels, one block */

static const double ZONE[2] = {1.0, 0.0};
static const double ZZERO[2] = {0.0, 0.0};

static double *zalloc(int64_t count)
{
    size_t bytes = (size_t)(count * 16);
    bytes = (bytes + 64 + 63) & ~(size_t)63;
    double *p = aligned_alloc(64, bytes);
    if (p)
        memset(p, 0, bytes);
    return p;
}

/* row-major C = A B for N x N, as torch's batched matmul computes it */
static void matmul(int n, const double *A, const double *B, double *C)
{
    if ((int64_t)n * n * n < 400) {
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                double ar = 0.0, ai = 0.0;
                for (int k = 0; k < n; k++) {
                    const double sr = A[2 * (i * n + k)], si = A[2 * (i * n + k) + 1];
                    const double mr = B[2 * (k * n + j)], mi = B[2 * (k * n + j) + 1];
                    const double pr = sr * mr - si * mi;
                    const double pim = sr * mi + si * mr;
                    ar = ar + pr;
                    ai = ai + pim;
                }
                C[2 * (i * n + j)] = ar;
                C[2 * (i * n + j) + 1] = ai;
            }
        return;
    }
    zgemm_p("N", "N", &n, &n, &n, ZONE, B, &n, A, &n, ZZERO, C, &n);
}

static void transpose(int n, const double *a, double *o)
{
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            o[2 * (j * n + i)] = a[2 * (i * n + j)];
            o[2 * (j * n + i) + 1] = a[2 * (i * n + j) + 1];
        }
}

typedef struct {
    int n;
    double *a, *b, *tau, *work;
    int *piv;
    int lwork;
} ws_t;

/* X = solve(A, B), row-major N x N */
static void solve(ws_t *w, const double *A, const double *B, double *X)
{
    int n = w->n, info = 0;
    transpose(n, A, w->a);
    transpose(n, B, w->b);
    zgetrf_p(&n, &n, w->a, &n, w->piv, &info);
    zgetrs_p("N", &n, &n, w->a, &n, w->piv, w->b, &n, &info);
    transpose(n, w->b, X);
}

static int ensure_work(ws_t *w, int need)
{
    if (need < 1)
        need = 1;
    if (need <= w->lwork)
        return 0;
    free(w->work);
    w->work = zalloc(need);
    w->lwork = need;
    return w->work == NULL;
}

/* q, r = linalg.qr(A); R is written upper triangular with zeros below */
static int qr(ws_t *w, const double *A, double *Q, double *Rm)
{
    int n = w->n, info = 0, lw = -1;
    double wq[2];
    transpose(n, A, w->a);
    zgeqrf_p(&n, &n, w->a, &n, w->tau, wq, &lw, &info);
    if (ensure_work(w, (int)wq[0]))
        return -1;
    lw = (int)wq[0] < 1 ? 1 : (int)wq[0];
    zgeqrf_p(&n, &n, w->a, &n, w->tau, w->work, &lw, &info);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            Rm[2 * (i * n + j)] = j >= i ? w->a[2 * (j * n + i)] : 0.0;
            Rm[2 * (i * n + j) + 1] = j >= i ? w->a[2 * (j * n + i) + 1] : 0.0;
        }
    lw = -1;
    zungqr_p(&n, &n, &n, w->a, &n, w->tau, wq, &lw, &info);
    if (ensure_work(w, (int)wq[0]))
        return -1;
    lw = (int)wq[0] < 1 ? 1 : (int)wq[0];
    zungqr_p(&n, &n, &n, w->a, &n, w->tau, w->work, &lw, &info);
    transpose(n, w->a, Q);
    return 0;
}

/* X <- X R^-1 (solve_triangular(R, X, upper=True, left=False)), row-major, in place */
static void trsm_right(ws_t *w, const double *Rm, double *X)
{
    int n = w->n;
    transpose(n, Rm, w->a);
    transpose(n, X, w->b);
    ztrsm_p("R", "U", "N", "N", &n, &n, ZONE, w->a, &n, w->b, &n);
    transpose(n, w->b, X);
}

/* z <- f z for a real-valued complex factor (f, fi), torch's product formula */
static inline void rmul(double f, double fi, const double *z, double *o)
{
    const double re = f * z[0] - fi * z[1];
    const double im = f * z[1] + fi * z[0];
    o[0] = re;
    o[1] = im;
}

/* keep slots, as solver._numerov_blocks names them */
enum { K_UMM1, K_UM, K_UMP1, K_MMM1, K_MMP1, K_SP1, K_SM1 };

/* CCNUMEROV: ECIS's modified Numerov (`ecist.f::inch`) in place of the plain implicit step, for
 * the spherical spin-orbit case (NM == NULL).  Operation for operation what
 * `solver._numerov_blocks` does with `HF_CC_MODNUM=1`, so this path stays bitwise the torch one.
 * `hf_cc_set_modnum(0)` is the A/B lever. */
static int cc_modnum = 1;

void hf_cc_set_modnum(int64_t on) { cc_modnum = (int)on; }

/* solver._numerov_blocks for ONE block (B = 1).
 *   M, NM : (E, R, N, N) complex, NM may be NULL (no derivative coupling)
 *   u1    : (E, N, N) complex, the solutions at r_1
 *   h     : (E,) step; nmatch : (E,) matching index
 *   wts   : for npts = 3..7, the (3, npts) complex finite-difference weights (row-major)
 *   keep  : (7, E, N, N) complex output, zero-initialised by the caller
 * Returns 0, or -1 when memory runs out. */
int hf_cc_block(int64_t E, int64_t N64, int64_t R, const double *M, const double *NM,
                const double *u1, const double *h, const int64_t *nmatch, const double **wts,
                double *keep)
{
    const int n = (int)N64;
    const int64_t nn = (int64_t)n * n, mat = 2 * nn; /* doubles per matrix */
    const int deformed = NM != NULL;
    int64_t nmax = 0;
    for (int64_t e = 0; e < E; e++)
        if (nmatch[e] > nmax)
            nmax = nmatch[e];
    nmax += 2;
    if (nmax + 1 > R)
        return -2;
    int rc = -1;
    double *u_prev = zalloc(E * nn), *u_cur = zalloc(E * nn), *u_next = zalloc(E * nn);
    double *mu_cur = zalloc(E * nn), *mu_prev = zalloc(E * nn), *rhs = zalloc(E * nn);
    double *lhs = zalloc(E * nn), *tmp = zalloc(nn), *qm = zalloc(E * nn), *rm = zalloc(E * nn);
    double *hist[6] = {0}, *hstack = NULL, *v3 = NULL, *prod = NULL, *s3 = zalloc(nn);
    double *c = malloc(sizeof(double) * (size_t)E);
    ws_t w = {n, zalloc(nn), zalloc(nn), zalloc(n), NULL, malloc(sizeof(int) * (size_t)n), 0};
    int nhist = 0;
    if (!u_prev || !u_cur || !u_next || !mu_cur || !mu_prev || !rhs || !lhs || !tmp || !qm ||
        !rm || !s3 || !c || !w.a || !w.b || !w.tau || !w.piv)
        goto done;
    if (deformed) {
        for (int k = 0; k < 6; k++)
            if (!(hist[k] = zalloc(E * nn)))
                goto done;
        if (!(hstack = zalloc(6 * E * nn)) || !(v3 = zalloc(3 * E * nn)) ||
            !(prod = zalloc(3 * E * nn)))
            goto done;
    }
    for (int64_t e = 0; e < E; e++)
        c[e] = h[e] * h[e] / 12.0;
    memcpy(u_cur, u1, (size_t)(E * mat) * sizeof(double));
    if (deformed) {
        memcpy(hist[0], u1, (size_t)(E * mat) * sizeof(double));
        nhist = 1;
    }
    int captured = 0, have_mu_prev = 0;
    const int modnum = cc_modnum && !deformed;
    const int64_t RN = R * nn;
    for (int64_t i = 0; i < nmax; i++) {
        const int use_m1 = deformed && i != 0;
        const double fac[3] = {(double)i + 2.0, 10.0 * ((double)i + 1.0), use_m1 ? (double)i : 0.0};
        const int npts = i + 3 < 7 ? (int)(i + 3) : 7;
        const double *wt = deformed ? wts[npts - 3] : NULL;
        const int top = deformed ? (npts - 1 < nhist ? npts - 1 : nhist) : 0;
        int any_hit = 0;
        for (int64_t e = 0; e < E; e++)
            any_hit |= nmatch[e] == i;
        if (deformed && top) {
            /* v3 = tensordot(wt[:, 1:top+1], stack(hist[:top]), dims=1) */
            for (int k = 0; k < top; k++)
                memcpy(hstack + k * E * mat, hist[k], (size_t)(E * mat) * sizeof(double));
            int M3 = (int)(E * nn), three = 3;
            zgemm_p("N", "N", &M3, &three, &top, ZONE, hstack, &M3, wt + 2, &npts, ZZERO, v3, &M3);
        }
        for (int64_t e = 0; e < E; e++) {
            const double *mc = M + 2 * (e * RN + i * nn);
            const double *mn = M + 2 * (e * RN + (i + 1) * nn);
            const double *mp = M + 2 * (e * RN + (i - 1) * nn);
            const double *uc = u_cur + e * mat, *up = u_prev + e * mat;
            double *r = rhs + e * mat, *l = lhs + e * mat, *mu = mu_cur + e * mat;
            const double ce = c[e];
            matmul(n, mc, uc, mu);
            if (modnum) {
                /* u_next = (2 u_cur - u_prev) + 12c * M u + 12c^2 * M (M u) */
                double *mu2 = r;  /* rhs is dead on this path */
                double *un = u_next + e * mat;
                const double c12 = 12.0 * ce, c144 = c12 * ce;
                matmul(n, mc, mu, mu2);
                for (int64_t q = 0; q < mat; q++)
                    un[q] = 2.0 * uc[q] - up[q] + c12 * mu[q] + c144 * mu2[q];
                if (nmatch[e] == i) {
                    memcpy(keep + 2 * (K_UM * E * nn) + e * mat, uc, (size_t)mat * sizeof(double));
                    memcpy(keep + 2 * (K_UMM1 * E * nn) + e * mat, up, (size_t)mat * sizeof(double));
                    memcpy(keep + 2 * (K_UMP1 * E * nn) + e * mat, un, (size_t)mat * sizeof(double));
                    memcpy(keep + 2 * (K_MMM1 * E * nn) + e * mat, i > 0 ? mp : mc,
                           (size_t)mat * sizeof(double));
                    memcpy(keep + 2 * (K_MMP1 * E * nn) + e * mat, mn, (size_t)mat * sizeof(double));
                }
                continue;
            }
            /* rhs = 2.0 * (u_cur + 5.0 * c * mu_cur) */
            const double c5 = 5.0 * ce - 0.0 * 0.0, c5i = 5.0 * 0.0 + 0.0 * ce;
            for (int64_t q = 0; q < nn; q++) {
                double t[2];
                rmul(c5, c5i, mu + 2 * q, t);
                t[0] = uc[2 * q] + t[0];
                t[1] = uc[2 * q + 1] + t[1];
                rmul(2.0, 0.0, t, r + 2 * q);
            }
            if (i > 0) {
                double *mup = mu_prev + e * mat;
                if (!have_mu_prev)
                    matmul(n, mp, up, mup);
                for (int64_t q = 0; q < nn; q++) {
                    double t[2];
                    rmul(ce, 0.0, mup + 2 * q, t);
                    t[0] = up[2 * q] - t[0];
                    t[1] = up[2 * q + 1] - t[1];
                    r[2 * q] = r[2 * q] - t[0];
                    r[2 * q + 1] = r[2 * q + 1] - t[1];
                }
            }
            /* lhs = eye - c * m_next */
            for (int a = 0; a < n; a++)
                for (int b = 0; b < n; b++) {
                    const int64_t q = (int64_t)a * n + b;
                    double t[2];
                    rmul(ce, 0.0, mn + 2 * q, t);
                    l[2 * q] = (a == b ? 1.0 : 0.0) - t[0];
                    l[2 * q + 1] = 0.0 - t[1];
                }
            if (deformed) {
                const double *nhs[3] = {NM + 2 * (e * RN + (i + 1) * nn), NM + 2 * (e * RN + i * nn),
                                        use_m1 ? NM + 2 * (e * RN + (i - 1) * nn)
                                               : NM + 2 * (e * RN + i * nn)};
                if (top) {
                    for (int k = 0; k < 3; k++)
                        matmul(n, nhs[k], v3 + 2 * (k * E * nn) + e * mat, prod + 2 * (k * E * nn) + e * mat);
                    /* rhs = rhs + c * (fac4 * prod).sum(0) */
                    for (int64_t q = 0; q < nn; q++) {
                        double acc[2] = {0.0, 0.0};
                        for (int k = 0; k < 3; k++) {
                            double t[2];
                            rmul(fac[k], 0.0, prod + 2 * (k * E * nn) + e * mat + 2 * q, t);
                            acc[0] = acc[0] + t[0];
                            acc[1] = acc[1] + t[1];
                        }
                        double t[2];
                        rmul(ce, 0.0, acc, t);
                        r[2 * q] = r[2 * q] + t[0];
                        r[2 * q + 1] = r[2 * q + 1] + t[1];
                    }
                }
                /* lhs = lhs - c * (fac4 * wt[:, 0] * nh3).sum(0) */
                for (int64_t q = 0; q < nn; q++) {
                    double acc[2] = {0.0, 0.0};
                    for (int k = 0; k < 3; k++) {
                        const double wr = wt[2 * (k * npts)], wi = wt[2 * (k * npts) + 1];
                        const double fw = fac[k] * wr - 0.0 * wi, fwi = fac[k] * wi + 0.0 * wr;
                        double t[2];
                        rmul(fw, fwi, nhs[k] + 2 * q, t);
                        acc[0] = acc[0] + t[0];
                        acc[1] = acc[1] + t[1];
                    }
                    double t[2];
                    rmul(ce, 0.0, acc, t);
                    l[2 * q] = l[2 * q] - t[0];
                    l[2 * q + 1] = l[2 * q + 1] - t[1];
                }
            }
            solve(&w, l, r, u_next + e * mat);
            if (nmatch[e] == i) {
                const double *kk = keep + 0;
                (void)kk;
                memcpy(keep + 2 * (K_UM * E * nn) + e * mat, uc, (size_t)mat * sizeof(double));
                memcpy(keep + 2 * (K_UMM1 * E * nn) + e * mat, up, (size_t)mat * sizeof(double));
                memcpy(keep + 2 * (K_UMP1 * E * nn) + e * mat, u_next + e * mat,
                       (size_t)mat * sizeof(double));
                memcpy(keep + 2 * (K_MMM1 * E * nn) + e * mat, i > 0 ? mp : mc,
                       (size_t)mat * sizeof(double));
                memcpy(keep + 2 * (K_MMP1 * E * nn) + e * mat, mn, (size_t)mat * sizeof(double));
                if (deformed) {
                    const double *nhs[3] = {NM + 2 * (e * RN + (i + 1) * nn),
                                            NM + 2 * (e * RN + i * nn),
                                            use_m1 ? NM + 2 * (e * RN + (i - 1) * nn)
                                                   : NM + 2 * (e * RN + i * nn)};
                    for (int k = 0; k < 3; k += 2) {
                        /* s3 = fac4 * (matmul(nh3, u_next) * wt[:, 0] + prod) */
                        matmul(n, nhs[k], u_next + e * mat, s3);
                        const double wr = wt[2 * (k * npts)], wi = wt[2 * (k * npts) + 1];
                        double *dst = keep + 2 * ((k == 0 ? K_SP1 : K_SM1) * E * nn) + e * mat;
                        for (int64_t q = 0; q < nn; q++) {
                            double t[2];
                            const double sr = s3[2 * q], si = s3[2 * q + 1];
                            t[0] = sr * wr - si * wi;
                            t[1] = sr * wi + si * wr;
                            if (top) {
                                const double *p = prod + 2 * (k * E * nn) + e * mat + 2 * q;
                                t[0] = t[0] + p[0];
                                t[1] = t[1] + p[1];
                            }
                            rmul(fac[k], 0.0, t, dst + 2 * q);
                        }
                    }
                }
            }
        }
        if (any_hit)
            captured = 1;
        if (deformed) {
            double *last = hist[5];
            for (int k = 5; k > 0; k--)
                hist[k] = hist[k - 1];
            hist[0] = last;
            memcpy(hist[0], u_next, (size_t)(E * mat) * sizeof(double));
            if (nhist < 6)
                nhist++;
        }
        {
            double *t = u_prev;
            u_prev = u_cur;
            u_cur = u_next;
            u_next = t;
            t = mu_prev;
            mu_prev = mu_cur;
            mu_cur = t;
            have_mu_prev = 1;
        }
        if (i % 10 == 9) {
            /* _stabilise_blocks for B = 1 */
            int ok = 1;
            for (int64_t e = 0; e < E; e++) {
                if (qr(&w, u_cur + e * mat, qm + e * mat, rm + e * mat))
                    goto done;
            }
            double dmin = INFINITY;
            for (int64_t q = 0; q < E * mat && ok; q++)
                if (!isfinite(rm[q]))
                    ok = 0;
            if (ok) {
                for (int64_t e = 0; e < E; e++)
                    for (int a = 0; a < n; a++) {
                        const double *z = rm + e * mat + 2 * ((int64_t)a * n + a);
                        const double d = hypot(z[0], z[1]);
                        if (d < dmin || d != d)
                            dmin = d;
                    }
                ok = dmin > 0.0;
            }
            if (ok) {
                for (int64_t e = 0; e < E; e++) {
                    const double *re = rm + e * mat;
                    if (captured)
                        for (int s = 0; s < 7; s++)
                            if (s == K_UMM1 || s == K_UM || s == K_UMP1 || s == K_SP1 || s == K_SM1)
                                trsm_right(&w, re, keep + 2 * (s * E * nn) + e * mat);
                    trsm_right(&w, re, u_prev + e * mat);
                    for (int k = 0; k < nhist; k++)
                        trsm_right(&w, re, hist[k] + e * mat);
                }
                memcpy(u_cur, qm, (size_t)(E * mat) * sizeof(double));
                have_mu_prev = 0;
            }
        }
    }
    rc = 0;
done:
    free(u_prev); free(u_cur); free(u_next); free(mu_cur); free(mu_prev); free(rhs); free(lhs);
    free(tmp); free(qm); free(rm); free(s3); free(c);
    for (int k = 0; k < 6; k++)
        free(hist[k]);
    free(hstack); free(v3); free(prod);
    free(w.a); free(w.b); free(w.tau); free(w.work); free(w.piv);
    return rc;
}
