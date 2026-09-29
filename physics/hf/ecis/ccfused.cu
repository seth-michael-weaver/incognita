// SPEED50B CCFUSED: the coupled-channels radial loops of `ccgpu._Side` as ONE CUDA kernel launch
// per bucket (compiled at run time by NVRTC through torch; no nvcc needed).
//
// One thread block integrates one (block, energy row) pair at a time, the whole radial loop and
// the matching inside the kernel: no per-step host launches. Each pair runs at its OWN channel
// count N (no padding). Matrices are row-major complex N x N (row = channel, column = solution),
// held in a per-thread-block global workspace (L1/L2 resident).
//
//   cc_modnum   : ccfast.c `cc_block_mn` (ECIS's modified Numerov, below soswitch)
//   cc_deformed : ccfast.c `cc_block_d` / ccgpu `_run_deformed` (implicit step with the one-sided
//                 7-point stencil for r du/dr), the implicit system solved by Gauss-Jordan with
//                 partial pivoting instead of Jacobi sweeps
// Stabilisation every STAB steps: CGS2 QR of u_i, u_i <- Q, the older solutions <- X R^-1
// (as ccgpu.py). Output per pair: U = u_m and U' at the matching point, both divided by the
// column maxima of |u_m| (ccgpu `_match`).
//
// REAL is the propagation type (double by default; the mixed-precision experiment compiles with
// -DREAL_FLOAT, accumulation and matching stay double).

#ifdef REAL_FLOAT
typedef float real;
typedef float2 creal;
#define MKC make_float2
#else
typedef double real;
typedef double2 creal;
#define MKC make_double2
#endif

#define NPMAX 128
#define STAB 15

__device__ __forceinline__ creal cfma(creal a, creal b, creal c)
{
    return MKC(c.x + a.x * b.x - a.y * b.y, c.y + a.x * b.y + a.y * b.x);
}
__device__ __forceinline__ creal cmul(creal a, creal b)
{
    return MKC(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x);
}

// C = A B (complex N x N)
__device__ void mm(int N, const creal *A, const creal *B, creal *C)
{
    const int nn = N * N;
    for (int q = threadIdx.x; q < nn; q += blockDim.x) {
        const int a = q / N, b = q - a * N;
        const creal *ar = A + a * N;
        real sr = 0, si = 0;
        for (int k = 0; k < N; k++) {
            const creal x = ar[k], y = B[k * N + b];
            sr += x.x * y.x - x.y * y.y;
            si += x.x * y.y + x.y * y.x;
        }
        C[q] = MKC(sr, si);
    }
}

// C = D B, D real
__device__ void rmm(int N, const real *D, const creal *B, creal *C)
{
    const int nn = N * N;
    for (int q = threadIdx.x; q < nn; q += blockDim.x) {
        const int a = q / N, b = q - a * N;
        const real *dr = D + a * N;
        real sr = 0, si = 0;
        for (int k = 0; k < N; k++) {
            const real x = dr[k];
            const creal y = B[k * N + b];
            sr += x * y.x;
            si += x * y.y;
        }
        C[q] = MKC(sr, si);
    }
}

struct Pair {
    int N, nlam, Rn, e;
    const real *S;      // (K NLAM, N, N) real: coupling [, so_grad, so_r2, so_deriv]
    const real *ll;     // (N,) l (l + 1)
    const real *ls2;    // (N,)
    const real *kap;    // (N,) kappa^2 of each channel at this row
    const creal *cen;   // (NLAM, Rn) mu * central
    const creal *so0;   // (Rn,) mu * spin-orbit lambda = 0
    const real *cou;    // (Rn,) mu * Coulomb
    const real *ir2;    // (Rn,) 1 / r^2
    const real *g, *qq; // (NLAM, Rn) mu * so_grad, mu * so_r2 (deformed only)
};

