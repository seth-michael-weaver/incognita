/* SETB: split-storage linear algebra for `ccfast.c`'s two radial loops (built with -DCCFAST_SPLIT).
 *
 * The profile of a deformed target on the Mac M2 (Hf-177: 10.0 of 11.9 CPU-s in `cc_block_w`) is two
 * operations per Numerov step on an N x N complex matrix, N = 49-64 for most of the time:
 *
 *  1. `solve_n`: (1 - c M) X = W for N right-hand sides. Accelerate's zgetrf + zgetrs and
 *     `lu_solve_small` both spend ~170 us at N = 56. Their inner loops walk interleaved (re, im)
 *     pairs, which clang does not vectorise well. The same elimination on separate re and im arrays
 *     is two contiguous SAXPY streams per column and takes ~82 us, with the same pivoting.
 *  2. `stabilise`, every `stab` steps: Householder QR of W (zgeqrf + zungqr) and a right
 *     triangular solve (ztrsm) of every other matrix, ~350 us at N = 56 (Accelerate's ztrsm is not
 *     accelerated). Any change of basis W <- W T with a well-conditioned result serves: the columns
 *     of all the matrices stay the same solutions in the same basis, and L = U' U^-1 at the matching
 *     radius does not depend on T. Here T = U^-1 from Gaussian elimination with partial pivoting,
 *     W = P L U, so W <- P L (unit lower triangular up to the row order, multipliers <= 1 in
 *     modulus) and every other X <- X U^-1, all in split storage: ~100 us.
 *
 * Both are the same discretised equations; the numbers move by rounding (test_ccfast.py holds the
 * loops to the bitwise SPEEDT3 kernel at 1e-9). zgemm stays interleaved: at N = 56 Accelerate's
 * runs on the AMX block in ~19 us, far ahead of any loop here.
 */

#ifndef CCSPLIT_H
#define CCSPLIT_H

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int64_t cap;
    double *buf;
} sp_ws_t;

static _Thread_local sp_ws_t sp_ws = {0, NULL};

/* `count` doubles of per-thread scratch, grown on demand (never freed: one per worker thread) */
static double *sp_scratch(int64_t count)
{
    if (count > sp_ws.cap) {
        free(sp_ws.buf);
        size_t bytes = ((size_t)count * sizeof(double) + 63) & ~(size_t)63;
        sp_ws.buf = aligned_alloc(64, bytes);
        sp_ws.cap = sp_ws.buf ? count : 0;
    }
    return sp_ws.buf;
}

static void sp_pack(int64_t nn, const double *z, double *re, double *im)
{
    for (int64_t q = 0; q < nn; q++) {
        re[q] = z[2 * q];
        im[q] = z[2 * q + 1];
    }
}

static void sp_unpack(int64_t nn, const double *re, const double *im, double *z)
{
    for (int64_t q = 0; q < nn; q++) {
        z[2 * q] = re[q];
        z[2 * q + 1] = im[q];
    }
}

/* Gaussian elimination with partial pivoting of the column-major N x N matrix (ar, ai); swaps go to
 * columns `swap_from`..N-1 of the matrix and to all `nb` columns of (br, bi), whose rows are also
 * forward-eliminated. On exit the upper triangle holds U, the strict lower triangle the multipliers,
 * `perm[i]` the original row now at row i. With `all_columns` (the stabilisation) returns -1 on a
 * zero or non-finite pivot; otherwise always 0. */
static int sp_eliminate(int64_t N, double *restrict ar, double *restrict ai, int64_t nb,
                        double *restrict br, double *restrict bi, int64_t *perm, int all_columns)
{
    for (int64_t i = 0; i < N; i++)
        perm[i] = i;
    for (int64_t k = 0; k < N; k++) {
        const double *cr = ar + k * N, *ci = ai + k * N;
        int64_t p = k;
        double best = cr[k] * cr[k] + ci[k] * ci[k];
        for (int64_t i = k + 1; i < N; i++) {
            const double v = cr[i] * cr[i] + ci[i] * ci[i];
            if (v > best) {
                best = v;
                p = i;
            }
        }
        if (all_columns && (!(best > 0.0) || best == 1.0 / 0.0))
            return -1; /* the stabilisation skips; a solve goes on to inf/nan as LAPACK's would */
        if (p != k) {
            int64_t t = perm[k];
            perm[k] = perm[p];
            perm[p] = t;
            for (int64_t c = all_columns ? 0 : k; c < N; c++) {
                double x = ar[c * N + k];
                ar[c * N + k] = ar[c * N + p];
                ar[c * N + p] = x;
                x = ai[c * N + k];
                ai[c * N + k] = ai[c * N + p];
                ai[c * N + p] = x;
            }
            for (int64_t c = 0; c < nb; c++) {
                double x = br[c * N + k];
                br[c * N + k] = br[c * N + p];
                br[c * N + p] = x;
                x = bi[c * N + k];
                bi[c * N + k] = bi[c * N + p];
                bi[c * N + p] = x;
            }
        }
        double *lr = ar + k * N, *li = ai + k * N;
        const double den = best, ir = lr[k] / den, ii = -li[k] / den;
        for (int64_t i = k + 1; i < N; i++) {
            const double a = lr[i], b = li[i];
            lr[i] = a * ir - b * ii;
            li[i] = a * ii + b * ir;
        }
        for (int64_t c = k + 1; c < N; c++) {
            double *restrict xr = ar + c * N, *restrict xi = ai + c * N;
            const double ur = xr[k], ui = xi[k];
            if (ur == 0.0 && ui == 0.0)
                continue;
            for (int64_t i = k + 1; i < N; i++) {
                xr[i] -= lr[i] * ur - li[i] * ui;
                xi[i] -= lr[i] * ui + li[i] * ur;
            }
        }
        for (int64_t c = 0; c < nb; c++) {
            double *restrict xr = br + c * N, *restrict xi = bi + c * N;
            const double ur = xr[k], ui = xi[k];
            if (ur == 0.0 && ui == 0.0)
                continue;
            for (int64_t i = k + 1; i < N; i++) {
                xr[i] -= lr[i] * ur - li[i] * ui;
                xi[i] -= lr[i] * ui + li[i] * ur;
            }
        }
    }
    return 0;
}

