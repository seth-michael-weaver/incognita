/* CCPROP (ROUTE100 WP8): the log-derivative propagator of one coupled-channels (J, parity) block,
 * as the candidate replacement for the renormalised Numerov step of `ccfast.c::cc_block_w`.
 *
 * It exists so that CCPROP's gate-1 FLOP claim is made about code that runs, not about a count on
 * paper. `physics/hf/ecis/ccprop.py` is the same method in torch and the two agree; the verdict on
 * both is a kill (`docs/results/hf-ccprop.md`).
 *
 * What it computes: Y = u' u^-1 at each energy's matching radius, which is exactly the `L` that
 * `solver._match` forms from the Numerov loop's kept solutions. The recursion over ECIS's own
 * radial grid is, per step,
 *
 *     kick    Y <- Y + w_i Mtilde_i          (w_i the composite Simpson weight of the node)
 *     drift   Y <- (1/h) 1 - (1/h^2) (Y + (1/h) 1)^-1
 *
 * so the step is **one complex matrix inverse** (zgetrf + zgetri) and O(N^2) besides -- no zgemm,
 * and no QR, because a log derivative cannot lose the linear independence that the Numerov loop's
 * stabilisation exists to restore. `Mtilde = (1 + h^2 M / 6)^-1 M` at the panel midpoints
 * (`CC_PROP_MODIFIED`), which is Johnson's reference-potential correction and one further
 * zgetrf + zgetrs every second step.
 *
 * `cc_prop_flops` returns the FLOPs the last call issued, counted from the LAPACK calls it made at
 * the dimensions it made them with, so `harness/ccprop_flops.py`'s model can be checked against
 * the kernel instead of trusted.
 *
 * Build: scripts/build_ccprop_native.sh -> physics/hf/native/lib/libccprop.so (gitignored).
 * LAPACK comes from torch by address, exactly as `ccfast.c` takes it.
 */

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef void (*zgetrf_t)(const int *, const int *, double *, const int *, int *, int *);
typedef void (*zgetri_t)(const int *, double *, const int *, const int *, double *, const int *,
                         int *);
typedef void (*zgetrs_t)(const char *, const int *, const int *, const double *, const int *,
                         const int *, double *, const int *, int *);

static zgetrf_t zgetrf_p;
static zgetri_t zgetri_p;
static zgetrs_t zgetrs_p;

int cc_prop_version(void) { return 1; }

void cc_prop_set_lapack(void *zgetrf, void *zgetri, void *zgetrs)
{
    zgetrf_p = (zgetrf_t)zgetrf;
    zgetri_p = (zgetri_t)zgetri;
    zgetrs_p = (zgetrs_t)zgetrs;
}

/* FLOPs of the last call, in the counts docs/results/hf-ccprop.md registers:
 * zgetrf (8/3) N^3, zgetri (16/3) N^3, zgetrs with N right-hand sides 8 N^3. */
static double flops_acc;
double cc_prop_flops(void) { return flops_acc; }

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
    const double *diagr;   /* (E, R, N) real */
    const double *so0;     /* (E, R) complex */
    const double *ls2;     /* (N,) real */
    const double *mu;      /* (E,) */
} blk_t;

/* M(r_i) at energy e, column-major complex -- `ccfast.c::build_m`, unchanged. */
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

/* A <- A^-1, column-major complex.
 *
 * zgetrf + zgetri is (8/3 + 16/3) N^3 = 8 N^3, the textbook complex inversion and the count the
 * gate model uses. torch's CPU library re-exports zgetrf and zgetrs but NOT zgetri, so when the
 * loader could not find it the kernel falls back to zgetrs against an identity right-hand side --
 * the same result, (8/3 + 8) N^3 = 10.67 N^3. `cc_prop_flops` reports whichever was issued, so the
 * gap between the kernel and the model is visible rather than hidden: the model is the one that
 * flatters the propagator. */
static int invert(int64_t N, double *A, int *piv, double *work, int lwork)
{
    const int n = (int)N;
    const double n3 = (double)N * (double)N * (double)N;
    int info = 0;
    zgetrf_p(&n, &n, A, &n, piv, &info);
    if (info != 0)
        return -1;
    if (zgetri_p) {
        zgetri_p(&n, A, &n, piv, work, &lwork, &info);
        if (info != 0)
            return -1;
        flops_acc += 8.0 * n3;
        return 0;
    }
    memset(work, 0, (size_t)(2 * N * N) * sizeof(double));
    for (int64_t a = 0; a < N; a++)
        work[2 * (a * N + a)] = 1.0;
    zgetrs_p("N", &n, &n, A, &n, piv, work, &n, &info);
    if (info != 0)
        return -1;
    memcpy(A, work, (size_t)(2 * N * N) * sizeof(double));
    flops_acc += (8.0 / 3.0 + 8.0) * n3;
    return 0;
}

