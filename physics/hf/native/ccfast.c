#define _POSIX_C_SOURCE 199309L

/* CCFAST2: the coupled-channels radial loop of one (J, parity) block, without bit-identity.
 *
 * `hfnative.c::hf_cc_block` (SPEEDT3) repeats `solver._numerov_blocks` operation for operation so
 * that its bits are the Python loop's. The project rule lifts that requirement, and this
 * kernel integrates the same discretised equations -- the same Numerov recurrence on the same grid,
 * matched at the same point -- with fewer floating-point operations:
 *
 *  1. W-form of the Numerov step. With W_i = (1 - c M_i) u_i and c = h^2 / 12 the matrix Numerov
 *     step (1 - c M_{i+1}) u_{i+1} = 2 u_i + 10 c M_i u_i - (1 - c M_{i-1}) u_{i-1} is exactly
 *         W_{i+1} = 12 u_i - 10 W_i - W_{i-1},    u_{i+1} = (1 - c M_{i+1})^-1 W_{i+1},
 *     because 2 u_i + 10 c M_i u_i = 12 u_i - 10 W_i. One LU solve per step and no M u product:
 *     ~1.7 N^3 complex flops per step instead of ~2.7 N^3.
 *  2. M(r_i) is built here from the form factors, (N x N) per step, instead of the whole
 *     (E, R, N, N) array that `solver._block_operators` allocates (133 MB for one Hf-179 block).
 *  3. Each energy stops at its own matching point instead of the batch's largest.
 *  4. The stabilisation (every `stab` steps) orthonormalises W by QR and carries the same right
 *     factor R^-1 to W_{i-1}, u_i and u_{i-1}: the columns of all four are the same solutions in
 *     the same basis, and L = U' U^-1 at the matching radius is invariant under it.
 *  5. Blocks of at most `small_n` channels skip LAPACK's call overhead (`lu_solve_small`).
 *
 * The W-form is the spherical spin-orbit case (`lo(13) = F`, E <= soswitch). Above the switch the
 * derivative coupling of the deformed spin-orbit puts step-dependent finite-difference terms into
 * the implicit matrix, which the W-form does not absorb: `cc_block_d` keeps `hf_cc_block`'s step
 * (four products and a solve) with points 2, 3 and 5.
 *
 * Storage is column-major throughout (LAPACK's), complex as interleaved (re, im) doubles. The
 * LAPACK/BLAS routines are torch's own, handed over by address (`ecis/ccnative.py`).
 * Build: scripts/build_ccfast_native.sh.
 */

#include <math.h>
#include <time.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

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
typedef void (*zgemm_t)(const char *, const char *, const int *, const int *, const int *,
                        const double *, const double *, const int *, const double *, const int *,
                        const double *, double *, const int *);

static zgetrf_t zgetrf_p;
static zgetrs_t zgetrs_p;
static zgeqrf_t zgeqrf_p;
static zungqr_t zungqr_p;
static ztrsm_t ztrsm_p;
static zgemm_t zgemm_p;

static const double ONE[2] = {1.0, 0.0};
static const double ZERO[2] = {0.0, 0.0};

int cc_version(void) { return 1; }

/* SETB: 1 when built with the split-storage solve and stabilisation (libccsplit) */
#ifdef CCFAST_SPLIT
int cc_split(void) { return 1; }
#else
int cc_split(void) { return 0; }
#endif

void cc_set_lapack(void *zgemm, void *zgetrf, void *zgetrs, void *zgeqrf, void *zungqr, void *ztrsm)
{
    zgemm_p = (zgemm_t)zgemm;
    zgetrf_p = (zgetrf_t)zgetrf;
    zgetrs_p = (zgetrs_t)zgetrs;
    zgeqrf_p = (zgeqrf_t)zgeqrf;
    zungqr_p = (zungqr_t)zungqr;
    ztrsm_p = (ztrsm_t)ztrsm;
}

static double *zalloc(int64_t count)
{
    size_t bytes = ((size_t)(count * 16) + 64 + 63) & ~(size_t)63;
    double *p = aligned_alloc(64, bytes);
    if (p)
        memset(p, 0, bytes);
    return p;
}

typedef struct {
    int64_t n, nlam, R;
    const double *central; /* (E, NLAM, R) complex */
    const double *cpl;     /* (NLAM, N, N) real, row-major */
    const double *diagr;   /* (E, R, N) real: l(l+1)/r^2 - k^2 + mu V_C */
    const double *so0;     /* (E, R) complex: the lambda = 0 spin-orbit form factor */
    const double *ls2;     /* (N,) real: 2 l.s */
    const double *mu;      /* (E,) */
} blk_t;

/* M(r_i) at energy e, column-major complex:
 *   M_ab = mu sum_lambda central[e, lambda, i] cpl[lambda, a, b]
 *        + delta_ab (diagr[e, i, a] + mu ls2[a] so0[e, i]) */
static void build_m(const blk_t *b, int64_t e, int64_t i, double *M)
{
    const int64_t n = b->n, nn = n * n;
    const double mu = b->mu[e];
    memset(M, 0, (size_t)(2 * nn) * sizeof(double));
    for (int64_t lam = 0; lam < b->nlam; lam++) {
        const double *z = b->central + 2 * ((e * b->nlam + lam) * b->R + i);
        const double sr = mu * z[0], si = mu * z[1];
        if (sr == 0.0 && si == 0.0)
            continue;
        const double *cp = b->cpl + lam * nn;
        for (int64_t a = 0; a < n; a++)
            for (int64_t c = 0; c < n; c++) {
                const double g = cp[a * n + c];
                double *m = M + 2 * (c * n + a);
                m[0] += sr * g;
                m[1] += si * g;
            }
    }
    const double *so = b->so0 + 2 * (e * b->R + i);
    const double *dr = b->diagr + (e * b->R + i) * n;
    for (int64_t a = 0; a < n; a++) {
        double *m = M + 2 * (a * n + a);
        const double f = mu * b->ls2[a];
        m[0] += dr[a] + f * so[0];
        m[1] += f * so[1];
    }
}

static void lhs_from(int64_t n, const double *M, double c, double *L)
{
    const int64_t nn2 = 2 * n * n;
    for (int64_t q = 0; q < nn2; q++)
        L[q] = -c * M[q];
    for (int64_t a = 0; a < n; a++)
        L[2 * (a * n + a)] += 1.0;
}

/* column-major src -> row-major dst (N x N complex) */
static void to_rows(int64_t n, const double *src, double *dst)
{
    for (int64_t a = 0; a < n; a++)
        for (int64_t c = 0; c < n; c++) {
            dst[2 * (a * n + c)] = src[2 * (c * n + a)];
            dst[2 * (a * n + c) + 1] = src[2 * (c * n + a) + 1];
        }
}

/* A X = B for n right-hand sides, column-major, in place (B <- X, A <- its LU): partial pivoting,
 * right-looking, no blocking. For the smallest blocks MKL's call overhead is a visible part of a
 * zgetrf + zgetrs; 1 - c M is strongly diagonally dominant, so the textbook elimination is as
 * accurate. */
static void lu_solve_small(int64_t n, double *A, double *B)
{
    for (int64_t k = 0; k < n; k++) {
        const double *col = A + 2 * k * n;
        int64_t p = k;
        double best = col[2 * k] * col[2 * k] + col[2 * k + 1] * col[2 * k + 1];
        for (int64_t i = k + 1; i < n; i++) {
            const double v = col[2 * i] * col[2 * i] + col[2 * i + 1] * col[2 * i + 1];
            if (v > best) {
                best = v;
                p = i;
            }
        }
        if (p != k) {
            for (int64_t j = 0; j < n; j++) {
                double *x = A + 2 * (j * n + k), *y = A + 2 * (j * n + p);
                double t0 = x[0], t1 = x[1];
                x[0] = y[0]; x[1] = y[1]; y[0] = t0; y[1] = t1;
                x = B + 2 * (j * n + k); y = B + 2 * (j * n + p);
                t0 = x[0]; t1 = x[1];
                x[0] = y[0]; x[1] = y[1]; y[0] = t0; y[1] = t1;
            }
        }
        double *ck = A + 2 * k * n;
        const double pr = ck[2 * k], pi = ck[2 * k + 1];
        const double den = pr * pr + pi * pi;
        const double ir = pr / den, ii = -pi / den; /* 1 / pivot */
        for (int64_t i = k + 1; i < n; i++) {
            const double ar = ck[2 * i], ai = ck[2 * i + 1];
            ck[2 * i] = ar * ir - ai * ii;
            ck[2 * i + 1] = ar * ii + ai * ir;
        }
        for (int64_t j = k + 1; j < n; j++) {
            double *cj = A + 2 * j * n;
            const double ur = cj[2 * k], ui = cj[2 * k + 1];
            if (ur == 0.0 && ui == 0.0)
                continue;
            for (int64_t i = k + 1; i < n; i++) {
                const double lr = ck[2 * i], li = ck[2 * i + 1];
                cj[2 * i] -= lr * ur - li * ui;
                cj[2 * i + 1] -= lr * ui + li * ur;
            }
        }
        /* forward substitution of every right-hand side through this column */
        for (int64_t j = 0; j < n; j++) {
            double *bj = B + 2 * j * n;
            const double br = bj[2 * k], bi = bj[2 * k + 1];
            if (br == 0.0 && bi == 0.0)
                continue;
            for (int64_t i = k + 1; i < n; i++) {
                const double lr = ck[2 * i], li = ck[2 * i + 1];
                bj[2 * i] -= lr * br - li * bi;
                bj[2 * i + 1] -= lr * bi + li * br;
            }
        }
    }
    for (int64_t k = n - 1; k >= 0; k--) {
        const double *ck = A + 2 * k * n;
        const double pr = ck[2 * k], pi = ck[2 * k + 1];
        const double den = pr * pr + pi * pi;
        const double ir = pr / den, ii = -pi / den;
        for (int64_t j = 0; j < n; j++) {
            double *bj = B + 2 * j * n;
            const double br = bj[2 * k], bi = bj[2 * k + 1];
            const double xr = br * ir - bi * ii, xi = br * ii + bi * ir;
            bj[2 * k] = xr;
            bj[2 * k + 1] = xi;
            if (xr == 0.0 && xi == 0.0)
                continue;
            for (int64_t i = 0; i < k; i++) {
                const double ur = ck[2 * i], ui = ck[2 * i + 1];
                bj[2 * i] -= ur * xr - ui * xi;
                bj[2 * i + 1] -= ur * xi + ui * xr;
            }
        }
    }
}

#if defined(__aarch64__)
/* channel count up to which `lu_solve_small` replaces zgetrf/zgetrs. Measured per platform on real
 * dense blocks: against x86 MKL (laptop) it ties at N = 12-15 and loses above (N = 70: 160 against
 * 93 ms per Hf-179 block); against Accelerate (Mac M2) it wins up to N ~ 50 (N = 15: 2.6 against
 * 3.7 ms, N = 45: 44 against 48 ms) and loses at N = 70 (175 against 163 ms). */
static int64_t small_n = 48;
#else
static int64_t small_n = 12;
#endif