/* X <- X U^-1 for the column-major N x N (xr, xi) and the upper triangle of (ur, ui) */
static void sp_right_solve_upper(int64_t N, const double *ur, const double *ui, double *restrict xr,
                                 double *restrict xi)
{
    for (int64_t j = 0; j < N; j++) {
        const double pr = ur[j * N + j], pi = ui[j * N + j];
        const double den = pr * pr + pi * pi, ir = pr / den, ii = -pi / den;
        double *yr = xr + j * N, *yi = xi + j * N;
        for (int64_t i = 0; i < N; i++) {
            const double a = yr[i], b = yi[i];
            yr[i] = a * ir - b * ii;
            yi[i] = a * ii + b * ir;
        }
        for (int64_t c = j + 1; c < N; c++) {
            const double gr = ur[c * N + j], gi = ui[c * N + j];
            if (gr == 0.0 && gi == 0.0)
                continue;
            double *restrict zr = xr + c * N, *restrict zi = xi + c * N;
            for (int64_t i = 0; i < N; i++) {
                zr[i] -= yr[i] * gr - yi[i] * gi;
                zi[i] -= yr[i] * gi + yi[i] * gr;
            }
        }
    }
}

/* A X = B for N right-hand sides on split column-major arrays, in place: (ar, ai) <- its LU,
 * (br, bi) <- X. A zero pivot gives inf/nan, as the interleaved loop's arithmetic does. */
static void sp_solve(int64_t N, double *restrict ar, double *restrict ai, double *restrict br,
                     double *restrict bi, int64_t *perm)
{
    sp_eliminate(N, ar, ai, N, br, bi, perm, 0);
    for (int64_t k = N - 1; k >= 0; k--) {
        const double *cr = ar + k * N, *ci = ai + k * N;
        const double den = cr[k] * cr[k] + ci[k] * ci[k], ir = cr[k] / den, ii = -ci[k] / den;
        for (int64_t j = 0; j < N; j++) {
            double *restrict xr = br + j * N, *restrict xi = bi + j * N;
            const double yr = xr[k] * ir - xi[k] * ii, yi = xr[k] * ii + xi[k] * ir;
            xr[k] = yr;
            xi[k] = yi;
            if (yr == 0.0 && yi == 0.0)
                continue;
            for (int64_t i = 0; i < k; i++) {
                xr[i] -= cr[i] * yr - ci[i] * yi;
                xi[i] -= cr[i] * yi + ci[i] * yr;
            }
        }
    }
}

/* `solve_n`: A X = B for N right-hand sides, column-major interleaved, in place (B <- X) */
static void solve_split(int64_t N, double *A, double *B, int *piv)
{
    const int64_t nn = N * N;
    double *s = sp_scratch(4 * nn + N);
    if (!s) {
        lu_solve_small(N, A, B);
        return;
    }
    double *ar = s, *ai = s + nn, *br = s + 2 * nn, *bi = s + 3 * nn;
    int64_t *perm = (int64_t *)(s + 4 * nn);
    (void)piv;
    sp_pack(nn, A, ar, ai);
    sp_pack(nn, B, br, bi);
    sp_solve(N, ar, ai, br, bi, perm);
    sp_unpack(nn, br, bi, B);
}

/* NATIVEX2 ccx: V = U^-1 for the upper triangle of (ar, ai), column by column (split, column-major) */
static void sp_upper_inverse(int64_t N, const double *ar, const double *ai, double *vr, double *vi)
{
    const int64_t nn = N * N;
    memset(vr, 0, (size_t)nn * sizeof(double));
    memset(vi, 0, (size_t)nn * sizeof(double));
    for (int64_t j = 0; j < N; j++) {
        double *restrict xr = vr + j * N, *restrict xi = vi + j * N;
        xr[j] = 1.0;
        for (int64_t k = j; k >= 0; k--) {
            const double *ur = ar + k * N, *ui = ai + k * N;
            const double den = ur[k] * ur[k] + ui[k] * ui[k], ir = ur[k] / den, ii = -ui[k] / den;
            const double yr = xr[k] * ir - xi[k] * ii, yi = xr[k] * ii + xi[k] * ir;
            xr[k] = yr;
            xi[k] = yi;
            if (yr == 0.0 && yi == 0.0)
                continue;
            for (int64_t i = 0; i < k; i++) {
                xr[i] -= ur[i] * yr - ui[i] * yi;
                xi[i] -= ur[i] * yi + ui[i] * yr;
            }
        }
    }
}

static _Thread_local ws_t st_ws = {0, NULL};

/* The stabilisation on split arrays: Q = P L U by elimination (on a copy in `work`, 2 N^2 doubles);
 * Q <- P L and every (xr[m], xi[m]) <- X U^-1. Returns 0, or -1 (nothing changed) on a zero or
 * non-finite pivot, where the QR version skips a singular R. */