/* B <- A^-1 B for N right-hand sides. (8/3) N^3 + 8 N^3. */
static int solve(int64_t N, double *A, double *B, int *piv)
{
    const int n = (int)N;
    int info = 0;
    zgetrf_p(&n, &n, A, &n, piv, &info);
    if (info != 0)
        return -1;
    zgetrs_p("N", &n, &n, A, &n, piv, B, &n, &info);
    flops_acc += (8.0 / 3.0 + 8.0) * (double)N * (double)N * (double)N;
    return 0;
}

/* One block, every energy.
 *   E, N, R, NLAM and central..mu as `ccfast.c::cc_block_w`
 *   lp1     : (N,) real, l_c + 1
 *   h       : (E,) step;  nmatch: (E,) matching index (r_match = h (nmatch + 1))
 *   modified: 1 to apply (1 + h^2 M / 6)^-1 M at the panel midpoints (fourth-order correction
 *             attempt), 0 for the bare kick-and-drift rule
 *   L       : (E, N, N) complex row-major output, Y = u' u^-1 at the matching radius
 * Returns 0; -1 out of memory or a singular step.
 *
 * An energy whose `nmatch` is odd starts one node later (r = 2h), so that the number of sectors up
 * to its matching node is even and the composite Simpson weights close properly. Nothing moves off
 * ECIS's grid.
 */
int cc_prop_w(int64_t E, int64_t N, int64_t R, int64_t NLAM, const double *central,
              const double *cpl, const double *diagr, const double *so0, const double *ls2,
              const double *mu, const double *lp1, const double *h, const int64_t *nmatch,
              int64_t modified, double *L)
{
    const int64_t nn = N * N, mat = 2 * nn;
    blk_t b = {N, NLAM, R, central, cpl, diagr, so0, ls2, mu};
    int rc = -1;
    const int lwork = (int)(zgetri_p ? 64 * N : N * N);
    double *Y = zalloc(nn), *M = zalloc(nn), *T = zalloc(nn), *Q = zalloc(nn);
    double *work = zalloc(lwork);
    int *piv = malloc(sizeof(int) * (size_t)N);
    if (!Y || !M || !T || !Q || !work || !piv)
        goto done;
    flops_acc = 0.0;
    for (int64_t e = 0; e < E; e++) {
        const int64_t nm = nmatch[e];
        if (nm + 2 > R)
            goto done;
        const int64_t start = nm % 2;
        const double hh = h[e], hi = 1.0 / hh, w3 = hh / 3.0, c6 = hh * hh / 6.0;
        const double r0 = hh * (double)(start + 1);
        memset(Y, 0, (size_t)mat * sizeof(double));
        for (int64_t a = 0; a < N; a++)
            Y[2 * (a * N + a)] = lp1[a] / r0;
        for (int64_t i = start; i <= nm; i++) {
            const int64_t p = i - start;
            const int mid = (p % 2) == 1;
            const double wt = mid ? 4.0 : ((p == 0 || i == nm) ? 1.0 : 2.0);
            build_m(&b, e, i, M);
            const double *use = M;
            if (mid && modified) {
                /* Q = (1 + h^2 M / 6)^-1 M */
                for (int64_t q = 0; q < mat; q++)
                    T[q] = c6 * M[q];
                for (int64_t a = 0; a < N; a++)
                    T[2 * (a * N + a)] += 1.0;
                memcpy(Q, M, (size_t)mat * sizeof(double));
                if (solve(N, T, Q, piv))
                    goto done;
                use = Q;
            }
            const double f = w3 * wt;
            for (int64_t q = 0; q < mat; q++)
                Y[q] += f * use[q];
            if (i == nm)
                break;
            /* drift: Y <- hi 1 - hi^2 (Y + hi 1)^-1 */
            for (int64_t a = 0; a < N; a++)
                Y[2 * (a * N + a)] += hi;
            if (invert(N, Y, piv, work, lwork))
                goto done;
            const double s = -hi * hi;
            for (int64_t q = 0; q < mat; q++)
                Y[q] *= s;
            for (int64_t a = 0; a < N; a++)
                Y[2 * (a * N + a)] += hi;
        }
        /* column-major -> row-major into L[e] */
        for (int64_t a = 0; a < N; a++)
            for (int64_t c = 0; c < N; c++) {
                L[2 * ((e * N + a) * N + c)] = Y[2 * (c * N + a)];
                L[2 * ((e * N + a) * N + c) + 1] = Y[2 * (c * N + a) + 1];
            }
    }
    rc = 0;
done:
    free(Y); free(M); free(T); free(Q); free(work); free(piv);
    return rc;
}