void cc_set_small_n(int64_t n) { small_n = n; }

#ifdef CCFAST_SPLIT
/* SETB: split-storage solve and stabilisation (ccsplit.h, included below; libccsplit) */
static void solve_split(int64_t N, double *A, double *B, int *piv);
static void stabilise_split(double *Q, double **others, int k, int64_t N);
#endif

static int nm_solve_z(int64_t N, const double *A, double *B);

static void solve_n(int64_t N, double *A, double *B, int *piv)
{
    if (nm_solve_z(N, A, B) == 0) /* NATIVEX2 ccx: Jacobi sweeps where they are cheaper */
        return;
#ifdef CCFAST_SPLIT
    solve_split(N, A, B, piv);
    return;
#endif
    if (N <= small_n) {
        lu_solve_small(N, A, B);
        return;
    }
    const int n = (int)N;
    int info = 0;
    zgetrf_p(&n, &n, A, &n, piv, &info);
    zgetrs_p("N", &n, &n, A, &n, piv, B, &n, &info);
}

/* NATIVEX2 ccx: complex products as four real ones. Accelerate runs a real N x N x N product on the
 * M2's matrix block ~14x faster than the complex one (N = 56: dgemm 1.5 us, zgemm 20.7 us; N = 32:
 * 0.5 against 9.3), so on arm64 C = A B is (Ar Br - Ai Bi) + i (Ar Bi + Ai Br), and a real A (the
 * derivative-coupling matrices) takes two. `cc_set_dgemm` hands the routine over (torch's own, by
 * address, as `cc_set_lapack`); `cc_set_real_gemm` switches the path. Off on x86 (not measured). */
typedef void (*dgemm_t)(const char *, const char *, const int *, const int *, const int *,
                        const double *, const double *, const int *, const double *, const int *,
                        const double *, double *, const int *);
static dgemm_t dgemm_p;
#if defined(__aarch64__)
static int dg_on = 1;
#else
static int dg_on = 0;
#endif

void cc_set_dgemm(void *f) { dgemm_p = (dgemm_t)f; }
void cc_set_real_gemm(int64_t on) { dg_on = (int)on; }

static int use_dgemm(void) { return dg_on && dgemm_p != NULL; }

typedef struct {
    int64_t cap;
    double *buf;
} ws_t;

static _Thread_local ws_t mm_ws = {0, NULL}, nm_ws = {0, NULL}, nz_ws = {0, NULL};

/* `count` doubles of per-thread scratch, grown on demand (never freed: one per worker thread) */
static double *ws_get(ws_t *w, int64_t count)
{
    if (count > w->cap) {
        free(w->buf);
        size_t bytes = ((size_t)count * sizeof(double) + 63) & ~(size_t)63;
        w->buf = aligned_alloc(64, bytes);
        w->cap = w->buf ? count : 0;
    }
    return w->buf;
}

/* C = A B on split column-major N x N complex matrices; `a_real`: Ai is zero */
static void dmm_split(int64_t N, const double *ar, const double *ai, const double *br,
                      const double *bi, double *cr, double *ci, int a_real)
{
    const int n = (int)N;
    const double one = 1.0, zero = 0.0, mone = -1.0;
    dgemm_p("N", "N", &n, &n, &n, &one, ar, &n, br, &n, &zero, cr, &n);
    dgemm_p("N", "N", &n, &n, &n, &one, ar, &n, bi, &n, &zero, ci, &n);
    if (!a_real) {
        dgemm_p("N", "N", &n, &n, &n, &mone, ai, &n, bi, &n, &one, cr, &n);
        dgemm_p("N", "N", &n, &n, &n, &one, ai, &n, br, &n, &one, ci, &n);
    }
}

/* CCNUMEROV: ECIS's modified Numerov (`ecist.f::inch`).  The coupled step becomes explicit --
 *     u_{i+1} = 2 u_i - u_{i-1} + 12 c M_i u_i + 12 c^2 M_i (M_i u_i),   c = h^2/12,
 * the truncation of 2(cosh kh - 1) = T + T^2/12 + T^3/360 + ... after two terms, with T = h^2 M --
 * so the factorise-and-solve of the W-form is replaced by a second matrix product and the port
 * sits on ECIS's own discretisation instead of the plain Numerov's (opposite-signed h^6 error,
 * ecis-113/ecis-114).  `cc_set_modnum(0)` restores the W-form: the A/B lever. */
static int modnum_on = 1;

void cc_set_modnum(int64_t on) { modnum_on = (int)on; }

/* C = A B on split column-major complex matrices, without needing torch's dgemm */
#ifdef CCFAST_SPLIT
static void mm_split(int64_t N, const double *ar, const double *ai, const double *br,
                     const double *bi, double *cr, double *ci)
{
    const int64_t nn = N * N;
    if (N >= 12 && use_dgemm()) {
        dmm_split(N, ar, ai, br, bi, cr, ci, 0);
        return;
    }
    memset(cr, 0, (size_t)nn * sizeof(double));
    memset(ci, 0, (size_t)nn * sizeof(double));
    for (int64_t j = 0; j < N; j++) {
        double *restrict cjr = cr + j * N, *restrict cji = ci + j * N;
        for (int64_t k = 0; k < N; k++) {
            const double x = br[j * N + k], y = bi[j * N + k];
            if (x == 0.0 && y == 0.0)
                continue;
            const double *restrict akr = ar + k * N, *restrict aki = ai + k * N;
            for (int64_t q = 0; q < N; q++) {
                cjr[q] += akr[q] * x - aki[q] * y;
                cji[q] += akr[q] * y + aki[q] * x;
            }
        }
    }
}
#endif

/* C = A B, column-major complex, A and B dense */
#if defined(__aarch64__)
static int64_t gemm_small = 16; /* up to this N the triple loop replaces zgemm (Accelerate: N = 15
                                 * 3.5 -> 3.2 ms per deformed block; worse from N = 24) */
#else
static int64_t gemm_small = 0; /* x86 MKL is faster on dense blocks from N = 12 up */
#endif

void cc_set_gemm_small(int64_t n) { gemm_small = n; }

static void mm(int64_t N, const double *A, const double *B, double *C)
{
    if (N >= 24 && use_dgemm()) { /* below, the packing outweighs the faster product */
        const int64_t nn = N * N;
        double *s = ws_get(&mm_ws, 6 * nn);
        if (s) {
            double *ar = s, *ai = s + nn, *br = s + 2 * nn, *bi = s + 3 * nn, *cr = s + 4 * nn,
                   *ci = s + 5 * nn;
            double any = 0.0;
            for (int64_t q = 0; q < nn; q++) {
                ar[q] = A[2 * q];
                ai[q] = A[2 * q + 1];
                any += fabs(A[2 * q + 1]);
                br[q] = B[2 * q];
                bi[q] = B[2 * q + 1];
            }
            dmm_split(N, ar, ai, br, bi, cr, ci, any == 0.0);
            for (int64_t q = 0; q < nn; q++) {
                C[2 * q] = cr[q];
                C[2 * q + 1] = ci[q];
            }
            return;
        }
    }
    if (N > gemm_small) {
        const int n = (int)N;
        zgemm_p("N", "N", &n, &n, &n, ONE, A, &n, B, &n, ZERO, C, &n);
        return;
    }
    memset(C, 0, (size_t)(2 * N * N) * sizeof(double));
    for (int64_t j = 0; j < N; j++) {
        double *cj = C + 2 * j * N;
        const double *bj = B + 2 * j * N;
        for (int64_t k = 0; k < N; k++) {
            const double br = bj[2 * k], bi = bj[2 * k + 1];
            if (br == 0.0 && bi == 0.0)
                continue;
            const double *ak = A + 2 * k * N;
            for (int64_t i = 0; i < N; i++) {
                cj[2 * i] += ak[2 * i] * br - ak[2 * i + 1] * bi;
                cj[2 * i + 1] += ak[2 * i] * bi + ak[2 * i + 1] * br;
            }
        }
    }
}

/* NATIVEX2 ccx: Jacobi sweeps in place of the elimination. The implicit Numerov matrix
 * L = 1 - c M is diagonal to a part in 1e2 at most and usually far less (the deformed couplings
 * against the diagonal: on Lu-175 and U-238 the infinity norm of D^-1 O, O = L - D, is below 1e-4 on
 * 2/3 of the steps, below 1e-8 on 1/3, never above 1.1e-2). There L X = W is Jacobi's fixed point
 * X = D^-1 (W - O X): from X = D^-1 W, p sweeps leave a truncation below rho^(p+1) |X| (rho the
 * norm, bounded from the off-diagonal row sums of |Re| + |Im|). A sweep is one product, which the
 * real path above makes ~10x cheaper than the elimination at N = 56. A step takes p sweeps when
 * rho^(p+1) <= `nm_tol` for p within the budget that is cheaper than the elimination at its N,
 * and the elimination otherwise. Every sweep recomputes X from W, so rounding does not
 * accumulate. Off by default on x86 (not measured against MKL); `cc_set_neumann` sets both. */
#if defined(__aarch64__)
static int nm_on = 1;
#else
static int nm_on = 0;
#endif
static double nm_tol = 1.0e-13;

void cc_set_neumann(int64_t on, double tol)
{
    nm_on = (int)on;
    nm_tol = tol;
}

/* sweeps cheaper than one elimination at N */
static int nm_budget(int64_t N)
{
    if (use_dgemm()) {
        /* Accelerate, M2, real products: one elimination against a sweep (four dgemm and the
         * update) is N = 16 2.3 : 0.9 us, 24 6.9 : 2.0, 32 14.2 : 2.4, 48 44 : 4.8, 56 70 : 8.4,
         * 64 102 : 10, 72 145 : 15 (the matrix block favours multiples of 16); below N = 24 the
         * row sums and the packing eat the margin (Pd-106, N <= 19: 84 against 109 ms) */
        if (N >= 64)
            return 9;
        if (N >= 48)
            return 7;
        if (N >= 32)
            return 5;
        if (N >= 24)
            return 3;
        return 0;
    }
    if (N >= 64) /* complex products (sp_solve against zgemm: 1.7 at N = 8 ... 6.1 at N = 72) */
        return 5;
    if (N >= 30)
        return 3;
    if (N >= 24)
        return 2;
    if (N >= 12)
        return 1;
    return 0;
}

/* the sweep count for the diagonal (dr, di) and the off-diagonal row sums, or -1 */
static int nm_order(int64_t N, const double *dr, const double *di, const double *s)
{
    double rho = 0.0;
    for (int64_t i = 0; i < N; i++) {
        const double d2 = dr[i] * dr[i] + di[i] * di[i];
        const double q = s[i] * s[i] / d2;
        if (!(q < 1.0))
            return -1;
        if (q > rho)
            rho = q;
    }
    rho = sqrt(rho);
    const int budget = nm_budget(N);
    double pw = rho;
    for (int p = 0; p <= budget; p++) {
        if (pw <= nm_tol)
            return p;
        pw *= rho;
    }
    return -1;
}