// M(r_i) (and NH(r_i), deformed)
__device__ void build_m(const Pair &P, int i, bool deformed, creal *M, real *NH)
{
    const int N = P.N, nn = N * N, nl = P.nlam;
    for (int q = threadIdx.x; q < nn; q += blockDim.x) {
        const int a = q / N, b = q - a * N;
        real mr = 0, mi = 0, nh = 0;
        for (int lam = 0; lam < nl; lam++) {
            const creal z = P.cen[lam * P.Rn + i];
            const real s = P.S[lam * nn + q];
            mr += z.x * s;
            mi += z.y * s;
        }
        if (deformed) {
            for (int lam = 0; lam < nl; lam++) {
                const real gv = P.g[lam * P.Rn + i], qv = P.qq[lam * P.Rn + i];
                mr += gv * P.S[(nl + lam) * nn + q] + qv * P.S[(2 * nl + lam) * nn + q];
                nh += qv * P.S[(3 * nl + lam) * nn + q];
            }
            NH[q] = nh;
        }
        if (a == b) {
            const creal so = P.so0[i];
            mr += P.ll[a] * P.ir2[i] - P.kap[a] + P.cou[i] + so.x * P.ls2[a];
            mi += so.y * P.ls2[a];
        }
        M[q] = MKC(mr, mi);
    }
}

// X <- X R^-1 for X in xs[0..nx), R upper triangular (row-major N x N)
__device__ void right_tri(int N, const creal *R, creal **xs, int nx)
{
    for (int t = threadIdx.x; t < nx * N; t += blockDim.x) {
        creal *row = xs[t / N] + (t % N) * N;
        for (int j = 0; j < N; j++) {
            creal s = row[j];
            for (int k = 0; k < j; k++) {
                const creal y = row[k], r = R[k * N + j];
                s.x -= y.x * r.x - y.y * r.y;
                s.y -= y.x * r.y + y.y * r.x;
            }
            const creal d = R[j * N + j];
            const real den = d.x * d.x + d.y * d.y;
            row[j] = MKC((s.x * d.x + s.y * d.y) / den, (s.y * d.x - s.x * d.y) / den);
        }
    }
}

__device__ __forceinline__ real warp_sum(real v)
{
    for (int o = 16; o > 0; o >>= 1)
        v += __shfl_down_sync(0xffffffffu, v, o);
    return v;
}

// A <- Q, R (upper) with A = Q R, classical Gram-Schmidt with one re-orthogonalisation (ccgpu
// `_qr_cgs2`)
__device__ void cgs2(int N, creal *A, creal *R)
{
    __shared__ creal rs[NPMAX];
    __shared__ real nrm;
    const int lane = threadIdx.x & 31, warp = threadIdx.x >> 5, nw = blockDim.x >> 5;
    for (int j = 0; j < N; j++) {
        for (int pass = 0; pass < 2 && j > 0; pass++) {
            for (int k = warp; k < j; k += nw) {
                real sr = 0, si = 0;
                for (int a = lane; a < N; a += 32) {
                    const creal q = A[a * N + k], v = A[a * N + j];
                    sr += q.x * v.x + q.y * v.y; // conj(q) v
                    si += q.x * v.y - q.y * v.x;
                }
                sr = warp_sum(sr);
                si = warp_sum(si);
                if (lane == 0) {
                    rs[k] = MKC(sr, si);
                    if (pass == 0)
                        R[k * N + j] = MKC(sr, si);
                    else
                        R[k * N + j] = MKC(R[k * N + j].x + sr, R[k * N + j].y + si);
                }
            }
            __syncthreads();
            for (int a = threadIdx.x; a < N; a += blockDim.x) {
                creal v = A[a * N + j];
                for (int k = 0; k < j; k++) {
                    const creal q = A[a * N + k], r = rs[k];
                    v.x -= q.x * r.x - q.y * r.y;
                    v.y -= q.x * r.y + q.y * r.x;
                }
                A[a * N + j] = v;
            }
            __syncthreads();
        }
        if (warp == 0) {
            real s = 0;
            for (int a = lane; a < N; a += 32) {
                const creal v = A[a * N + j];
                s += v.x * v.x + v.y * v.y;
            }
            s = warp_sum(s);
            if (lane == 0) {
                nrm = sqrt(s);
                R[j * N + j] = MKC(nrm, 0);
            }
        }
        __syncthreads();
        const real inv = 1 / nrm;
        for (int a = threadIdx.x; a < N; a += blockDim.x) {
            const creal v = A[a * N + j];
            A[a * N + j] = MKC(v.x * inv, v.y * inv);
        }
        __syncthreads();
    }
}