static int sp_stabilise(int64_t N, double *qr, double *qi, double **xr, double **xi, int k,
                        double *work, int64_t *perm)
{
    const int64_t nn = N * N;
    double *ar = work, *ai = work + nn;
    memcpy(ar, qr, (size_t)nn * sizeof(double));
    memcpy(ai, qi, (size_t)nn * sizeof(double));
    if (sp_eliminate(N, ar, ai, 0, NULL, NULL, perm, 1) != 0)
        return -1;
    for (int64_t a = 0; a < N; a++)
        if (!isfinite(ar[a * N + a]) || !isfinite(ai[a * N + a]))
            return -1;
    double *s = use_dgemm() && N >= 32 ? ws_get(&st_ws, 4 * nn) : NULL; /* loops win below */
    if (s) { /* NATIVEX2 ccx: X U^-1 as X V with V = U^-1, by real products */
        sp_upper_inverse(N, ar, ai, s, s + nn);
        for (int m = 0; m < k; m++) {
            dmm_split(N, xr[m], xi[m], s, s + nn, s + 2 * nn, s + 3 * nn, 0);
            memcpy(xr[m], s + 2 * nn, (size_t)nn * sizeof(double));
            memcpy(xi[m], s + 3 * nn, (size_t)nn * sizeof(double));
        }
    } else {
        for (int m = 0; m < k; m++)
            sp_right_solve_upper(N, ar, ai, xr[m], xi[m]);
    }
    memset(qr, 0, (size_t)nn * sizeof(double));
    memset(qi, 0, (size_t)nn * sizeof(double));
    for (int64_t j = 0; j < N; j++) {
        qr[j * N + perm[j]] = 1.0;
        for (int64_t i = j + 1; i < N; i++) {
            qr[j * N + perm[i]] = ar[j * N + i];
            qi[j * N + perm[i]] = ai[j * N + i];
        }
    }
    return 0;
}

/* `stabilise` on interleaved matrices (the derivative-coupling loop's history) */
static void stabilise_split(double *Q, double **others, int k, int64_t N)
{
    const int64_t nn = N * N;
    double *s = sp_scratch((4 + 2 * (int64_t)k) * nn + N);
    if (!s)
        return;
    double *qr = s, *qi = s + nn, *work = s + 2 * nn;
    int64_t *perm = (int64_t *)(s + (4 + 2 * (int64_t)k) * nn);
    double *xr[8], *xi[8];
    sp_pack(nn, Q, qr, qi);
    for (int m = 0; m < k; m++) {
        xr[m] = s + (4 + 2 * (int64_t)m) * nn;
        xi[m] = xr[m] + nn;
        sp_pack(nn, others[m], xr[m], xi[m]);
    }
    if (sp_stabilise(N, qr, qi, xr, xi, k, work, perm) != 0)
        return;
    sp_unpack(nn, qr, qi, Q);
    for (int m = 0; m < k; m++)
        sp_unpack(nn, xr[m], xi[m], others[m]);
}

/* column-major split -> row-major interleaved (N x N) */
static void sp_to_rows(int64_t n, const double *re, const double *im, double *dst)
{
    for (int64_t a = 0; a < n; a++)
        for (int64_t c = 0; c < n; c++) {
            dst[2 * (a * n + c)] = re[c * n + a];
            dst[2 * (a * n + c) + 1] = im[c * n + a];
        }
}

/* CCNUMEROV: M(r_i) in split column-major storage, from the same inputs the fused L build below
 * reads (the monopole shortcut of NATIVEX2 ccx included). */
static void build_m_split(int64_t N, int64_t NLAM, int64_t R, int64_t e, int64_t i,
                          const double *central, const double *gcm, const int *lam_diag,
                          const double *diagr, const double *so0, const double *ls2, double m,
                          double *Mr, double *Mi)
{
    const int64_t nn = N * N;
    memset(Mr, 0, (size_t)nn * sizeof(double));
    memset(Mi, 0, (size_t)nn * sizeof(double));
    for (int64_t lam = 0; lam < NLAM; lam++) {
        const double *zc = central + 2 * ((e * NLAM + lam) * R + i);
        const double sr = m * zc[0], si = m * zc[1];
        if (sr == 0.0 && si == 0.0)
            continue;
        const double *restrict g = gcm + lam * nn;
        if (lam < 16 && lam_diag[lam]) {
            for (int64_t a = 0; a < N; a++) {
                Mr[a * N + a] += sr * g[a * N + a];
                Mi[a * N + a] += si * g[a * N + a];
            }
            continue;
        }
        for (int64_t q = 0; q < nn; q++) {
            Mr[q] += sr * g[q];
            Mi[q] += si * g[q];
        }
    }
    {
        const double *so = so0 + 2 * (e * R + i);
        const double *dr = diagr + (e * R + i) * N;
        for (int64_t a = 0; a < N; a++) {
            const double f = m * ls2[a];
            Mr[a * N + a] += dr[a] + f * so[0];
            Mi[a * N + a] += f * so[1];
        }
    }
}


/* CCNUMEROV: `cc_block_w_split` with ECIS's modified Numerov step -- two split products of M(r_i)
 * per step and no solve at all.  Same arguments and return codes as `cc_block_w`. */