/* X <- L^-1 W by the sweeps, all split column-major: (lr, li) = L, (wr, wi) = W, X into (xr, xi).
 * With the real products the sweep is X <- G - F X, F = D^-1 O and G = D^-1 W formed once, so a
 * sweep is a copy of G and four products (beta = 1) and nothing elementwise; F overwrites L, whose
 * diagonal and off-diagonal are put back only when the elimination has to take over. Returns -1
 * (X not written) when the elimination is cheaper or needed; L is intact then. */
static int nm_solve_split(int64_t N, double *restrict lr, double *restrict li, const double *wr,
                          const double *wi, double *restrict xr, double *restrict xi)
{
    if (!nm_on || nm_budget(N) <= 0)
        return -1;
    const int64_t nn = N * N;
    const int real = use_dgemm();
    double *s = ws_get(&nm_ws, (real ? 4 : 8) * nn + 5 * N);
    if (!s)
        return -1;
    double *const orr = lr, *const oi = li, *tr = s, *ti = s + nn;
    double *dr = s + (real ? 4 : 8) * nn, *di = dr + N, *sum = dr + 2 * N, *ir = dr + 3 * N,
           *ii = dr + 4 * N;
    for (int64_t i = 0; i < N; i++) {
        dr[i] = orr[i * N + i];
        di[i] = oi[i * N + i];
        orr[i * N + i] = oi[i * N + i] = 0.0;
        sum[i] = 0.0;
    }
    for (int64_t k = 0; k < N; k++) {
        const double *restrict a = orr + k * N, *restrict b = oi + k * N;
        for (int64_t i = 0; i < N; i++)
            sum[i] += fabs(a[i]) + fabs(b[i]);
    }
    const int p = nm_order(N, dr, di, sum);
    if (p < 0) {
        for (int64_t i = 0; i < N; i++) {
            orr[i * N + i] = dr[i];
            oi[i * N + i] = di[i];
        }
        return -1;
    }
    for (int64_t i = 0; i < N; i++) {
        const double d2 = dr[i] * dr[i] + di[i] * di[i];
        ir[i] = dr[i] / d2;
        ii[i] = -di[i] / d2;
    }
    if (real) {
        /* G into the output of the last sweep, F = D^-1 O in place of L */
        double *gr = tr + 2 * nn, *gi = tr + 3 * nn; /* s + 2 nn, s + 3 nn: G */
        for (int64_t j = 0; j < N; j++) {
            const double *restrict a = wr + j * N, *restrict b = wi + j * N;
            double *restrict yr = gr + j * N, *restrict yi = gi + j * N;
            double *restrict fr = orr + j * N, *restrict fi = oi + j * N;
            for (int64_t i = 0; i < N; i++) {
                yr[i] = a[i] * ir[i] - b[i] * ii[i];
                yi[i] = a[i] * ii[i] + b[i] * ir[i];
                const double u = fr[i], v = fi[i];
                fr[i] = u * ir[i] - v * ii[i];
                fi[i] = u * ii[i] + v * ir[i];
            }
        }
        /* sweeps alternate between (xr, xi) and (tr, ti) so that the last lands in X */
        double *cr[2] = {xr, tr}, *ci[2] = {xi, ti};
        int cur = p % 2 == 0 ? 0 : 1; /* holds X_0 = G */
        memcpy(cr[cur], gr, (size_t)nn * sizeof(double));
        memcpy(ci[cur], gi, (size_t)nn * sizeof(double));
        const int n = (int)N;
        const double one = 1.0, mone = -1.0;
        for (int sw = 0; sw < p; sw++) {
            const int nxt = 1 - cur;
            memcpy(cr[nxt], gr, (size_t)nn * sizeof(double));
            memcpy(ci[nxt], gi, (size_t)nn * sizeof(double));
            /* X' = G - (Fr + i Fi)(Xr + i Xi) */
            dgemm_p("N", "N", &n, &n, &n, &mone, orr, &n, cr[cur], &n, &one, cr[nxt], &n);
            dgemm_p("N", "N", &n, &n, &n, &one, oi, &n, ci[cur], &n, &one, cr[nxt], &n);
            dgemm_p("N", "N", &n, &n, &n, &mone, orr, &n, ci[cur], &n, &one, ci[nxt], &n);
            dgemm_p("N", "N", &n, &n, &n, &mone, oi, &n, cr[cur], &n, &one, ci[nxt], &n);
            cur = nxt;
        }
        return 0; /* L now holds F: the caller does not read it again */
    }
    double *z = s + 2 * nn; /* interleaved O, X, O X for the complex product */
    for (int64_t q = 0; q < nn; q++) {
        z[2 * q] = orr[q];
        z[2 * q + 1] = oi[q];
    }
    for (int64_t j = 0; j < N; j++) {
        const double *a = wr + j * N, *b = wi + j * N;
        double *restrict yr = xr + j * N, *restrict yi = xi + j * N;
        for (int64_t i = 0; i < N; i++) {
            yr[i] = a[i] * ir[i] - b[i] * ii[i];
            yi[i] = a[i] * ii[i] + b[i] * ir[i];
        }
    }
    for (int sw = 0; sw < p; sw++) {
        for (int64_t q = 0; q < nn; q++) {
            z[2 * nn + 2 * q] = xr[q];
            z[2 * nn + 2 * q + 1] = xi[q];
        }
        mm(N, z, z + 2 * nn, z + 4 * nn);
        for (int64_t q = 0; q < nn; q++) {
            tr[q] = z[4 * nn + 2 * q];
            ti[q] = z[4 * nn + 2 * q + 1];
        }
        for (int64_t j = 0; j < N; j++) {
            const double *a = wr + j * N, *b = wi + j * N, *c = tr + j * N, *d = ti + j * N;
            double *restrict yr = xr + j * N, *restrict yi = xi + j * N;
            for (int64_t i = 0; i < N; i++) {
                const double u = a[i] - c[i], v = b[i] - d[i];
                yr[i] = u * ir[i] - v * ii[i];
                yi[i] = u * ii[i] + v * ir[i];
            }
        }
    }
    for (int64_t i = 0; i < N; i++) {
        orr[i * N + i] = dr[i];
        oi[i * N + i] = di[i];
    }
    return 0;
}

/* the same on interleaved column-major L = A and B (B <- X, A untouched) */
static int nm_solve_z(int64_t N, const double *A, double *B)
{
    if (!nm_on || nm_budget(N) <= 0)
        return -1;
    const int64_t nn = N * N;
    double *s = ws_get(&nz_ws, 6 * nn);
    if (!s)
        return -1;
    double *lr = s, *li = s + nn, *wr = s + 2 * nn, *wi = s + 3 * nn, *xr = s + 4 * nn,
           *xi = s + 5 * nn;
    for (int64_t q = 0; q < nn; q++) {
        lr[q] = A[2 * q];
        li[q] = A[2 * q + 1];
        wr[q] = B[2 * q];
        wi[q] = B[2 * q + 1];
    }
    if (nm_solve_split(N, lr, li, wr, wi, xr, xi) != 0)
        return -1;
    for (int64_t q = 0; q < nn; q++) {
        B[2 * q] = xr[q];
        B[2 * q + 1] = xi[q];
    }
    return 0;
}


typedef struct {
    int n, lwork;
    double *A, *tau, *work;
} qr_ws_t;

static int qr_ws_init(qr_ws_t *w, int64_t N)
{
    const int n = (int)N;
    int info = 0, lwork = -1;
    double q1[2], q2[2];
    w->n = n;
    w->A = zalloc(N * N);
    w->tau = zalloc(N);
    w->work = NULL;
    if (!w->A || !w->tau)
        return -1;
    zgeqrf_p(&n, &n, w->A, &n, w->tau, q1, &lwork, &info);
    zungqr_p(&n, &n, &n, w->A, &n, w->tau, q2, &lwork, &info);
    w->lwork = (int)(q1[0] > q2[0] ? q1[0] : q2[0]);
    if (w->lwork < 1)
        w->lwork = 1;
    w->work = zalloc(w->lwork);
    return w->work ? 0 : -1;
}

static void qr_ws_free(qr_ws_t *w)
{
    free(w->A);
    free(w->tau);
    free(w->work);
}

/* `solver._stabilise`: Q R = Q_in (Householder), Q_in <- Q and every matrix in `others` <- X R^-1,
 * so all of them hold the same solutions in the same new basis. Skipped when R has a zero or
 * non-finite diagonal. (A modified Gram-Schmidt carrying the column operations along was tried and
 * is ~2x slower at N = 65: its inner loops over four interleaved-complex matrices do not vectorise.) */
static void stabilise(qr_ws_t *w, double *Q, double **others, int k)
{
#ifdef CCFAST_SPLIT
    stabilise_split(Q, others, k, w->n);
    return;
#endif
    const int n = w->n;
    const int64_t N = n;
    int info = 0;
    memcpy(w->A, Q, (size_t)(2 * N * N) * sizeof(double));
    zgeqrf_p(&n, &n, w->A, &n, w->tau, w->work, &w->lwork, &info);
    if (info != 0)
        return;
    for (int64_t a = 0; a < N; a++) {
        const double dr = w->A[2 * (a * N + a)], di = w->A[2 * (a * N + a) + 1];
        if (!isfinite(dr) || !isfinite(di) || (dr == 0.0 && di == 0.0))
            return;
    }
    for (int m = 0; m < k; m++)
        ztrsm_p("R", "U", "N", "N", &n, &n, ONE, w->A, &n, others[m], &n);
    zungqr_p(&n, &n, &n, w->A, &n, w->tau, w->work, &w->lwork, &info);
    memcpy(Q, w->A, (size_t)(2 * N * N) * sizeof(double));
}

enum { K_UMM1, K_UM, K_UMP1, K_MMM1, K_MMP1, K_SP1, K_SM1 };

#ifdef CCFAST_SPLIT
#include "ccsplit.h"
#endif

/* One block, every energy. Inputs as `blk_t`, plus
 *   u1     : (E, N, N) complex row-major, the solutions at r_1
 *   h      : (E,) step; nmatch: (E,) matching index; stab: steps between two stabilisations
 *   keep   : (7, E, N, N) complex row-major output (sp1/sm1 left as the caller zeroed them)
 * Returns 0; -1 out of memory; -2 the radial axis is shorter than a matching point needs. */
/* CCNUMEROV: `cc_block_w`'s loop with ECIS's modified Numerov step.  No implicit matrix, so no
 * LU per step and no W: two products of M(r_i) instead, and the stabilisation orthonormalises the
 * solutions themselves.  Same arguments and return codes as `cc_block_w`. */