// X <- L^-1 X by Gauss-Jordan with partial pivoting (L destroyed). Returns false on a zero or
// non-finite pivot.
__device__ bool gj_solve(int N, creal *L, creal *X)
{
    __shared__ int piv;
    __shared__ bool bad;
    __shared__ creal f[NPMAX];
    const int lane = threadIdx.x & 31, warp = threadIdx.x >> 5;
    if (threadIdx.x == 0)
        bad = false;
    for (int k = 0; k < N; k++) {
        if (warp == 0) {
            real best = -1;
            int bi = k;
            for (int r = k + lane; r < N; r += 32) {
                const creal v = L[r * N + k];
                const real m = fabs(v.x) + fabs(v.y);
                if (m > best) {
                    best = m;
                    bi = r;
                }
            }
            for (int o = 16; o > 0; o >>= 1) {
                const real ob = __shfl_down_sync(0xffffffffu, best, o);
                const int oi = __shfl_down_sync(0xffffffffu, bi, o);
                if (ob > best || (ob == best && oi < bi)) {
                    best = ob;
                    bi = oi;
                }
            }
            if (lane == 0) {
                piv = bi;
                if (!(best > 0) || !isfinite(best))
                    bad = true;
            }
        }
        __syncthreads();
        if (bad)
            return false;
        const int p = piv;
        if (p != k) {
            for (int j = threadIdx.x; j < 2 * N; j += blockDim.x) {
                creal *A = j < N ? L : X;
                const int c = j < N ? j : j - N;
                const creal t = A[k * N + c];
                A[k * N + c] = A[p * N + c];
                A[p * N + c] = t;
            }
            __syncthreads();
        }
        // pivot row scaled; column k of the other rows kept as the elimination factors
        const creal d = L[k * N + k];
        const real den = d.x * d.x + d.y * d.y;
        const creal inv = MKC(d.x / den, -d.y / den);
        for (int r = threadIdx.x; r < N; r += blockDim.x)
            f[r] = L[r * N + k];
        __syncthreads();
        const int W = (N - k - 1) + N;
        for (int j = threadIdx.x; j < W; j += blockDim.x) {
            creal *A = j < N - k - 1 ? L : X;
            const int c = j < N - k - 1 ? k + 1 + j : j - (N - k - 1);
            A[k * N + c] = cmul(A[k * N + c], inv);
        }
        __syncthreads();
        for (int t = threadIdx.x; t < N * W; t += blockDim.x) {
            const int r = t / W, j = t - r * W;
            if (r == k)
                continue;
            creal *A = j < N - k - 1 ? L : X;
            const int c = j < N - k - 1 ? k + 1 + j : j - (N - k - 1);
            const creal fr = f[r], pk = A[k * N + c];
            creal v = A[r * N + c];
            v.x -= fr.x * pk.x - fr.y * pk.y;
            v.y -= fr.x * pk.y + fr.y * pk.x;
            A[r * N + c] = v;
        }
        __syncthreads();
    }
    return true;
}

// U, U' at the matching point from (u_{m-1}, u_m, u_{m+1}) and the second derivatives
// dd_{m+-1} (ccgpu `_match`), column-normalised, into out (2, Np, Np)
__device__ void match_out(int N, int Np, const creal *um, const creal *uc, const creal *un,
                          const creal *ddp, const creal *ddm, real c, real h, double2 *out)
{
    __shared__ real cn[NPMAX];
    for (int b = threadIdx.x; b < N; b += blockDim.x) {
        real m = 0;
        for (int a = 0; a < N; a++) {
            const creal v = uc[a * N + b];
            m = fmax(m, sqrt(v.x * v.x + v.y * v.y));
        }
        cn[b] = fmax(m, (real)1.0e-300);
    }
    __syncthreads();
    const int nn = N * N;
    for (int q = threadIdx.x; q < nn; q += blockDim.x) {
        const int a = q / N, b = q - a * N;
        const creal u = uc[q], x = un[q], y = um[q], dp = ddp[q], dm = ddm[q];
        const real du_r = ((x.x - 2 * c * dp.x) - (y.x - 2 * c * dm.x)) / (2 * h);
        const real du_i = ((x.y - 2 * c * dp.y) - (y.y - 2 * c * dm.y)) / (2 * h);
        out[a * Np + b] = make_double2(u.x / cn[b], u.y / cn[b]);
        out[Np * Np + a * Np + b] = make_double2(du_r / cn[b], du_i / cn[b]);
    }
    __syncthreads();
}

