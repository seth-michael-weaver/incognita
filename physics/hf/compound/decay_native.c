/* SPEEDD: compiled kernels for compound.decay_fast (the multiple-emission compound decay).
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * compound.f90's feeding of one mother bin (and of a batch of them), as decay_fast.py arranges it:
 * the same sums over the same terms, with the loops written out so that zero cells are skipped and
 * no temporary is allocated. (The widths' denominators stay numpy/torch in decay_fast: the same
 * loops in C moved the golden's feedexcl by 1.3e-15, past the speed wave's 1e-15 rule.)
 * Sums are taken in loop order rather than BLAS order, so results move by rounding only (tested
 * against the numpy path at 1e-13 in tests/hf/test_decay_fast.py; the golden is the end-to-end
 * check). Arrays are C-contiguous float64 / int64 / uint8.
 *
 * Spin-l' selection: a mother cell J reaches residual spin index i through
 * lbeg[J*jx + i] <= l' <= lend[J*jx + i] (continuum._spin_l_mask). The parity index c of a
 * transmission is either an explicit axis (C == 2, the photon: T[b, c, n, l]) or the parity of
 * l' (C == 1, a particle: T[b, n, l], c = l mod 2).
 */
#include <stdint.h>
#include <string.h>

int dk_version(void) { return 1; }

static inline int64_t imin(int64_t a, int64_t b) { return a < b ? a : b; }

/* compound.f90's feeding of bins rows[0..B-1] by F[b, J, P] (J < nj): for every row n, residual
 * spin i and residual parity q,
 *   dp[b, n, i, q] = sfac rho[row, n, i, q] sum_l' (T_0[row, n, l'] V[i, q, l'] + T_1 V[i, 1-q, l'])
 * with V[i, q, l'] = sum over J reaching (i, l') of F[b, J, q]; the discrete levels k < nd add
 * sfac rho_d[row, k] (sum_J tot0 F[J, pd] + sum_J tot1 F[J, 1 - pd]) at (k, ird[k], pd[k]);
 * mc[b, n] = sum over (i, q) of dp[b, n, i, q]. V is work space (jx, 2, L). */
void dk_contract(int64_t B, const int64_t *rows, int64_t n, int64_t jx, int64_t np_, int64_t L,
                 int64_t nj, int64_t C, const double *F, const int64_t *lbeg, const int64_t *lend,
                 const double *T, const double *rho, double sfac, int64_t nd, const double *tot0,
                 const double *tot1, const double *rho_d, const int64_t *ird, const int64_t *pd,
                 int64_t njd, double *V, double *dp, double *mc)
{
    for (int64_t b = 0; b < B; b++) {
        int64_t row = rows[b];
        const double *Fb = F + b * nj * 2;
        memset(V, 0, (size_t)(jx * 2 * L) * sizeof(double));
        for (int64_t i = 0; i < jx; i++) {
            for (int64_t J = 0; J < nj; J++) {
                int64_t lb = lbeg[J * jx + i], le = imin(lend[J * jx + i], L - 1);
                if (lb > le) continue;
                for (int64_t q = 0; q < 2; q++) {
                    double f = Fb[J * 2 + q];
                    if (f == 0.0) continue;
                    double *Vo = V + (i * 2 + q) * L;
                    for (int64_t l = lb; l <= le; l++) Vo[l] += f;
                }
            }
        }
        double *dpb = dp + b * n * jx * 2;
        for (int64_t k = 0; k < n; k++) {
            const double *rk = rho + ((row * n + k) * jx) * np_;
            const double *T0, *T1;
            if (C == 1) { T0 = T + (row * n + k) * L; T1 = T0; }
            else { T0 = T + ((row * 2 + 0) * n + k) * L; T1 = T + ((row * 2 + 1) * n + k) * L; }
            for (int64_t i = 0; i < jx; i++) {
                for (int64_t q = 0; q < 2; q++) {
                    double r = rk[i * np_ + (np_ == 1 ? 0 : q)];
                    double out = 0.0;
                    if (r != 0.0) {
                        const double *Vq = V + (i * 2 + q) * L, *Vn = V + (i * 2 + 1 - q) * L;
                        double tv;
                        if (C == 1) {
                            tv = 0.0;
                            for (int64_t l = 0; l < L; l++) tv += T0[l] * ((l & 1) ? Vn[l] : Vq[l]);
                        } else {
                            double s0 = 0.0, s1 = 0.0;
                            for (int64_t l = 0; l < L; l++) { s0 += T0[l] * Vq[l]; s1 += T1[l] * Vn[l]; }
                            tv = s0 + s1;
                        }
                        out = sfac * r * tv;
                    }
                    dpb[(k * jx + i) * 2 + q] = out;
                }
            }
        }
        for (int64_t k = 0; k < nd; k++) {
            double r = rho_d[row * nd + k];
            if (r == 0.0) continue;
            double a = 0.0, c = 0.0;
            for (int64_t J = 0; J < nj; J++) {
                a += Fb[J * 2 + pd[k]] * tot0[(row * njd + J) * nd + k];
                c += Fb[J * 2 + 1 - pd[k]] * tot1[(row * njd + J) * nd + k];
            }
            dpb[(k * jx + ird[k]) * 2 + pd[k]] += sfac * r * (a + c);
        }
        for (int64_t k = 0; k < n; k++) {
            double s = 0.0;
            for (int64_t i = 0; i < jx; i++) s += dpb[(k * jx + i) * 2] + dpb[(k * jx + i) * 2 + 1];
            mc[b * n + k] = s;
        }
    }
}