static int cc_block_mn(int64_t E, int64_t N, int64_t R, int64_t NLAM, const double *central,
                       const double *cpl, const double *diagr, const double *so0,
                       const double *ls2, const double *mu, const double *u1, const double *h,
                       const int64_t *nmatch, int64_t stab, double *keep)
{
    const int64_t nn = N * N, mat = 2 * nn;
    blk_t b = {N, NLAM, R, central, cpl, diagr, so0, ls2, mu};
    int rc = -1;
    double *up = zalloc(nn), *uc = zalloc(nn), *un = zalloc(nn);
    double *y = zalloc(nn), *z = zalloc(nn), *M = zalloc(nn);
    qr_ws_t qw = {0, 0, NULL, NULL, NULL};
    if (!up || !uc || !un || !y || !z || !M || qr_ws_init(&qw, N))
        goto done;
    if (stab < 1)
        stab = 1;
    for (int64_t e = 0; e < E; e++) {
        const int64_t nm = nmatch[e];
        if (nm + 2 > R) {
            rc = -2;
            goto done;
        }
        const double c = h[e] * h[e] / 12.0, c12 = 12.0 * c, c144 = c12 * c;
        for (int64_t a = 0; a < N; a++)
            for (int64_t k = 0; k < N; k++) {
                uc[2 * (k * N + a)] = u1[2 * ((e * N + a) * N + k)];
                uc[2 * (k * N + a) + 1] = u1[2 * ((e * N + a) * N + k) + 1];
            }
        memset(up, 0, (size_t)mat * sizeof(double));
        build_m(&b, e, 0, M);
        for (int64_t i = 0; i <= nm; i++) {
            mm(N, M, uc, y);
            mm(N, M, y, z);
            for (int64_t q = 0; q < mat; q++)
                un[q] = 2.0 * uc[q] - up[q] + c12 * y[q] + c144 * z[q];
            if (i == nm) {
                to_rows(N, uc, keep + 2 * (K_UM * E * nn) + e * mat);
                to_rows(N, up, keep + 2 * (K_UMM1 * E * nn) + e * mat);
                to_rows(N, un, keep + 2 * (K_UMP1 * E * nn) + e * mat);
                build_m(&b, e, i + 1, M);
                to_rows(N, M, keep + 2 * (K_MMP1 * E * nn) + e * mat);
                build_m(&b, e, i > 0 ? i - 1 : 0, M);
                to_rows(N, M, keep + 2 * (K_MMM1 * E * nn) + e * mat);
                break;
            }
            double *t = up;
            up = uc;
            uc = un;
            un = t;
            build_m(&b, e, i + 1, M);
            if (i % stab == stab - 1) {
                double *oth[1] = {up};
                stabilise(&qw, uc, oth, 1);
            }
        }
    }
    rc = 0;
done:
    free(up); free(uc); free(un); free(y); free(z); free(M);
    qr_ws_free(&qw);
    return rc;
}


int cc_block_w(int64_t E, int64_t N, int64_t R, int64_t NLAM, const double *central,
               const double *cpl, const double *diagr, const double *so0, const double *ls2,
               const double *mu, const double *u1, const double *h, const int64_t *nmatch,
               int64_t stab, double *keep)
{
#ifdef CCFAST_SPLIT
    if (modnum_on)
        return cc_block_mn_split(E, N, R, NLAM, central, cpl, diagr, so0, ls2, mu, u1, h, nmatch,
                                 stab, keep);
    return cc_block_w_split(E, N, R, NLAM, central, cpl, diagr, so0, ls2, mu, u1, h, nmatch, stab,
                            keep);
#endif
    if (modnum_on)
        return cc_block_mn(E, N, R, NLAM, central, cpl, diagr, so0, ls2, mu, u1, h, nmatch, stab,
                           keep);
    const int64_t nn = N * N, mat = 2 * nn;
    blk_t b = {N, NLAM, R, central, cpl, diagr, so0, ls2, mu};
    int rc = -1;
    double *Wp = zalloc(nn), *Wc = zalloc(nn), *Wn = zalloc(nn);
    double *up = zalloc(nn), *uc = zalloc(nn), *un = zalloc(nn);
    double *L = zalloc(nn), *M = zalloc(nn);
    int *piv = malloc(sizeof(int) * (size_t)N);
    qr_ws_t qw = {0, 0, NULL, NULL, NULL};
    if (!Wp || !Wc || !Wn || !up || !uc || !un || !L || !M || !piv || qr_ws_init(&qw, N))
        goto done;
    if (stab < 1)
        stab = 1;
    for (int64_t e = 0; e < E; e++) {
        const int64_t nm = nmatch[e];
        if (nm + 2 > R) {
            rc = -2;
            goto done;
        }
        const double c = h[e] * h[e] / 12.0;
        /* u_0 (row-major diagonal in the caller) to column-major; u_{-1} = W_{-1} = 0 */
        for (int64_t a = 0; a < N; a++)
            for (int64_t k = 0; k < N; k++) {
                uc[2 * (k * N + a)] = u1[2 * ((e * N + a) * N + k)];
                uc[2 * (k * N + a) + 1] = u1[2 * ((e * N + a) * N + k) + 1];
            }
        memset(up, 0, (size_t)mat * sizeof(double));
        memset(Wp, 0, (size_t)mat * sizeof(double));
        build_m(&b, e, 0, M);
        lhs_from(N, M, c, L);
        mm(N, L, uc, Wc);
        for (int64_t i = 0; i <= nm; i++) {
            for (int64_t q = 0; q < mat; q++)
                Wn[q] = 12.0 * uc[q] - 10.0 * Wc[q] - Wp[q];
            build_m(&b, e, i + 1, M);
            lhs_from(N, M, c, L);
            memcpy(un, Wn, (size_t)mat * sizeof(double));
            solve_n(N, L, un, piv);
            if (i == nm) {
                to_rows(N, uc, keep + 2 * (K_UM * E * nn) + e * mat);
                to_rows(N, up, keep + 2 * (K_UMM1 * E * nn) + e * mat);
                to_rows(N, un, keep + 2 * (K_UMP1 * E * nn) + e * mat);
                to_rows(N, M, keep + 2 * (K_MMP1 * E * nn) + e * mat);
                build_m(&b, e, i > 0 ? i - 1 : 0, M);
                to_rows(N, M, keep + 2 * (K_MMM1 * E * nn) + e * mat);
                break;
            }
            double *t = Wp;
            Wp = Wc;
            Wc = Wn;
            Wn = t;
            t = up;
            up = uc;
            uc = un;
            un = t;
            if (i % stab == stab - 1) {
                double *oth[3] = {Wp, uc, up};
                stabilise(&qw, Wc, oth, 3);
            }
        }
    }
    rc = 0;
done:
    free(Wp); free(Wc); free(Wn); free(up); free(uc); free(un);
    free(L); free(M); free(piv);
    qr_ws_free(&qw);
    return rc;
}


/* ------------------------------------------------------- above soswitch: derivative coupling */

typedef struct {
    blk_t base;
    const double *so_grad; /* (E, NLAM, R) real */
    const double *so_r2;   /* (E, NLAM, R) real */
    const double *so1c, *so2c, *sodc; /* (NLAM, N, N) real, row-major */
} blkd_t;

/* add f * T (T real row-major N x N) to column-major complex M */
static void add_real(int64_t n, const double *T, double f, double *M)
{
    if (f == 0.0)
        return;
    for (int64_t a = 0; a < n; a++)
        for (int64_t c = 0; c < n; c++)
            M[2 * (c * n + a)] += f * T[a * n + c];
}

/* M(r_i) with the deformed spin-orbit terms, and nh(r_i), the matrix of r du/dr */
static void build_md(const blkd_t *d, int64_t e, int64_t i, double *M, double *NH)
{
    const blk_t *b = &d->base;
    const int64_t n = b->n, nn = n * n, R = b->R;
    const double mu = b->mu[e];
    build_m(b, e, i, M);
    memset(NH, 0, (size_t)(2 * nn) * sizeof(double));
    for (int64_t lam = 0; lam < b->nlam; lam++) {
        const double g = d->so_grad[(e * b->nlam + lam) * R + i];
        const double q = d->so_r2[(e * b->nlam + lam) * R + i];
        add_real(n, d->so1c + lam * nn, mu * g, M);
        add_real(n, d->so2c + lam * nn, mu * q, M);
        add_real(n, d->sodc + lam * nn, mu * q, NH);
    }
}

/* The derivative-coupling block loop, `solver._numerov_blocks` with `nm` (ECIS lo(13) = T), one
 * block, every energy, each stopped at its own matching point: the implicit Numerov step with
 * r du/dr written on the one-sided 7-point stencil (`solver._fd_weights`).
 *   fdw: the real parts of `_fd_weights(npts)` for npts = 3..7, each (3, npts) row-major, concatenated
 * Other arguments as `cc_block_w`. CCBLOCKD: this is the A arm, kept verbatim as the accuracy
 * reference; `cc_block_d` below is the one the port calls (`HF_CCBLOCKD=0` selects this one). */