struct Args {
    int P, nlam, Rn, Np;
    const int *pb, *pe, *nm, *bN, *pOff;  // per pair: block, row, matching index, vector offset
    const long long *bOffS;               // per block: offset of its S in `S`
    const int *bOffV;                     // per block: offset of its (N,) vectors
    const real *S, *ll, *ls2;
    const real *kapP, *u1P;               // per pair (N,), packed at pOff
    const creal *cen, *so0;               // (E, NLAM, Rn), (E, Rn)
    const real *cou, *ir2, *g, *qq;       // (E, Rn), (E, Rn), (E, NLAM, Rn) x 2
    const real *cst, *hh;                 // (E,)
    const real *WW;                       // (nmax + 1, 3, 7) stencil weights x fac (deformed)
    real *ws;                             // workspace
    long long wsPer;                      // workspace per thread block, in creal
    double2 *UU;                          // (P, 2, Np, Np)
    double *rho;                          // (P,) 0 ok, inf failed
};

__device__ Pair make_pair(const Args &A, int p, bool deformed)
{
    Pair P;
    const int b = A.pb[p], e = A.pe[p];
    P.N = A.bN[b];
    P.nlam = A.nlam;
    P.Rn = A.Rn;
    P.e = e;
    P.S = A.S + A.bOffS[b];
    P.ll = A.ll + A.bOffV[b];
    P.ls2 = A.ls2 + A.bOffV[b];
    P.kap = A.kapP + A.pOff[p];
    P.cen = A.cen + (long long)e * A.nlam * A.Rn;
    P.so0 = A.so0 + (long long)e * A.Rn;
    P.cou = A.cou + (long long)e * A.Rn;
    P.ir2 = A.ir2 + (long long)e * A.Rn;
    if (deformed) {
        P.g = A.g + (long long)e * A.nlam * A.Rn;
        P.qq = A.qq + (long long)e * A.nlam * A.Rn;
    }
    return P;
}

__device__ void set_diag(int N, creal *u, const real *d)
{
    for (int q = threadIdx.x; q < N * N; q += blockDim.x) {
        const int a = q / N, b = q - a * N;
        u[q] = MKC(a == b ? d[a] : (real)0, (real)0);
    }
}

extern "C" __global__ void cc_modnum(const Args *pA)
{
    const Args A = *pA;
    creal *base = (creal *)A.ws + (long long)blockIdx.x * A.wsPer;
    const int NS = A.Np * A.Np;
    for (int p = blockIdx.x; p < A.P; p += gridDim.x) {
        const Pair P = make_pair(A, p, false);
        const int N = P.N, nn = N * N, nm = A.nm[p];
        creal *Mp = base, *Mc = base + NS, *Mn = base + 2 * NS, *up = base + 3 * NS,
              *uc = base + 4 * NS, *un = base + 5 * NS, *y = base + 6 * NS, *R = base + 7 * NS;
        const real c = A.cst[P.e], h = A.hh[P.e], c12 = 12 * c;
        set_diag(N, uc, A.u1P + A.pOff[p]);
        for (int q = threadIdx.x; q < nn; q += blockDim.x)
            up[q] = MKC((real)0, (real)0);
        build_m(P, 0, false, Mc, nullptr);
        __syncthreads();
        for (int i = 0; i <= nm; i++) {
            mm(N, Mc, uc, y); // y = M u  (scaled below)
            __syncthreads();
            for (int q = threadIdx.x; q < nn; q += blockDim.x)
                y[q] = MKC(c12 * y[q].x, c12 * y[q].y);
            __syncthreads();
            // un = y + 2 u_i - u_{i-1} + (h^2 M) y / 12
            for (int q = threadIdx.x; q < nn; q += blockDim.x) {
                const int a = q / N, b = q - a * N;
                const creal *mr = Mc + a * N;
                real sr = 0, si = 0;
                for (int k = 0; k < N; k++) {
                    const creal x = mr[k], z = y[k * N + b];
                    sr += x.x * z.x - x.y * z.y;
                    si += x.x * z.y + x.y * z.x;
                }
                const real f = c12 / 12;
                un[q] = MKC(y[q].x + 2 * uc[q].x - up[q].x + f * sr,
                            y[q].y + 2 * uc[q].y - up[q].y + f * si);
            }
            __syncthreads();
            if (i == nm) {
                build_m(P, i + 1, false, Mn, nullptr);
                __syncthreads();
                creal *Mm = i > 0 ? Mp : Mc;
                mm(N, Mn, un, y);  // dd_{m+1}
                mm(N, Mm, up, R);  // dd_{m-1}
                __syncthreads();
                match_out(N, A.Np, up, uc, un, y, R, c, h,
                          A.UU + (long long)p * 2 * A.Np * A.Np);
                if (threadIdx.x == 0)
                    A.rho[p] = 0;
                break;
            }
            creal *t = up;
            up = uc;
            uc = un;
            un = t;
            t = Mp;
            Mp = Mc;
            Mc = Mn;
            Mn = t;
            build_m(P, i + 1, false, Mc, nullptr);
            __syncthreads();
            if (i % STAB == STAB - 1) {
                cgs2(N, uc, R);
                creal *xs[1] = {up};
                right_tri(N, R, xs, 1);
                __syncthreads();
            }
        }
        __syncthreads();
    }
}