/* The feed of one mother bin: active cells (pop >= popeps_b), compound.f90:222's dead cells (no
 * exit but alpha, alpha then closed too), the denominator, and feed = pop / denom where live.
 * Returns bit 0 = some cell dead, bit 1 = some active cell with no exit at all (trapped). */
int dk_feed(int64_t nj, const double *pop, double popeps_b, const double *dsum6,
            const uint8_t *zero6, const double *d6, double *feed, uint8_t *dead)
{
    int any_dead = 0, trapped = 0;
    for (int64_t x = 0; x < nj * 2; x++) {
        int active = pop[x] >= popeps_b;
        dead[x] = (uint8_t)(active && zero6[x]);
        any_dead |= dead[x];
    }
    for (int64_t x = 0; x < nj * 2; x++) {
        int active = pop[x] >= popeps_b;
        double denom = dsum6[x];
        if (d6) denom = any_dead ? denom + (dead[x] ? 0.0 : d6[x]) : denom + d6[x];
        int live = active && pop[x] != 0.0 && denom != 0.0;
        feed[x] = live ? pop[x] / denom : 0.0;
        if (active && pop[x] != 0.0 && denom == 0.0) trapped = 1;
    }
    return any_dead | (trapped << 1);
}

/* One bin of the photon exit in one call: dk_feed, then dk_contract for this bin alone.
 * ip: n, jx, np, L, C, nd, njd, closed, has_d6;  pp: lbeg, lend, T, rho, tot0, tot1, rho_d, ird,
 * pd, dsum6, zero6, d6 (the last three for all bins, stride njd * 2);  sfac in dpar[0].
 * Returns dk_feed's flags; dp/mc are written only when the exit is open and nothing is trapped. */
int dk_bin_photon(const int64_t *ip, const uint64_t *pp, const double *dpar, int64_t row,
                  int64_t nj, const double *pop, double popeps_b, double *feed, uint8_t *dead,
                  double *V, double *dp, double *mc)
{
    int64_t n = ip[0], jx = ip[1], np_ = ip[2], L = ip[3], C = ip[4], nd = ip[5], njd = ip[6];
    int64_t closed = ip[7], has_d6 = ip[8];
    const double *dsum6 = (const double *)pp[9] + row * njd * 2;
    const uint8_t *zero6 = (const uint8_t *)pp[10] + row * njd * 2;
    const double *d6 = has_d6 ? (const double *)pp[11] + row * njd * 2 : 0;
    int flags = dk_feed(nj, pop, popeps_b, dsum6, zero6, d6, feed, dead);
    if (closed || (flags & 2)) return flags;
    dk_contract(1, &row, n, jx, np_, L, nj, C, feed, (const int64_t *)pp[0], (const int64_t *)pp[1],
                (const double *)pp[2], (const double *)pp[3], dpar[0], nd, (const double *)pp[4],
                (const double *)pp[5], (const double *)pp[6], (const int64_t *)pp[7],
                (const int64_t *)pp[8], njd, V, dp, mc);
    return flags;
}