static int cc_block_d_ref(int64_t E, int64_t N, int64_t R, int64_t NLAM, const double *central,
               const double *cpl, const double *diagr, const double *so0, const double *ls2,
               const double *mu, const double *so_grad, const double *so_r2, const double *so1c,
               const double *so2c, const double *sodc, const double *fdw, const double *u1,
               const double *h, const int64_t *nmatch, int64_t stab, double *keep)
{
    static const int64_t off[5] = {0, 9, 21, 36, 54};
    const int64_t nn = N * N, mat = 2 * nn;
    blkd_t d = {{N, NLAM, R, central, cpl, diagr, so0, ls2, mu}, so_grad, so_r2, so1c, so2c, sodc};
    int rc = -1;
    double *hist[6] = {0};
    double *Mp = zalloc(nn), *Mc = zalloc(nn), *Mn = zalloc(nn);
    double *NHp = zalloc(nn), *NHc = zalloc(nn), *NHn = zalloc(nn);
    double *mu_c = zalloc(nn), *mu_p = zalloc(nn), *rhs = zalloc(nn), *L = zalloc(nn);
    double *v3 = zalloc(3 * nn), *prod = zalloc(3 * nn), *s3 = zalloc(nn), *un = zalloc(nn);
    int *piv = malloc(sizeof(int) * (size_t)N);
    qr_ws_t qw = {0, 0, NULL, NULL, NULL};
    for (int k = 0; k < 6; k++)
        hist[k] = zalloc(nn);
    if (!Mp || !Mc || !Mn || !NHp || !NHc || !NHn || !mu_c || !mu_p || !rhs || !L || !v3 || !prod ||
        !s3 || !un || !piv || qr_ws_init(&qw, N) || !hist[0] || !hist[1] || !hist[2] || !hist[3] ||
        !hist[4] || !hist[5])
        goto done;
    if (stab < 1)
        stab = 1;
    for (int64_t e = 0; e < E; e++) {
        const int64_t nm = nmatch[e];
        if (nm + 2 > R) {
            rc = -2;
            goto done;
        }
        const double c = h[e] * h[e] / 12.0;
        double *u0 = hist[0];
        for (int64_t a = 0; a < N; a++)
            for (int64_t k = 0; k < N; k++) {
                u0[2 * (k * N + a)] = u1[2 * ((e * N + a) * N + k)];
                u0[2 * (k * N + a) + 1] = u1[2 * ((e * N + a) * N + k) + 1];
            }
        int nhist = 1, have_mu_p = 0;
        build_md(&d, e, 0, Mc, NHc);
        for (int64_t i = 0; i <= nm; i++) {
            const int use_m1 = i != 0;
            const int npts = i + 3 < 7 ? (int)(i + 3) : 7;
            const double *w = fdw + off[npts - 3];
            const int top = npts - 1 < nhist ? npts - 1 : nhist;
            const double fac[3] = {(double)i + 2.0, 10.0 * ((double)i + 1.0),
                                   use_m1 ? (double)i : 0.0};
            const double *uc = hist[0], *up = nhist > 1 ? hist[1] : NULL;
            build_md(&d, e, i + 1, Mn, NHn);
            const double *nh3[3] = {NHn, NHc, use_m1 ? NHp : NHc};
            /* rhs = 2 (u_i + 5 c M_i u_i) - (u_{i-1} - c M_{i-1} u_{i-1}) */
            mm(N, Mc, uc, mu_c);
            for (int64_t q = 0; q < mat; q++)
                rhs[q] = 2.0 * uc[q] + 10.0 * c * mu_c[q];
            if (use_m1) {
                if (!have_mu_p)
                    mm(N, Mp, up, mu_p);
                for (int64_t q = 0; q < mat; q++)
                    rhs[q] -= up[q] - c * mu_p[q];
            }
            /* v3_k = sum_{m=1..top} w[k, m] u_{i+1-m};  rhs += c sum_k fac_k nh3_k v3_k */
            for (int k = 0; k < 3; k++) {
                double *vk = v3 + k * mat, *pk = prod + k * mat;
                memset(vk, 0, (size_t)mat * sizeof(double));
                if (fac[k] == 0.0) {
                    memset(pk, 0, (size_t)mat * sizeof(double));
                    continue;
                }
                for (int m = 1; m <= top; m++) {
                    const double wt = w[k * npts + m];
                    const double *hm = hist[m - 1];
                    for (int64_t q = 0; q < mat; q++)
                        vk[q] += wt * hm[q];
                }
                mm(N, nh3[k], vk, pk);
                const double f = c * fac[k];
                for (int64_t q = 0; q < mat; q++)
                    rhs[q] += f * pk[q];
            }
            /* L = 1 - c M_{i+1} - c sum_k fac_k w[k, 0] nh3_k */
            lhs_from(N, Mn, c, L);
            for (int k = 0; k < 3; k++) {
                const double f = c * fac[k] * w[k * npts];
                if (f == 0.0)
                    continue;
                for (int64_t q = 0; q < mat; q++)
                    L[q] -= f * nh3[k][q];
            }
            memcpy(un, rhs, (size_t)mat * sizeof(double));
            solve_n(N, L, un, piv);
            if (i == nm) {
                to_rows(N, uc, keep + 2 * (K_UM * E * nn) + e * mat);
                if (up)
                    to_rows(N, up, keep + 2 * (K_UMM1 * E * nn) + e * mat);
                to_rows(N, un, keep + 2 * (K_UMP1 * E * nn) + e * mat);
                to_rows(N, Mn, keep + 2 * (K_MMP1 * E * nn) + e * mat);
                to_rows(N, use_m1 ? Mp : Mc, keep + 2 * (K_MMM1 * E * nn) + e * mat);
                for (int k = 0; k < 3; k += 2) {
                    /* s3_k = fac_k (nh3_k u_{i+1} w[k, 0] + prod_k): the derivative-coupling part
                     * of u'' at r_{i+1} (k = 0) and r_{i-1} (k = 2) */
                    mm(N, nh3[k], un, s3);
                    const double wk = w[k * npts];
                    const double *pk = prod + k * mat;
                    for (int64_t q = 0; q < mat; q++)
                        s3[q] = fac[k] * (wk * s3[q] + pk[q]);
                    to_rows(N, s3, keep + 2 * ((k == 0 ? K_SP1 : K_SM1) * E * nn) + e * mat);
                }
                break;
            }
            /* advance: history, M, nh, M u */
            double *last = hist[5];
            for (int k = 5; k > 0; k--)
                hist[k] = hist[k - 1];
            hist[0] = last;
            memcpy(hist[0], un, (size_t)mat * sizeof(double));
            if (nhist < 6)
                nhist++;
            double *t = Mp; Mp = Mc; Mc = Mn; Mn = t;
            t = NHp; NHp = NHc; NHc = NHn; NHn = t;
            t = mu_p; mu_p = mu_c; mu_c = t;
            have_mu_p = 1;
            if (i % stab == stab - 1) {
                stabilise(&qw, hist[0], hist + 1, nhist - 1);
                have_mu_p = 0;
            }
        }
    }
    rc = 0;
done:
    for (int k = 0; k < 6; k++)
        free(hist[k]);
    free(Mp); free(Mc); free(Mn); free(NHp); free(NHc); free(NHn); free(mu_c); free(mu_p);
    free(rhs); free(L); free(v3); free(prod); free(s3); free(un); free(piv);
    qr_ws_free(&qw);
    return rc;
}


/* --------------------------------------------- CCBLOCKD: the same step, two products cheaper
 *
 * `cc_block_d_ref` above issues four complex products and one solve per step, 42.67 N^3 in the
 * counts CCPROP registered. Two facts about the step make two of those products avoidable without
 * touching the discretisation -- same Numerov recurrence, same 7-point one-sided stencil, same
 * grid, same matching point, same `keep`:
 *
 *  1. The three stencil products `nh3_k v_k` have a purely REAL left factor. `build_md` reaches
 *     `nh` through `add_real(sodc, ...)` and nothing else, and `sodc` (`ch.so_deriv_coef`) is
 *     real on every block. A real N x N times a complex N x N is C_re = D B_re, C_im = D B_im:
 *     two real products, 4 N^3, against zgemm's 8 -- the two terms zgemm forms against Im(D) are
 *     multiplications by an exact zero. The blocks are packed into the split layout
 *     [B_re | B_im] (N x 2N) so that the pair is one `dgemm`.
 *
 *  2. `M_i u_i` need not be recomputed: carry Y_j = (1 - c M_j) u_j as `cc_block_w` carries W.
 *     The right-hand side 2 u_i + 10 c M_i u_i - (u_{i-1} - c M_{i-1} u_{i-1}) is exactly
 *     12 u_i - 10 Y_i - Y_{i-1}, which costs no product at all. `cc_block_w` reads W_{i+1} off its
 *     solve; here the implicit matrix is L = (1 - c M_{i+1}) - c G with
 *     G = sum_k fac_k w[k,0] nh3_k, so
 *         Y_{i+1} = (1 - c M_{i+1}) u_{i+1} = L u_{i+1} + c G u_{i+1} = rhs + c (G u_{i+1}),
 *     and G is assembled for L anyway and is real: one 4 N^3 product in place of an 8 N^3 one.
 *     Y is linear in the solutions, so the stabilisation carries Y_i and Y_{i-1} as two more
 *     `ztrsm` companions -- and the reference's recomputation of M_{i-1} u_{i-1} after every
 *     stabilisation disappears with it.
 *
 * Per step: 3 x 4 + 4 + 10.67 = 26.67 N^3 against 42.67, plus one complex product per energy for
 * Y_0. Not bit-identical to `cc_block_d_ref` (BLAS summation order, and the recurrence carries Y
 * instead of re-forming M u); held to <= 1e-12, `docs/results/hf-ccblockd.md`.
 * `cc_set_blockd(0)` selects the reference arm (`HF_CCBLOCKD=0`).
 */

/* 0: `cc_block_d_ref`. 1 (the default): the real stencil products and the two-pass build, with
 * `M_i u_i` still formed, so the right-hand side carries no cancellation. 2: and lever 2, the
 * carried Y -- 5 % less CPU and ~13x further from the reference (`docs/results/hf-ccblockd.md`),
 * which is why it is not the default. */
static int bd_on = 1;

void cc_set_blockd(int64_t on) { bd_on = (int)on; }

/* CCBLOCKD: where `cc_block_d`'s time goes, for the write-up. Off unless `cc_set_blockd_time(1)`:
 * 0 build_mdr, 1 the v build, 2 the three stencil products, 3 the right-hand side and L,
 * 4 the solve, 5 Y and the advance. */
static int bd_time = 0;
static double bd_sec[6];

void cc_set_blockd_time(int64_t on)
{
    bd_time = (int)on;
    for (int k = 0; k < 6; k++)
        bd_sec[k] = 0.0;
}

void cc_get_blockd_time(double *out)
{
    for (int k = 0; k < 6; k++)
        out[k] = bd_sec[k];
}

static double bd_now(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double)t.tv_sec + 1.0e-9 * (double)t.tv_nsec;
}

#define BD_T0() bd_t0 = bd_time ? bd_now() : 0.0
#define BD_T1(k) do { if (bd_time) bd_sec[k] += bd_now() - bd_t0; } while (0)

/* below this N the triple loop replaces `dgemm` in `rmm` */
static int64_t rmm_small = 0;

void cc_set_rmm_small(int64_t n) { rmm_small = n; }

static double *dalloc(int64_t count)
{
    size_t bytes = ((size_t)(count * 8) + 64 + 63) & ~(size_t)63;
    double *p = aligned_alloc(64, bytes);
    if (p)
        memset(p, 0, bytes);
    return p;
}

/* `build_md` (M complex, nh real -- it has no imaginary part), the same additions per element in
 * the same order, but as two vectorisable passes over the block instead of ~4 NLAM + 1
 * read-modify-write passes with a transposed read on every one. The coupling matrices are
 * transposed into column-major once per block (`mdw_t`), so every read here is unit stride.
 * Bit-identical to `build_md`: each element sees the same sequence of additions.
 *
 * `build_md`'s order per element is: the NLAM central terms; then, on the diagonal only,
 * `diagr + mu ls2 so0`; then the NLAM (so1c, so2c) pairs. The diagonal sits between the two
 * groups, which is why this is two passes and not one. */
typedef struct {
    int64_t n, nlam;
    double *cplT, *so1T, *so2T, *sodT; /* (NLAM, N, N) column-major */
} mdw_t;

static int mdw_init(mdw_t *w, const blkd_t *d)
{
    const blk_t *b = &d->base;
    const int64_t n = b->n, nn = n * n, nl = b->nlam;
    w->n = n;
    w->nlam = nl;
    w->cplT = dalloc(4 * nl * nn);
    if (!w->cplT)
        return -1;
    w->so1T = w->cplT + nl * nn;
    w->so2T = w->so1T + nl * nn;
    w->sodT = w->so2T + nl * nn;
    for (int64_t lam = 0; lam < nl; lam++)
        for (int64_t a = 0; a < n; a++)
            for (int64_t c = 0; c < n; c++) {
                const int64_t s = lam * nn + a * n + c, t = lam * nn + c * n + a;
                w->cplT[t] = b->cpl[s];
                w->so1T[t] = d->so1c[s];
                w->so2T[t] = d->so2c[s];
                w->sodT[t] = d->sodc[s];
            }
    return 0;
}

static void mdw_free(mdw_t *w) { free(w->cplT); }