static int cc_block_mn_split(int64_t E, int64_t N, int64_t R, int64_t NLAM, const double *central,
                             const double *cpl, const double *diagr, const double *so0,
                             const double *ls2, const double *mu, const double *u1,
                             const double *h, const int64_t *nmatch, int64_t stab, double *keep)
{
    const int64_t nn = N * N, mat = 2 * nn;
    blk_t b = {N, NLAM, R, central, cpl, diagr, so0, ls2, mu};
    int rc = -1;
    /* 10 split matrices (up uc un y z M) + stabilisation work + column-major couplings */
    const int64_t count = 14 * nn + NLAM * nn + N;
    double *pool = zalloc((count + 1) / 2 + 1);
    double *M = zalloc(nn);
    if (!pool || !M)
        goto done;
    if (stab < 1)
        stab = 1;
    {
        double *upr = pool, *upi = pool + nn, *ucr = pool + 2 * nn, *uci = pool + 3 * nn;
        double *unr = pool + 4 * nn, *uni = pool + 5 * nn, *yr = pool + 6 * nn, *yi = pool + 7 * nn;
        double *zr = pool + 8 * nn, *zi = pool + 9 * nn, *Mr = pool + 10 * nn, *Mi = pool + 11 * nn;
        double *work = pool + 12 * nn;
        double *gcm = pool + 14 * nn;
        int64_t *perm = (int64_t *)(pool + 14 * nn + NLAM * nn);
        for (int64_t lam = 0; lam < NLAM; lam++)
            for (int64_t a = 0; a < N; a++)
                for (int64_t c2 = 0; c2 < N; c2++)
                    gcm[lam * nn + c2 * N + a] = cpl[lam * nn + a * N + c2];
        int lam_diag[16] = {0};
        for (int64_t lam = 0; lam < NLAM && lam < 16; lam++) {
            lam_diag[lam] = 1;
            for (int64_t q = 0; q < nn; q++)
                if (q % (N + 1) != 0 && gcm[lam * nn + q] != 0.0)
                    lam_diag[lam] = 0;
        }
        for (int64_t e = 0; e < E; e++) {
            const int64_t nm = nmatch[e];
            if (nm + 2 > R) {
                rc = -2;
                goto done;
            }
            const double c = h[e] * h[e] / 12.0, m = mu[e];
            const double c12 = 12.0 * c, c144 = c12 * c;
            for (int64_t a = 0; a < N; a++)
                for (int64_t k = 0; k < N; k++) {
                    ucr[k * N + a] = u1[2 * ((e * N + a) * N + k)];
                    uci[k * N + a] = u1[2 * ((e * N + a) * N + k) + 1];
                }
            memset(upr, 0, (size_t)nn * sizeof(double));
            memset(upi, 0, (size_t)nn * sizeof(double));
            build_m_split(N, NLAM, R, e, 0, central, gcm, lam_diag, diagr, so0, ls2, m, Mr, Mi);
            for (int64_t i = 0; i <= nm; i++) {
                mm_split(N, Mr, Mi, ucr, uci, yr, yi);
                mm_split(N, Mr, Mi, yr, yi, zr, zi);
                for (int64_t q = 0; q < nn; q++) {
                    unr[q] = 2.0 * ucr[q] - upr[q] + c12 * yr[q] + c144 * zr[q];
                    uni[q] = 2.0 * uci[q] - upi[q] + c12 * yi[q] + c144 * zi[q];
                }
                if (i == nm) {
                    sp_to_rows(N, ucr, uci, keep + 2 * (K_UM * E * nn) + e * mat);
                    sp_to_rows(N, upr, upi, keep + 2 * (K_UMM1 * E * nn) + e * mat);
                    sp_to_rows(N, unr, uni, keep + 2 * (K_UMP1 * E * nn) + e * mat);
                    build_m(&b, e, i + 1, M);
                    to_rows(N, M, keep + 2 * (K_MMP1 * E * nn) + e * mat);
                    build_m(&b, e, i > 0 ? i - 1 : 0, M);
                    to_rows(N, M, keep + 2 * (K_MMM1 * E * nn) + e * mat);
                    break;
                }
                double *t;
                t = upr; upr = ucr; ucr = unr; unr = t;
                t = upi; upi = uci; uci = uni; uni = t;
                build_m_split(N, NLAM, R, e, i + 1, central, gcm, lam_diag, diagr, so0, ls2, m,
                              Mr, Mi);
                if (i % stab == stab - 1) {
                    double *xr[1] = {upr}, *xi[1] = {upi};
                    sp_stabilise(N, ucr, uci, xr, xi, 1, work, perm);
                }
            }
        }
    }
    rc = 0;
done:
    free(pool);
    free(M);
    return rc;
}


/* `cc_block_w` with every per-step matrix in split storage: L = 1 - c M(r_{i+1}) is assembled
 * directly from column-major copies of the coupling matrices, and W, u, the solve and the
 * stabilisation never leave split storage; the interleaved M and u are formed only at the
 * matching point. Same arguments and return codes as `cc_block_w`. */