extern "C" __global__ void cc_deformed(const Args *pA)
{
    const Args A = *pA;
    creal *base = (creal *)A.ws + (long long)blockIdx.x * A.wsPer;
    const int NS = A.Np * A.Np;
    for (int p = blockIdx.x; p < A.P; p += gridDim.x) {
        const Pair P = make_pair(A, p, true);
        const int N = P.N, nn = N * N, nm = A.nm[p];
        creal *slot[7];
        for (int k = 0; k < 7; k++)
            slot[k] = base + k * NS;
        creal *Mp = base + 7 * NS, *Mc = base + 8 * NS, *Mn = base + 9 * NS;
        real *NHp = (real *)(base + 10 * NS), *NHc = (real *)(base + 11 * NS),
             *NHn = (real *)(base + 12 * NS);
        creal *mu_c = base + 13 * NS, *mu_p = base + 14 * NS, *L = base + 15 * NS,
              *V = base + 16 * NS, *ps0 = base + 17 * NS, *ps1 = base + 18 * NS,
              *ps2 = base + 19 * NS, *R = base + 20 * NS, *T1 = base + 21 * NS,
              *T2 = base + 22 * NS, *T3 = base + 23 * NS, *T4 = base + 24 * NS;
        // hist[m] = u_{i-m} lives in slot hs[m], m < nh; slot fr takes u_{i+1}
        int hs[6] = {0, 1, 2, 3, 4, 5};
        int nh = 1, fr = 6;
        const real c = A.cst[P.e], h = A.hh[P.e];
        set_diag(N, slot[hs[0]], A.u1P + A.pOff[p]);
        build_m(P, 0, true, Mc, NHc);
        __syncthreads();
        bool ok = true;
        for (int i = 0; i <= nm; i++) {
            const bool use_m1 = i != 0;
            const real *W = A.WW + i * 21;
            build_m(P, i + 1, true, Mn, NHn);
            const creal *uc = slot[hs[0]];
            const real *nh3[3] = {NHn, NHc, use_m1 ? NHp : NHc};
            const creal *Mprev = use_m1 ? Mp : Mc;
            mm(N, Mc, uc, mu_c);
            __syncthreads();
            creal *rhs = slot[fr];
            for (int q = threadIdx.x; q < nn; q += blockDim.x) {
                creal v = MKC(2 * uc[q].x + 10 * c * mu_c[q].x, 2 * uc[q].y + 10 * c * mu_c[q].y);
                if (use_m1) {
                    const creal u1 = slot[hs[1]][q], m1 = mu_p[q];
                    v.x += -u1.x + c * m1.x;
                    v.y += -u1.y + c * m1.y;
                }
                rhs[q] = v;
            }
            const int top = nh;  // = min(i + 1, 6)
            creal *psk[3] = {ps0, ps1, ps2};
            for (int k = 0; k < 3; k++) {
                for (int q = threadIdx.x; q < nn; q += blockDim.x) {
                    real vr = 0, vi = 0;
                    for (int m = 1; m <= top; m++) {
                        const real w = W[k * 7 + m];
                        const creal u = slot[hs[m - 1]][q];
                        vr += w * u.x;
                        vi += w * u.y;
                    }
                    V[q] = MKC(vr, vi);
                }
                __syncthreads();
                rmm(N, nh3[k], V, psk[k]);
                __syncthreads();
            }
            for (int q = threadIdx.x; q < nn; q += blockDim.x) {
                const int a = q / N, b = q - a * N;
                const creal s0 = ps0[q], s1 = ps1[q], s2 = ps2[q];
                rhs[q].x += c * (s0.x + s1.x + s2.x);
                rhs[q].y += c * (s0.y + s1.y + s2.y);
                // L = 1 - c M_{i+1} - c G,  G = sum_k W[k, 0] nh3_k
                const real G = W[0] * nh3[0][q] + W[7] * nh3[1][q] + W[14] * nh3[2][q];
                const creal m = Mn[q];
                L[q] = MKC((a == b ? (real)1 : (real)0) - c * m.x - c * G, -c * m.y);
            }
            __syncthreads();
            if (!gj_solve(N, L, rhs)) {
                ok = false;
                break;
            }
            creal *un = rhs;
            if (i == nm) {
                const creal *umm1 = nh > 1 ? slot[hs[1]] : nullptr;
                mm(N, Mn, un, T1);
                rmm(N, nh3[0], un, T2);
                if (umm1)
                    mm(N, Mprev, umm1, T3);
                rmm(N, nh3[2], un, T4);
                __syncthreads();
                creal *zero = L;
                for (int q = threadIdx.x; q < nn; q += blockDim.x) {
                    // dd_{m+1} = M_{m+1} u_{m+1} + s3_0, dd_{m-1} = M_{m-1} u_{m-1} + s3_2,
                    // s3_k = W[k, 0] nh3_k u_{m+1} + ps_k
                    T1[q].x += W[0] * T2[q].x + ps0[q].x;
                    T1[q].y += W[0] * T2[q].y + ps0[q].y;
                    const creal t3 = umm1 ? T3[q] : MKC((real)0, (real)0);
                    T3[q] = MKC(t3.x + W[14] * T4[q].x + ps2[q].x, t3.y + W[14] * T4[q].y + ps2[q].y);
                    zero[q] = MKC((real)0, (real)0);
                }
                __syncthreads();
                match_out(N, A.Np, umm1 ? umm1 : zero, uc, un, T1, T3, c, h,
                          A.UU + (long long)p * 2 * A.Np * A.Np);
                break;
            }
            // hist <- [un] + hist[:5]; the dropped slot (or a free one) takes the next rhs
            {
                const int drop = nh == 6 ? hs[5] : -1;
                for (int m = (nh == 6 ? 5 : nh); m > 0; m--)
                    hs[m] = hs[m - 1];
                hs[0] = fr;
                if (drop >= 0) {
                    fr = drop;
                } else {
                    nh++;
                    int used[7] = {0, 0, 0, 0, 0, 0, 0};
                    for (int m = 0; m < nh; m++)
                        used[hs[m]] = 1;
                    fr = 0;
                    while (used[fr])
                        fr++;
                }
            }
            creal *t = mu_p;
            mu_p = mu_c;
            mu_c = t;
            t = Mp;
            Mp = Mc;
            Mc = Mn;
            Mn = t;
            real *tr = NHp;
            NHp = NHc;
            NHc = NHn;
            NHn = tr;
            __syncthreads();
            if (i % STAB == STAB - 1) {
                cgs2(N, slot[hs[0]], R);
                creal *xs[6];
                int nx = 0;
                for (int m = 1; m < nh; m++)
                    xs[nx++] = slot[hs[m]];
                xs[nx++] = mu_p;
                right_tri(N, R, xs, nx);
                __syncthreads();
            }
        }
        if (threadIdx.x == 0)
            A.rho[p] = ok ? 0.0 : __longlong_as_double(0x7ff0000000000000LL);
        __syncthreads();
    }
}