static void build_mdr(const mdw_t *w, const blkd_t *d, int64_t e, int64_t i, double *M, double *NH)
{
    const blk_t *b = &d->base;
    const int64_t n = w->n, nn = n * n, R = b->R, nl = w->nlam;
    const double mu = b->mu[e];
    /* the active terms, packed so that the element loops carry no branch */
    const double *pc[16], *p1[16], *p2[16], *pd[16];
    double cr[16], ci[16], f1[16], f2[16];
    int nc = 0, n1 = 0, n2 = 0;
    for (int64_t lam = 0; lam < nl && lam < 16; lam++) {
        const double *z = b->central + 2 * ((e * nl + lam) * R + i);
        const double sr = mu * z[0], si = mu * z[1];
        if (sr != 0.0 || si != 0.0) {
            cr[nc] = sr;
            ci[nc] = si;
            pc[nc++] = w->cplT + lam * nn;
        }
        const double g = mu * d->so_grad[(e * nl + lam) * R + i];
        if (g != 0.0) {
            f1[n1] = g;
            p1[n1++] = w->so1T + lam * nn;
        }
        const double q = mu * d->so_r2[(e * nl + lam) * R + i];
        if (q != 0.0) {
            f2[n2] = q;
            p2[n2] = w->so2T + lam * nn;
            pd[n2++] = w->sodT + lam * nn;
        }
    }
    for (int64_t q = 0; q < nn; q++) {
        double mr = 0.0, mi = 0.0;
        for (int t = 0; t < nc; t++) {
            const double g = pc[t][q];
            mr += cr[t] * g;
            mi += ci[t] * g;
        }
        M[2 * q] = mr;
        M[2 * q + 1] = mi;
    }
    const double *so = b->so0 + 2 * (e * b->R + i);
    const double *dr = b->diagr + (e * b->R + i) * n;
    for (int64_t a = 0; a < n; a++) {
        double *m = M + 2 * (a * n + a);
        const double f = mu * b->ls2[a];
        m[0] += dr[a] + f * so[0];
        m[1] += f * so[1];
    }
    for (int64_t q = 0; q < nn; q++) {
        double mr = M[2 * q], nh = 0.0;
        for (int t = 0; t < n1; t++)
            mr += f1[t] * p1[t][q];
        for (int t = 0; t < n2; t++) {
            mr += f2[t] * p2[t][q];
            nh += f2[t] * pd[t][q];
        }
        M[2 * q] = mr;
        NH[q] = nh;
    }
}

/* C = D B, D real column-major N x N, B and C complex in the split layout [re | im]
 * (N x 2N column-major, leading dimension N). 4 N^3. */
static void rmm(int64_t N, const double *D, const double *B, double *C)
{
    if (dgemm_p && N > rmm_small) {
        const int n = (int)N, n2 = (int)(2 * N);
        const double one = 1.0, zero = 0.0;
        dgemm_p("N", "N", &n, &n2, &n, &one, D, &n, B, &n, &zero, C, &n);
        return;
    }
    memset(C, 0, (size_t)(2 * N * N) * sizeof(double));
    for (int64_t j = 0; j < 2 * N; j++) {
        double *cj = C + j * N;
        const double *bj = B + j * N;
        for (int64_t k = 0; k < N; k++) {
            const double b = bj[k];
            if (b == 0.0)
                continue;
            const double *dk = D + k * N;
            for (int64_t a = 0; a < N; a++)
                cj[a] += dk[a] * b;
        }
    }
}

int cc_block_d(int64_t E, int64_t N, int64_t R, int64_t NLAM, const double *central,
               const double *cpl, const double *diagr, const double *so0, const double *ls2,
               const double *mu, const double *so_grad, const double *so_r2, const double *so1c,
               const double *so2c, const double *sodc, const double *fdw, const double *u1,
               const double *h, const int64_t *nmatch, int64_t stab, double *keep)
{
#ifdef CCFAST_SPLIT
    if (use_dgemm() && N >= 24) /* NATIVEX2 ccx: split storage, real products, Jacobi sweeps */
        return cc_block_d_split(E, N, R, NLAM, central, cpl, diagr, so0, ls2, mu, so_grad, so_r2,
                                so1c, so2c, sodc, fdw, u1, h, nmatch, stab, keep);
#endif
    if (!bd_on)
        return cc_block_d_ref(E, N, R, NLAM, central, cpl, diagr, so0, ls2, mu, so_grad, so_r2,
                              so1c, so2c, sodc, fdw, u1, h, nmatch, stab, keep);
    static const int64_t off[5] = {0, 9, 21, 36, 54};
    const int64_t nn = N * N, mat = 2 * nn;
    blkd_t d = {{N, NLAM, R, central, cpl, diagr, so0, ls2, mu}, so_grad, so_r2, so1c, so2c, sodc};
    int rc = -1;
    double *hist[6] = {0};
    double *Mp = zalloc(nn), *Mc = zalloc(nn), *Mn = zalloc(nn);
    double *Yp = zalloc(nn), *Yc = zalloc(nn), *Yn = zalloc(nn);
    double *rhs = zalloc(nn), *L = zalloc(nn), *s3 = zalloc(nn), *un = zalloc(nn);
    double *mu_c = zalloc(nn), *mu_p = zalloc(nn);
    double *NHp = dalloc(nn), *NHc = dalloc(nn), *NHn = dalloc(nn), *G = dalloc(nn);
    double *us = dalloc(2 * nn), *gs = dalloc(2 * nn);
    double *vs[3] = {dalloc(2 * nn), dalloc(2 * nn), dalloc(2 * nn)};
    double *ps[3] = {dalloc(2 * nn), dalloc(2 * nn), dalloc(2 * nn)};
    int *piv = malloc(sizeof(int) * (size_t)N);
    qr_ws_t qw = {0, 0, NULL, NULL, NULL};
    mdw_t mw = {0, 0, NULL, NULL, NULL, NULL};
    for (int k = 0; k < 6; k++)
        hist[k] = zalloc(nn);
    const int use_y = bd_on == 2;
    if (mdw_init(&mw, &d))
        goto done;
    if (!Mp || !Mc || !Mn || !Yp || !Yc || !Yn || !rhs || !L || !s3 || !un || !mu_c || !mu_p ||
        !NHp || !NHc ||
        !NHn || !G || !us || !gs || !vs[0] || !vs[1] || !vs[2] || !ps[0] || !ps[1] || !ps[2] ||
        !piv || qr_ws_init(&qw, N) || !hist[0] || !hist[1] || !hist[2] || !hist[3] || !hist[4] ||
        !hist[5])
        goto done;
    if (stab < 1)
        stab = 1;
    for (int64_t e = 0; e < E; e++) {
        const int64_t nm = nmatch[e];
        if (nm + 2 > R) {
            rc = -2;
            goto done;
        }
        const double c = h[e] * h[e] / 12.0;
        for (int64_t a = 0; a < N; a++)
            for (int64_t k = 0; k < N; k++) {
                hist[0][2 * (k * N + a)] = u1[2 * ((e * N + a) * N + k)];
                hist[0][2 * (k * N + a) + 1] = u1[2 * ((e * N + a) * N + k) + 1];
            }
        int nhist = 1, have_mu_p = 0;
        build_mdr(&mw, &d, e, 0, Mc, NHc);
        if (use_y) { /* lever 2 only */
            /* Y_0 = (1 - c M_0) u_0, one complex product per energy; Y_{-1} = 0 */
            lhs_from(N, Mc, c, L);
            mm(N, L, hist[0], Yc);
            memset(Yp, 0, (size_t)mat * sizeof(double));
        }
        for (int64_t i = 0; i <= nm; i++) {
            const int use_m1 = i != 0;
            const int npts = i + 3 < 7 ? (int)(i + 3) : 7;
            const double *w = fdw + off[npts - 3];
            const int top = npts - 1 < nhist ? npts - 1 : nhist;
            const double fac[3] = {(double)i + 2.0, 10.0 * ((double)i + 1.0),
                                   use_m1 ? (double)i : 0.0};
            const double *uc = hist[0];
            double bd_t0 = 0.0;
            { BD_T0(); build_mdr(&mw, &d, e, i + 1, Mn, NHn); BD_T1(0); }
            const double *nh3[3] = {NHn, NHc, use_m1 ? NHp : NHc};
            /* v_k = fac_k sum_{m=1..top} w[k, m] u_{i+1-m}, split. The element is the outer loop
             * and the history the inner one, so the six accumulators live in registers and each
             * u_{i+1-m} is read once: the reference reads the whole history three times and
             * writes the three v's `top` times each. */
            {
                BD_T0();
                double a0[7], a1[7], a2[7];
                const double *hp[7];
                for (int m = 1; m <= top; m++) {
                    a0[m] = fac[0] * w[m];
                    a1[m] = fac[1] * w[npts + m];
                    a2[m] = fac[2] * w[2 * npts + m];
                    hp[m] = hist[m - 1];
                }
                double *restrict v0 = vs[0];
                double *restrict v1 = vs[1];
                double *restrict v2 = vs[2];
                for (int64_t q = 0; q < nn; q++) {
                    double v0r = 0.0, v0i = 0.0, v1r = 0.0, v1i = 0.0, v2r = 0.0, v2i = 0.0;
                    for (int m = 1; m <= top; m++) {
                        const double hr = hp[m][2 * q], hi = hp[m][2 * q + 1];
                        v0r += a0[m] * hr;
                        v0i += a0[m] * hi;
                        v1r += a1[m] * hr;
                        v1i += a1[m] * hi;
                        v2r += a2[m] * hr;
                        v2i += a2[m] * hi;
                    }
                    v0[q] = v0r;
                    v0[nn + q] = v0i;
                    v1[q] = v1r;
                    v1[nn + q] = v1i;
                    v2[q] = v2r;
                    v2[nn + q] = v2i;
                }
                BD_T1(1);
            }
            {
                BD_T0();
                for (int k = 0; k < 3; k++) {
                    if (fac[k] == 0.0)
                        memset(ps[k], 0, (size_t)mat * sizeof(double));
                    else
                        rmm(N, nh3[k], vs[k], ps[k]);
                }
                BD_T1(2);
            }
            BD_T0();
            if (use_y) {
                /* rhs = 12 u_i - 10 Y_i - Y_{i-1} + c sum_k fac_k nh3_k v_k */
                for (int64_t q = 0; q < nn; q++) {
                    rhs[2 * q] = 12.0 * uc[2 * q] - 10.0 * Yc[2 * q] - Yp[2 * q]
                                 + c * (ps[0][q] + ps[1][q] + ps[2][q]);
                    rhs[2 * q + 1] = 12.0 * uc[2 * q + 1] - 10.0 * Yc[2 * q + 1] - Yp[2 * q + 1]
                                     + c * (ps[0][nn + q] + ps[1][nn + q] + ps[2][nn + q]);
                }
            } else {
                /* the reference right-hand side, which forms M_i u_i:
                 * 2 (u_i + 5 c M_i u_i) - (u_{i-1} - c M_{i-1} u_{i-1}) + c sum_k ... */
                const double *up = nhist > 1 ? hist[1] : NULL;
                mm(N, Mc, uc, mu_c);
                for (int64_t q = 0; q < nn; q++) {
                    rhs[2 * q] = 2.0 * uc[2 * q] + 10.0 * c * mu_c[2 * q];
                    rhs[2 * q + 1] = 2.0 * uc[2 * q + 1] + 10.0 * c * mu_c[2 * q + 1];
                }
                if (use_m1) {
                    if (!have_mu_p)
                        mm(N, Mp, up, mu_p);
                    for (int64_t q = 0; q < mat; q++)
                        rhs[q] -= up[q] - c * mu_p[q];
                }
                for (int64_t q = 0; q < nn; q++) {
                    rhs[2 * q] += c * (ps[0][q] + ps[1][q] + ps[2][q]);
                    rhs[2 * q + 1] += c * (ps[0][nn + q] + ps[1][nn + q] + ps[2][nn + q]);
                }
            }
            /* G = sum_k fac_k w[k, 0] nh3_k;  L = 1 - c M_{i+1} - c G */
            memset(G, 0, (size_t)nn * sizeof(double));
            for (int k = 0; k < 3; k++) {
                const double f = fac[k] * w[k * npts];
                if (f == 0.0)
                    continue;
                const double *restrict nk = nh3[k];
                double *restrict g = G;
                for (int64_t q = 0; q < nn; q++)
                    g[q] += f * nk[q];
            }
            lhs_from(N, Mn, c, L);
            for (int64_t q = 0; q < nn; q++)
                L[2 * q] -= c * G[q];
            memcpy(un, rhs, (size_t)mat * sizeof(double));
            BD_T1(3);
            {
                BD_T0();
                solve_n(N, L, un, piv);
                BD_T1(4);
            }
            BD_T0();
            for (int64_t q = 0; q < nn; q++) {
                us[q] = un[2 * q];
                us[nn + q] = un[2 * q + 1];
            }
            if (i == nm) {
                const double *up = nhist > 1 ? hist[1] : NULL;
                to_rows(N, uc, keep + 2 * (K_UM * E * nn) + e * mat);
                if (up)
                    to_rows(N, up, keep + 2 * (K_UMM1 * E * nn) + e * mat);
                to_rows(N, un, keep + 2 * (K_UMP1 * E * nn) + e * mat);
                to_rows(N, Mn, keep + 2 * (K_MMP1 * E * nn) + e * mat);
                to_rows(N, use_m1 ? Mp : Mc, keep + 2 * (K_MMM1 * E * nn) + e * mat);
                for (int k = 0; k < 3; k += 2) {
                    /* s3_k = fac_k (nh3_k u_{i+1} w[k, 0] + prod_k), the derivative-coupling part
                     * of u'' at r_{i+1} (k = 0) and r_{i-1} (k = 2); ps_k already carries fac_k */
                    if (fac[k] == 0.0) {
                        memset(s3, 0, (size_t)mat * sizeof(double));
                    } else {
                        const double wk = fac[k] * w[k * npts];
                        rmm(N, nh3[k], us, gs);
                        for (int64_t q = 0; q < nn; q++) {
                            s3[2 * q] = wk * gs[q] + ps[k][q];
                            s3[2 * q + 1] = wk * gs[nn + q] + ps[k][nn + q];
                        }
                    }
                    to_rows(N, s3, keep + 2 * ((k == 0 ? K_SP1 : K_SM1) * E * nn) + e * mat);
                }
                break;
            }
            if (use_y) {
                /* Y_{i+1} = rhs + c G u_{i+1} */
                rmm(N, G, us, gs);
                for (int64_t q = 0; q < nn; q++) {
                    Yn[2 * q] = rhs[2 * q] + c * gs[q];
                    Yn[2 * q + 1] = rhs[2 * q + 1] + c * gs[nn + q];
                }
            }
            /* advance: history, M, nh, Y */
            double *last = hist[5];
            for (int k = 5; k > 0; k--)
                hist[k] = hist[k - 1];
            hist[0] = last;
            memcpy(hist[0], un, (size_t)mat * sizeof(double));
            if (nhist < 6)
                nhist++;
            double *t = Mp; Mp = Mc; Mc = Mn; Mn = t;
            t = NHp; NHp = NHc; NHc = NHn; NHn = t;
            t = Yp; Yp = Yc; Yc = Yn; Yn = t;
            t = mu_p; mu_p = mu_c; mu_c = t;
            have_mu_p = 1;
            if (i % stab == stab - 1) {
                double *oth[7];
                int no = 0;
                for (int k = 1; k < nhist; k++)
                    oth[no++] = hist[k];
                if (use_y) {
                    oth[no++] = Yc;
                    oth[no++] = Yp;
                }
                stabilise(&qw, hist[0], oth, no);
                have_mu_p = 0;
            }
            BD_T1(5);
        }
    }
    rc = 0;
done:
    for (int k = 0; k < 6; k++)
        free(hist[k]);
    for (int k = 0; k < 3; k++) {
        free(vs[k]);
        free(ps[k]);
    }
    free(Mp); free(Mc); free(Mn); free(Yp); free(Yc); free(Yn);
    free(rhs); free(L); free(s3); free(un); free(mu_c); free(mu_p);
    free(NHp); free(NHc); free(NHn); free(G); free(us); free(gs);
    free(piv);
    qr_ws_free(&qw);
    mdw_free(&mw);
    return rc;
}