static int cc_block_w_split(int64_t E, int64_t N, int64_t R, int64_t NLAM, const double *central,
                            const double *cpl, const double *diagr, const double *so0,
                            const double *ls2, const double *mu, const double *u1, const double *h,
                            const int64_t *nmatch, int64_t stab, double *keep)
{
    const int64_t nn = N * N, mat = 2 * nn;
    blk_t b = {N, NLAM, R, central, cpl, diagr, so0, ls2, mu};
    int rc = -1;
    /* 6 split matrices (Wp Wc Wn up uc un) + L + stabilisation work + column-major couplings */
    const int64_t count = 16 * nn + NLAM * nn + N;
    double *pool = zalloc((count + 1) / 2 + 1);
    double *M = zalloc(nn), *L = zalloc(nn);
    if (!pool || !M || !L)
        goto done;
    if (stab < 1)
        stab = 1;
    {
        double *Wpr = pool, *Wpi = pool + nn, *Wcr = pool + 2 * nn, *Wci = pool + 3 * nn;
        double *Wnr = pool + 4 * nn, *Wni = pool + 5 * nn, *upr = pool + 6 * nn, *upi = pool + 7 * nn;
        double *ucr = pool + 8 * nn, *uci = pool + 9 * nn, *unr = pool + 10 * nn, *uni = pool + 11 * nn;
        double *Lr = pool + 12 * nn, *Li = pool + 13 * nn, *work = pool + 14 * nn;
        double *gcm = pool + 16 * nn;
        int64_t *perm = (int64_t *)(pool + 16 * nn + NLAM * nn);
        for (int64_t lam = 0; lam < NLAM; lam++)
            for (int64_t a = 0; a < N; a++)
                for (int64_t c2 = 0; c2 < N; c2++)
                    gcm[lam * nn + c2 * N + a] = cpl[lam * nn + a * N + c2];
        /* NATIVEX2 ccx: a diagonal coupling matrix (the monopole: the identity) adds to the diagonal
         * of L only */
        int lam_diag[16] = {0};
        for (int64_t lam = 0; lam < NLAM && lam < 16; lam++) {
            lam_diag[lam] = 1;
            for (int64_t q = 0; q < nn; q++)
                if (q % (N + 1) != 0 && gcm[lam * nn + q] != 0.0)
                    lam_diag[lam] = 0;
        }
        for (int64_t e = 0; e < E; e++) {
            const int64_t nm = nmatch[e];
            if (nm + 2 > R) {
                rc = -2;
                goto done;
            }
            const double c = h[e] * h[e] / 12.0, m = mu[e];
            for (int64_t a = 0; a < N; a++)
                for (int64_t k = 0; k < N; k++) {
                    ucr[k * N + a] = u1[2 * ((e * N + a) * N + k)];
                    uci[k * N + a] = u1[2 * ((e * N + a) * N + k) + 1];
                }
            memset(upr, 0, (size_t)nn * sizeof(double));
            memset(upi, 0, (size_t)nn * sizeof(double));
            memset(Wpr, 0, (size_t)nn * sizeof(double));
            memset(Wpi, 0, (size_t)nn * sizeof(double));
            {
                double *Wtmp = zalloc(nn), *U0 = zalloc(nn);
                if (!Wtmp || !U0) {
                    free(Wtmp);
                    free(U0);
                    goto done;
                }
                build_m(&b, e, 0, M);
                lhs_from(N, M, c, L);
                sp_unpack(nn, ucr, uci, U0);
                mm(N, L, U0, Wtmp);
                sp_pack(nn, Wtmp, Wcr, Wci);
                free(Wtmp);
                free(U0);
            }
            for (int64_t i = 0; i <= nm; i++) {
                for (int64_t q = 0; q < nn; q++) {
                    Wnr[q] = 12.0 * ucr[q] - 10.0 * Wcr[q] - Wpr[q];
                    Wni[q] = 12.0 * uci[q] - 10.0 * Wci[q] - Wpi[q];
                }
                /* L = 1 - c M(r_{i+1}) */
                memset(Lr, 0, (size_t)nn * sizeof(double));
                memset(Li, 0, (size_t)nn * sizeof(double));
                for (int64_t lam = 0; lam < NLAM; lam++) {
                    const double *z = central + 2 * ((e * NLAM + lam) * R + i + 1);
                    const double sr = -c * m * z[0], si = -c * m * z[1];
                    if (sr == 0.0 && si == 0.0)
                        continue;
                    const double *restrict g = gcm + lam * nn;
                    if (lam < 16 && lam_diag[lam]) {
                        for (int64_t a = 0; a < N; a++) {
                            Lr[a * N + a] += sr * g[a * N + a];
                            Li[a * N + a] += si * g[a * N + a];
                        }
                        continue;
                    }
                    for (int64_t q = 0; q < nn; q++) {
                        Lr[q] += sr * g[q];
                        Li[q] += si * g[q];
                    }
                }
                {
                    const double *so = so0 + 2 * (e * R + i + 1);
                    const double *dr = diagr + (e * R + i + 1) * N;
                    for (int64_t a = 0; a < N; a++) {
                        const double f = m * ls2[a];
                        Lr[a * N + a] += 1.0 - c * (dr[a] + f * so[0]);
                        Li[a * N + a] += -c * (f * so[1]);
                    }
                }
                if (nm_solve_split(N, Lr, Li, Wnr, Wni, unr, uni) != 0) { /* NATIVEX2 ccx */
                    memcpy(unr, Wnr, (size_t)nn * sizeof(double));
                    memcpy(uni, Wni, (size_t)nn * sizeof(double));
                    sp_solve(N, Lr, Li, unr, uni, perm);
                }
                if (i == nm) {
                    sp_to_rows(N, ucr, uci, keep + 2 * (K_UM * E * nn) + e * mat);
                    sp_to_rows(N, upr, upi, keep + 2 * (K_UMM1 * E * nn) + e * mat);
                    sp_to_rows(N, unr, uni, keep + 2 * (K_UMP1 * E * nn) + e * mat);
                    build_m(&b, e, i + 1, M);
                    to_rows(N, M, keep + 2 * (K_MMP1 * E * nn) + e * mat);
                    build_m(&b, e, i > 0 ? i - 1 : 0, M);
                    to_rows(N, M, keep + 2 * (K_MMM1 * E * nn) + e * mat);
                    break;
                }
                double *t;
                t = Wpr; Wpr = Wcr; Wcr = Wnr; Wnr = t;
                t = Wpi; Wpi = Wci; Wci = Wni; Wni = t;
                t = upr; upr = ucr; ucr = unr; unr = t;
                t = upi; upi = uci; uci = uni; uni = t;
                if (i % stab == stab - 1) {
                    double *xr[3] = {Wpr, ucr, upr}, *xi[3] = {Wpi, uci, upi};
                    sp_stabilise(N, Wcr, Wci, xr, xi, 3, work, perm);
                }
            }
        }
    }
    rc = 0;
done:
    free(pool);
    free(M);
    free(L);
    return rc;
}