/* ---------------------------------------------- CCGLUE: matching and accumulation of one block
 *
 * `solver._match(minus_identity=True)` followed by `solver.accumulate(minus_identity=True)` for
 * the (E, N, N) `keep` that `cc_block_w` / `cc_block_d` wrote, in one call instead of ~60 torch
 * operations per block. The same algebra on the same numbers, to rounding (the gate is <= 1e-12
 * per cell):
 *   ddp1 = M_{m+1} u_{m+1} + s_{m+1},  ddm1 = M_{m-1} u_{m-1} + s_{m-1},
 *   U' = ((u_{m+1} - 2c ddp1) - (u_{m-1} - 2c ddm1)) / 2h, with U and U' column-normalised by
 *   max_a |U_ac|;  L = U' U^-1;  (L H+ - H+') D = L (H- - H+) - (H- - H+')  column by column;
 *   D <- D / scale_a * sqrt(k_a / k_c) on open (a, c), 0 elsewhere.
 * Only the elastic columns of D are ever read by `accumulate`, so only those right-hand sides are
 * solved. The asymptotic functions (`_asymptotic`) are formed here from the Coulomb functions
 * gathered per channel; a closed channel takes the decaying Riccati-Bessel function (`_riccati_k`).
 *
 * Arrays: keep (7, E, N, N) complex row-major (the kernels' output); k (E, N), open (E, N) bytes;
 * fv, dfv, gv, dgv (E, N) the Coulomb F, dF/drho, G, dG/drho at each channel's own l; l, level
 * (N,) int64; jv (N,); elastic (N,) bytes. Outputs per energy: reac, tot, el (E,), direct
 * (E, NLEV), tjl (E, LMAX + 1, 2), all in `accumulate`'s units and written, not added.
 * Returns 0, or -1 on allocation failure.
 */
#include <complex.h>

typedef double complex zc;

static void zsolve(int64_t n, int64_t nrhs, double *A, double *B, int *piv)
{
    if (nrhs == n && n <= small_n) {
        lu_solve_small(n, A, B);
        return;
    }
    const int nn = (int)n, nr = (int)nrhs;
    int info = 0;
    zgetrf_p(&nn, &nn, A, &nn, piv, &info);
    zgetrs_p("N", &nn, &nr, A, &nn, piv, B, &nn, &info);
}