/* NATIVEX2 ccx: M(r_i) (split, column-major) and the real derivative-coupling matrix NH(r_i) of
 * `build_md`, from column-major copies of the coupling matrices (gcm, c1, c2, cd: NLAM N^2 each);
 * a diagonal coupling matrix (`lam_diag`) adds to the diagonal only. The terms are added in
 * `build_md`'s order. */
static void dsp_build(int64_t N, int64_t NLAM, int64_t R, int64_t e, int64_t i, double m,
                      const double *central, const double *gcm, const int *lam_diag,
                      const double *diagr, const double *so0, const double *ls2,
                      const double *so_grad, const double *so_r2, const double *c1, const double *c2,
                      const double *cd, double *restrict Mr, double *restrict Mi, double *restrict NH)
{
    const int64_t nn = N * N;
    memset(Mr, 0, (size_t)nn * sizeof(double));
    memset(Mi, 0, (size_t)nn * sizeof(double));
    memset(NH, 0, (size_t)nn * sizeof(double));
    for (int64_t lam = 0; lam < NLAM; lam++) {
        const double *z = central + 2 * ((e * NLAM + lam) * R + i);
        const double sr = m * z[0], si = m * z[1];
        if (sr == 0.0 && si == 0.0)
            continue;
        const double *restrict g = gcm + lam * nn;
        if (lam < 16 && lam_diag[lam]) {
            for (int64_t a = 0; a < N; a++) {
                Mr[a * N + a] += sr * g[a * N + a];
                Mi[a * N + a] += si * g[a * N + a];
            }
            continue;
        }
        for (int64_t q = 0; q < nn; q++) {
            Mr[q] += sr * g[q];
            Mi[q] += si * g[q];
        }
    }
    const double *so = so0 + 2 * (e * R + i);
    const double *dr = diagr + (e * R + i) * N;
    for (int64_t a = 0; a < N; a++) {
        const double f = m * ls2[a];
        Mr[a * N + a] += dr[a] + f * so[0];
        Mi[a * N + a] += f * so[1];
    }
    for (int64_t lam = 0; lam < NLAM; lam++) {
        const double fg = m * so_grad[(e * NLAM + lam) * R + i];
        const double fq = m * so_r2[(e * NLAM + lam) * R + i];
        const double *restrict a1 = c1 + lam * nn, *restrict a2 = c2 + lam * nn,
                               *restrict ad = cd + lam * nn;
        if (fg != 0.0)
            for (int64_t q = 0; q < nn; q++)
                Mr[q] += fg * a1[q];
        if (fq != 0.0) {
            for (int64_t q = 0; q < nn; q++)
                Mr[q] += fq * a2[q];
            for (int64_t q = 0; q < nn; q++)
                NH[q] += fq * ad[q];
        }
    }
}

/* NATIVEX2 ccx: `cc_block_d` with every matrix in split storage, the products as real ones
 * (`dmm_split`), the solve by the Jacobi sweeps where they apply and `sp_solve` otherwise, and the
 * stabilisation of `sp_stabilise`: the same step, operation for operation where the arithmetic is
 * elementwise. Same arguments and return codes as `cc_block_d`. */
static int cc_block_d_split(int64_t E, int64_t N, int64_t R, int64_t NLAM, const double *central,
                            const double *cpl, const double *diagr, const double *so0,
                            const double *ls2, const double *mu, const double *so_grad,
                            const double *so_r2, const double *so1c, const double *so2c,
                            const double *sodc, const double *fdw, const double *u1,
                            const double *h, const int64_t *nmatch, int64_t stab, double *keep)
{
    static const int64_t off[5] = {0, 9, 21, 36, 54};
    const int64_t nn = N * N, mat = 2 * nn;
    /* split matrices: hist 12, M 6, NH 3, mu 4, rhs 2, L 2, un 2, v3 6, prod 6, s3 2, work 2 */
    const int64_t count = 47 * nn + 4 * NLAM * nn + N;
    double *pool = zalloc((count + 1) / 2 + 1);
    if (!pool)
        return -1;
    if (stab < 1)
        stab = 1;
    double *p = pool;
#define TAKE(k) (p += (k), p - (k))
    double *hr[6], *hi[6];
    for (int k = 0; k < 6; k++) {
        hr[k] = TAKE(nn);
        hi[k] = TAKE(nn);
    }
    double *Mpr = TAKE(nn), *Mpi = TAKE(nn), *Mcr = TAKE(nn), *Mci = TAKE(nn), *Mnr = TAKE(nn),
           *Mni = TAKE(nn);
    double *NHp = TAKE(nn), *NHc = TAKE(nn), *NHn = TAKE(nn);
    double *mcr = TAKE(nn), *mci = TAKE(nn), *mpr = TAKE(nn), *mpi = TAKE(nn);
    double *rr = TAKE(nn), *ri = TAKE(nn), *Lr = TAKE(nn), *Li = TAKE(nn), *unr = TAKE(nn),
           *uni = TAKE(nn);
    double *vr[3], *vi[3], *pr3[3], *pi3[3];
    for (int k = 0; k < 3; k++) {
        vr[k] = TAKE(nn);
        vi[k] = TAKE(nn);
        pr3[k] = TAKE(nn);
        pi3[k] = TAKE(nn);
    }
    double *s3r = TAKE(nn), *s3i = TAKE(nn), *work = TAKE(2 * nn);
    double *gcm = TAKE(NLAM * nn), *c1 = TAKE(NLAM * nn), *c2 = TAKE(NLAM * nn),
           *cd = TAKE(NLAM * nn);
    int64_t *perm = (int64_t *)TAKE(N);
#undef TAKE
    for (int64_t lam = 0; lam < NLAM; lam++)
        for (int64_t a = 0; a < N; a++)
            for (int64_t b = 0; b < N; b++) {
                gcm[lam * nn + b * N + a] = cpl[lam * nn + a * N + b];
                c1[lam * nn + b * N + a] = so1c[lam * nn + a * N + b];
                c2[lam * nn + b * N + a] = so2c[lam * nn + a * N + b];
                cd[lam * nn + b * N + a] = sodc[lam * nn + a * N + b];
            }
    int lam_diag[16] = {0};
    for (int64_t lam = 0; lam < NLAM && lam < 16; lam++) {
        lam_diag[lam] = 1;
        for (int64_t q = 0; q < nn; q++)
            if (q % (N + 1) != 0 && gcm[lam * nn + q] != 0.0)
                lam_diag[lam] = 0;
    }
    int rc = 0;
    for (int64_t e = 0; e < E && rc == 0; e++) {
        const int64_t nm = nmatch[e];
        if (nm + 2 > R) {
            rc = -2;
            break;
        }
        const double c = h[e] * h[e] / 12.0, m = mu[e];
        for (int64_t a = 0; a < N; a++)
            for (int64_t k = 0; k < N; k++) {
                hr[0][k * N + a] = u1[2 * ((e * N + a) * N + k)];
                hi[0][k * N + a] = u1[2 * ((e * N + a) * N + k) + 1];
            }
        int nhist = 1, have_mu_p = 0;
        dsp_build(N, NLAM, R, e, 0, m, central, gcm, lam_diag, diagr, so0, ls2, so_grad, so_r2, c1,
                  c2, cd, Mcr, Mci, NHc);
        for (int64_t i = 0; i <= nm; i++) {
            const int use_m1 = i != 0;
            const int npts = i + 3 < 7 ? (int)(i + 3) : 7;
            const double *w = fdw + off[npts - 3];
            const int top = npts - 1 < nhist ? npts - 1 : nhist;
            const double fac[3] = {(double)i + 2.0, 10.0 * ((double)i + 1.0),
                                   use_m1 ? (double)i : 0.0};
            const double *ucr = hr[0], *uci = hi[0];
            const double *upr = nhist > 1 ? hr[1] : NULL, *upi = nhist > 1 ? hi[1] : NULL;
            dsp_build(N, NLAM, R, e, i + 1, m, central, gcm, lam_diag, diagr, so0, ls2, so_grad,
                      so_r2, c1, c2, cd, Mnr, Mni, NHn);
            const double *nh3[3] = {NHn, NHc, use_m1 ? NHp : NHc};
            /* rhs = 2 (u_i + 5 c M_i u_i) - (u_{i-1} - c M_{i-1} u_{i-1}) + c sum_k fac_k nh3_k v3_k,
             * v3_k = sum_{m=1..top} w[k, m] u_{i+1-m}: the products first, then one pass that adds
             * the terms of every element in the order of `cc_block_d` */
            dmm_split(N, Mcr, Mci, ucr, uci, mcr, mci, 0);
            if (use_m1 && !have_mu_p)
                dmm_split(N, Mpr, Mpi, upr, upi, mpr, mpi, 0);
            double fk[3] = {0.0, 0.0, 0.0};
            for (int k = 0; k < 3; k++) {
                if (fac[k] == 0.0) {
                    memset(pr3[k], 0, (size_t)nn * sizeof(double));
                    memset(pi3[k], 0, (size_t)nn * sizeof(double));
                    continue;
                }
                const double *wk = w + k * npts;
                for (int part = 0; part < 2; part++) {
                    const double *restrict h1 = part ? hi[0] : hr[0];
                    const double *restrict h2 = part ? hi[1] : hr[1];
                    const double *restrict h3 = part ? hi[2] : hr[2];
                    const double *restrict h4 = part ? hi[3] : hr[3];
                    const double *restrict h5 = part ? hi[4] : hr[4];
                    const double *restrict h6 = part ? hi[5] : hr[5];
                    double *restrict v = part ? vi[k] : vr[k];
                    const double a1 = wk[1], a2 = top > 1 ? wk[2] : 0.0, a3 = top > 2 ? wk[3] : 0.0,
                                 a4 = top > 3 ? wk[4] : 0.0, a5 = top > 4 ? wk[5] : 0.0,
                                 a6 = top > 5 ? wk[6] : 0.0;
                    switch (top) {
                    case 1:
                        for (int64_t q = 0; q < nn; q++)
                            v[q] = a1 * h1[q];
                        break;
                    case 2:
                        for (int64_t q = 0; q < nn; q++)
                            v[q] = a1 * h1[q] + a2 * h2[q];
                        break;
                    case 3:
                        for (int64_t q = 0; q < nn; q++)
                            v[q] = a1 * h1[q] + a2 * h2[q] + a3 * h3[q];
                        break;
                    case 4:
                        for (int64_t q = 0; q < nn; q++)
                            v[q] = a1 * h1[q] + a2 * h2[q] + a3 * h3[q] + a4 * h4[q];
                        break;
                    case 5:
                        for (int64_t q = 0; q < nn; q++)
                            v[q] = a1 * h1[q] + a2 * h2[q] + a3 * h3[q] + a4 * h4[q] + a5 * h5[q];
                        break;
                    default:
                        for (int64_t q = 0; q < nn; q++)
                            v[q] = a1 * h1[q] + a2 * h2[q] + a3 * h3[q] + a4 * h4[q] + a5 * h5[q]
                                   + a6 * h6[q];
                        break;
                    }
                }
                dmm_split(N, nh3[k], NULL, vr[k], vi[k], pr3[k], pi3[k], 1);
                fk[k] = c * fac[k];
            }
            {
                const double c10 = 10.0 * c;
                const double *restrict p0r = pr3[0], *restrict p1r = pr3[1], *restrict p2r = pr3[2];
                const double *restrict p0i = pi3[0], *restrict p1i = pi3[1], *restrict p2i = pi3[2];
                if (use_m1)
                    for (int64_t q = 0; q < nn; q++) {
                        double a = 2.0 * ucr[q] + c10 * mcr[q], b = 2.0 * uci[q] + c10 * mci[q];
                        a -= upr[q] - c * mpr[q];
                        b -= upi[q] - c * mpi[q];
                        rr[q] = ((a + fk[0] * p0r[q]) + fk[1] * p1r[q]) + fk[2] * p2r[q];
                        ri[q] = ((b + fk[0] * p0i[q]) + fk[1] * p1i[q]) + fk[2] * p2i[q];
                    }
                else
                    for (int64_t q = 0; q < nn; q++) {
                        const double a = 2.0 * ucr[q] + c10 * mcr[q], b = 2.0 * uci[q] + c10 * mci[q];
                        rr[q] = (a + fk[0] * p0r[q]) + fk[1] * p1r[q];
                        ri[q] = (b + fk[0] * p0i[q]) + fk[1] * p1i[q];
                    }
            }
            /* L = 1 - c M_{i+1} - c sum_k fac_k w[k, 0] nh3_k */
            for (int64_t q = 0; q < nn; q++) {
                Lr[q] = -c * Mnr[q];
                Li[q] = -c * Mni[q];
            }
            for (int64_t a = 0; a < N; a++)
                Lr[a * N + a] += 1.0;
            {
                const double g0 = c * fac[0] * w[0], g1 = c * fac[1] * w[npts],
                             g2 = c * fac[2] * w[2 * npts];
                const double *restrict n0 = nh3[0], *restrict n1 = nh3[1], *restrict n2 = nh3[2];
                for (int64_t q = 0; q < nn; q++)
                    Lr[q] = ((Lr[q] - g0 * n0[q]) - g1 * n1[q]) - g2 * n2[q];
            }
            if (nm_solve_split(N, Lr, Li, rr, ri, unr, uni) != 0) {
                memcpy(unr, rr, (size_t)nn * sizeof(double));
                memcpy(uni, ri, (size_t)nn * sizeof(double));
                sp_solve(N, Lr, Li, unr, uni, perm);
            }
            if (i == nm) {
                sp_to_rows(N, ucr, uci, keep + 2 * (K_UM * E * nn) + e * mat);
                if (upr)
                    sp_to_rows(N, upr, upi, keep + 2 * (K_UMM1 * E * nn) + e * mat);
                sp_to_rows(N, unr, uni, keep + 2 * (K_UMP1 * E * nn) + e * mat);
                sp_to_rows(N, Mnr, Mni, keep + 2 * (K_MMP1 * E * nn) + e * mat);
                if (use_m1)
                    sp_to_rows(N, Mpr, Mpi, keep + 2 * (K_MMM1 * E * nn) + e * mat);
                else
                    sp_to_rows(N, Mcr, Mci, keep + 2 * (K_MMM1 * E * nn) + e * mat);
                for (int k = 0; k < 3; k += 2) {
                    /* s3_k = fac_k (nh3_k u_{i+1} w[k, 0] + prod_k) at r_{i+1} (k = 0), r_{i-1} (2) */
                    dmm_split(N, nh3[k], NULL, unr, uni, s3r, s3i, 1);
                    const double wk = w[k * npts];
                    for (int64_t q = 0; q < nn; q++) {
                        s3r[q] = fac[k] * (wk * s3r[q] + pr3[k][q]);
                        s3i[q] = fac[k] * (wk * s3i[q] + pi3[k][q]);
                    }
                    sp_to_rows(N, s3r, s3i,
                               keep + 2 * ((k == 0 ? K_SP1 : K_SM1) * E * nn) + e * mat);
                }
                break;
            }
            /* advance: history (the new solution takes the oldest buffer), M, NH, M u */
            double *t = hr[5], *t2 = hi[5];
            for (int k = 5; k > 0; k--) {
                hr[k] = hr[k - 1];
                hi[k] = hi[k - 1];
            }
            hr[0] = unr;
            hi[0] = uni;
            unr = t;
            uni = t2;
            if (nhist < 6)
                nhist++;
            t = Mpr; Mpr = Mcr; Mcr = Mnr; Mnr = t;
            t = Mpi; Mpi = Mci; Mci = Mni; Mni = t;
            t = NHp; NHp = NHc; NHc = NHn; NHn = t;
            t = mpr; mpr = mcr; mcr = t;
            t = mpi; mpi = mci; mci = t;
            have_mu_p = 1;
            if (i % stab == stab - 1) {
                sp_stabilise(N, hr[0], hi[0], hr + 1, hi + 1, nhist - 1, work, perm);
                have_mu_p = 0;
            }
        }
    }
    free(pool);
    return rc;
}

#endif