int cc_match_acc(int64_t E, int64_t N, const double *keep, const double *h,
                 const int64_t *nmatch, const double *k, const uint8_t *open, const double *fv,
                 const double *dfv, const double *gv, const double *dgv, const int64_t *l,
                 const int64_t *level, const double *jv, const uint8_t *elastic, int64_t NLEV,
                 int64_t LMAX, double gw, double twoJp1, double two_i0p1, double *reac,
                 double *tot, double *el, double *direct, double *tjl)
{
    const int64_t nn = N * N, mat = 2 * nn;
    int64_t nent = 0, lmx = 0;
    for (int64_t a = 0; a < N; a++) {
        nent += elastic[a] != 0;
        if (l[a] > lmx)
            lmx = l[a];
    }
    int rc = -1;
    zc *um = malloc(sizeof(zc) * (size_t)nn), *du = malloc(sizeof(zc) * (size_t)nn);
    zc *tmp = malloc(sizeof(zc) * (size_t)nn), *A = malloc(sizeof(zc) * (size_t)nn);
    zc *B = malloc(sizeof(zc) * (size_t)(N * (nent > 0 ? nent : 1)));
    zc *hp = malloc(sizeof(zc) * (size_t)N), *dhp = malloc(sizeof(zc) * (size_t)N);
    zc *hm = malloc(sizeof(zc) * (size_t)N), *dhm = malloc(sizeof(zc) * (size_t)N);
    double *scale = malloc(sizeof(double) * (size_t)N), *rk = malloc(sizeof(double) * (size_t)(lmx + 2));
    double *col2 = malloc(sizeof(double) * (size_t)(nent > 0 ? nent : 1));
    int64_t *ent = malloc(sizeof(int64_t) * (size_t)(nent > 0 ? nent : 1));
    int *piv = malloc(sizeof(int) * (size_t)N);
    if (!um || !du || !tmp || !A || !B || !hp || !dhp || !hm || !dhm || !scale || !rk || !col2
        || !ent || !piv)
        goto done;
    for (int64_t a = 0, m = 0; a < N; a++)
        if (elastic[a])
            ent[m++] = a;
    memset(direct, 0, sizeof(double) * (size_t)(E * NLEV));
    memset(tjl, 0, sizeof(double) * (size_t)(E * (LMAX + 1) * 2));
    const zc zone = 1.0, zzero = 0.0;
    const int ni = (int)N;
    for (int64_t e = 0; e < E; e++) {
        const double he = h[e], c = he * he / 12.0, rm = he * ((double)nmatch[e] + 1.0);
        const double *ummb = keep + mat * (K_UMM1 * E + e), *umb = keep + mat * (K_UM * E + e);
        const double *umpb = keep + mat * (K_UMP1 * E + e), *mmmb = keep + mat * (K_MMM1 * E + e);
        const double *mmpb = keep + mat * (K_MMP1 * E + e), *spb = keep + mat * (K_SP1 * E + e);
        const double *smb = keep + mat * (K_SM1 * E + e);
        /* row-major A B is the column-major product B A of the same buffers */
        zgemm_p("N", "N", &ni, &ni, &ni, (const double *)&zone, umpb, &ni, mmpb, &ni,
                (const double *)&zzero, (double *)du, &ni);
        zgemm_p("N", "N", &ni, &ni, &ni, (const double *)&zone, ummb, &ni, mmmb, &ni,
                (const double *)&zzero, (double *)tmp, &ni);
        const zc c2 = 2.0 * c, inv2h = 2.0 * he;
        for (int64_t q = 0; q < nn; q++) {
            const zc ddp1 = du[q] + (spb[2 * q] + I * spb[2 * q + 1]);
            const zc ddm1 = tmp[q] + (smb[2 * q] + I * smb[2 * q + 1]);
            const zc up = umpb[2 * q] + I * umpb[2 * q + 1], uq = ummb[2 * q] + I * ummb[2 * q + 1];
            du[q] = ((up - c2 * ddp1) - (uq - c2 * ddm1)) / inv2h;
            um[q] = umb[2 * q] + I * umb[2 * q + 1];
        }
        for (int64_t cc = 0; cc < N; cc++) { /* row-major column cc: q = a N + cc */
            double cn = 0.0;
            for (int64_t a = 0; a < N; a++) {
                const double v = cabs(um[a * N + cc]);
                if (v > cn)
                    cn = v;
            }
            if (cn < 1.0e-300)
                cn = 1.0e-300;
            for (int64_t a = 0; a < N; a++) {
                um[a * N + cc] /= cn;
                du[a * N + cc] /= cn;
            }
        }
        /* L = U' U^-1: (U^T) X = U'^T, and the row-major buffers are the transposes read column-
         * major, so the solution buffer is L row-major */
        zsolve(N, N, (double *)um, (double *)du, piv);
        const zc *L = du;
        /* asymptotic functions */
        const double *ke = k + e * N;
        for (int64_t a = 0; a < N; a++) {
            const double kk = ke[a];
            if (open[e * N + a]) {
                hp[a] = gv[e * N + a] + I * fv[e * N + a];
                hm[a] = gv[e * N + a] - I * fv[e * N + a];
                dhp[a] = dgv[e * N + a] * kk + I * (dfv[e * N + a] * kk);
                dhm[a] = dgv[e * N + a] * kk - I * (dfv[e * N + a] * kk);
                scale[a] = 1.0;
            } else {
                double x = kk * rm;
                if (x < 1.0e-30)
                    x = 1.0e-30;
                const int64_t la = l[a];
                rk[0] = exp(-x);
                rk[1] = exp(-x) * (1.0 + 1.0 / x);
                for (int64_t q = 1; q <= la; q++)
                    rk[q + 1] = rk[q - 1] + (double)(2 * q + 1) * rk[q] / x;
                const double kv = rk[la];
                const double dkv = ((double)la + 1.0) * rk[la] / x - rk[la + 1];
                double s = fabs(kv);
                if (s < 1.0e-300)
                    s = 1.0e-300;
                scale[a] = s;
                hp[a] = kv / s;
                dhp[a] = (dkv * kk) / s;
                hm[a] = 0.0;
                dhm[a] = 0.0;
            }
        }
        /* (L H+ - H+') D = L (H- - H+) - (H- - H+'), column-major, elastic columns only */
        for (int64_t cc = 0; cc < N; cc++)
            for (int64_t a = 0; a < N; a++)
                A[cc * N + a] = L[a * N + cc] * hp[cc] - (a == cc ? dhp[cc] : 0.0);
        for (int64_t m = 0; m < nent; m++) {
            const int64_t cc = ent[m];
            const zc dh = hm[cc] - hp[cc], ddh = dhm[cc] - dhp[cc];
            for (int64_t a = 0; a < N; a++)
                B[m * N + a] = L[a * N + cc] * dh - (a == cc ? ddh : 0.0);
        }
        if (nent > 0)
            zsolve(N, nent, (double *)A, (double *)B, piv);
        /* D_{a, ent[m]} = B[m N + a] / scale_a * sqrt(k_a / k_c) on open (a, c) */
        double sr = 0.0, st = 0.0, se = 0.0;
        double *dir = direct + e * NLEV, *tj = tjl + e * (LMAX + 1) * 2;
        for (int64_t m = 0; m < nent; m++) {
            const int64_t cc = ent[m];
            const double kc = ke[cc] > 1.0e-30 ? ke[cc] : 1.0e-30;
            double s2 = 0.0;
            for (int64_t a = 0; a < N; a++) {
                zc d = 0.0;
                if (open[e * N + a] && open[e * N + cc])
                    d = B[m * N + a] / scale[a] * sqrt(ke[a] / kc);
                B[m * N + a] = d;
                const double p = creal(d) * creal(d) + cimag(d) * cimag(d);
                s2 += p;
                if (elastic[a])
                    se += p;
                else if (level[a] >= 1 && level[a] < NLEV)
                    dir[level[a]] += p;
            }
            const double dre = creal(B[m * N + cc]);
            double t = -2.0 * dre - s2;
            if (!(t >= 0.0))
                t = t != t ? t : 0.0;
            sr += t;
            st += -dre;
            const int64_t orb = l[cc];
            if (orb <= LMAX) {
                const int col = jv[cc] > (double)orb ? 1 : 0;
                tj[2 * orb + col] += twoJp1 / ((2.0 * jv[cc] + 1.0) * two_i0p1) * t;
            }
        }
        reac[e] = gw * sr;
        tot[e] = 2.0 * gw * st;
        el[e] = gw * se;
        for (int64_t b = 0; b < NLEV; b++)
            dir[b] *= gw;
    }
    rc = 0;
done:
    free(um); free(du); free(tmp); free(A); free(B); free(hp); free(dhp); free(hm); free(dhm);
    free(scale); free(rk); free(col2); free(ent); free(piv);
    return rc;
}


/* ------------------------------------------------------------ CCGLUE: 6j symbols element-wise
 *
 * `coupling.sixj` = `angmom.racah(a, b, e, d, c, f) * cos(pi (a + b + d + e))` for M argument
 * sextets, the same operations per element in the same order (the torch version is element-wise
 * too). torch's lgamma and exp are not libm's to the bit, and a 3e-16 change in a few hundred 6j
 * values moves coupled-channels cells by up to 6e-12, so the log-factorials come from torch's
 * table (`cc_set_logfact`) and the exponential is left to the caller. Chart-wide the torch evaluation was ~9 CPU-s
 * of the coupled-channels stage, nearly all op dispatch on (J, parity) blocks of a few thousand
 * elements. */
static int64_t twice_j(double j) { return (int64_t)trunc(2.0 * j + 1.0e-3); }

/* ln((k-1)!) from the caller's table when it covers k (`angmom._LOGFACT_TABLE`, torch's own lgamma,
 * which is not libm's to the bit), else libm */
static const double *lf_table = NULL;
static int64_t lf_n = 0;

void cc_set_logfact(const double *table, int64_t n)
{
    lf_table = table;
    lf_n = n;
}

static double lf(int64_t k)
{
    if (k < 1)
        k = 1;
    return k < lf_n ? lf_table[k] : lgamma((double)k);
}

static int64_t tdiv2(int64_t v) { return v / 2; } /* C division truncates toward zero, as torch's */

/* `__attribute__((optimize("fp-contract=off")))` is a GCC extension that Clang silently accepts
 * but does not implement (MACFIX6: this left arm64 Apple-clang builds fusing racah1's a*b+c chains
 * into fma(), breaking "torch does not fuse element-wise ops" -- test_ccglue's sixj-to-the-bit
 * failed on the Mac). The pragma below is the portable ISO C way to say the same thing, honoured
 * by both compilers; the GCC attribute stays for the toolchains that only look at attributes. */
#if defined(__GNUC__) && !defined(__clang__)
__attribute__((optimize("fp-contract=off"))) /* torch does not fuse element-wise ops */
#endif
#pragma STDC FP_CONTRACT OFF
static void racah1(double a, double b, double c, double d, double e, double f, double *expo,
                   double *mult)
{
    const int64_t ja = twice_j(a), jb = twice_j(b), jc = twice_j(c), jd = twice_j(d),
                  je = twice_j(e), jf = twice_j(f);
    const int64_t raw[12] = {ja + jb - je, jb + je - ja, je + ja - jb, jc + jd - je,
                             jd + je - jc, je + jc - jd, ja + jc - jf, jc + jf - ja,
                             jf + ja - jc, jb + jd - jf, jd + jf - jb, jf + jb - jd};
    int64_t n = jb + jd + jf;
    int ok = 1;
    int64_t ii[12];
    for (int q = 0; q < 12; q++) {
        const int64_t k = tdiv2(raw[q]);
        ok &= (raw[q] == 2 * k) && (k >= 0);
        if (k < n)
            n = k;
        ii[q] = k + 1;
    }
    const int64_t i13 = tdiv2(ja + jb + je), i14 = tdiv2(jc + jd + je), i15 = tdiv2(ja + jc + jf),
                  i16 = tdiv2(jb + jd + jf);
    int64_t il = i13 > i14 ? i13 : i14;
    const int64_t m2 = i15 > i16 ? i15 : i16;
    il = il > m2 ? il : m2;
    if (il < 0)
        il = 0;
    const int64_t j1 = il - i13 + 1, j2 = il - i14 + 1, j3 = il - i15 + 1, j4 = il - i16 + 1;
    const int64_t j5 = i13 + ii[3] - il, j6 = i15 + ii[4] - il, j7 = i16 + ii[5] - il;
    ok &= (j5 >= 1) && (j6 >= 1) && (j7 >= 1);
    *expo = 0.0;
    *mult = 0.0;
    if (!(ok && n >= 0))
        return;
    *expo = 0.5 * (lf(ii[0]) + lf(ii[1]) + lf(ii[2]) - lf(i13 + 2) + lf(ii[3]) + lf(ii[4])
                   + lf(ii[5]) - lf(i14 + 2) + lf(ii[6]) + lf(ii[7]) + lf(ii[8]) - lf(i15 + 2)
                   + lf(ii[9]) + lf(ii[10]) + lf(ii[11]) - lf(i16 + 2))
            + lf(il + 2) - lf(j1) - lf(j2) - lf(j3) - lf(j4) - lf(j5) - lf(j6) - lf(j7);
    const double sign = (j5 % 2 != 0) ? 1.0 : -1.0; /* h = -exp(expo), negated for odd j5 */
    if (n == 0) {
        *mult = sign;
        return;
    }
    const double p = (double)(il + 2), r_ = (double)j1, o_ = (double)j2, v_ = (double)j3,
                 w_ = (double)j4, x_ = (double)(j5 - 1), y_ = (double)(j6 - 1),
                 z_ = (double)(j7 - 1);
    double s = 1.0;
    for (int64_t qi = n - 1; qi >= 0; qi--) {
        const double q = (double)qi;
        s = 1.0 - s * ((p + q) / (r_ + q) * (x_ - q) / (o_ + q) * (y_ - q) / (v_ + q) * (z_ - q)
                       / (w_ + q));
    }
    *mult = sign * s;
}
#pragma STDC FP_CONTRACT ON

/* The 6j is exp(expo[m]) * mult[m]: the caller takes the exponential with torch's own exp, which
 * makes the values torch's to the bit (sign flips and the phase cos(pi n) = +-1 are exact). */
void cc_sixj(int64_t M, const double *j1, const double *j2, const double *j3, const double *j4,
             const double *j5, const double *j6, double *expo, double *mult)
{
    const double pi = 3.141592653589793;
    for (int64_t m = 0; m < M; m++) {
        racah1(j1[m], j2[m], j5[m], j4[m], j3[m], j6[m], expo + m, mult + m);
        mult[m] *= cos(pi * (j1[m] + j2[m] + j4[m] + j5[m]));
    }
}
