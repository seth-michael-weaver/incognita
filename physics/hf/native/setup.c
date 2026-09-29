/* CENGSETUP (ROUTE100 WP9): the set-up kernels of a nuclide (DWBA levels, the inverse channels'
 * inward Coulomb Numerov) laid out for the vector units, built by scripts/build_setup_native.sh
 * with -O3 and, on x86 with AVX2 + FMA, -mavx2 -mfma; always -std=c11 -ffp-contract=off, so no
 * product is fused and no sum is reordered. Every function returns the bits of the kernel it
 * stands in for (the wrappers fall back to that kernel when this library is not built).
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 * ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license.
 *
 * cs_dwba_levels -- `nx2_dwba_levels` (native/nx2_dwba.c), same arguments, same bits:
 *   * the Numerov rows of one energy advance in groups of four: 1 / D_i of a row is one
 *     vectorised pass over its steps, then the group's recurrence steps its four rows as one
 *     AVX2 vector (nx2 stepped every row together, one scalar row after another, so each step
 *     touched every row's arrays);
 *   * the overlap sums keep nx2's four accumulation lanes (lane m takes the radii i = m mod 4,
 *     the tail goes to lane 0, then (l0 + l1) + (l2 + l3)); the four lanes are one AVX2 vector,
 *     on separate real and imaginary arrays.
 * cs_numerov_inward -- `hf_numerov_inward` (native/hfnative.c) on columns of one step count, eight
 *   columns per step instead of four (the recurrence carries one division per step, so the
 *   out-of-order core runs twice the lanes side by side); every column has the arithmetic of
 *   hfnative's scalar and AVX2 forms, which agree bit for bit when the step counts are equal.
 *   Columns whose step count differs from the first column's go to the scalar form. On arm64
 *   (no `__AVX2__`) this file has no matching NEON form for hfnative.c's `#if HF_NEON` path, so
 *   it runs the plain scalar loop there instead; measured against hfnative's NEON output
 *   (MACFIX2) that lands within 3.2e-15 relative, not bit-identical -- reasonably close, per the
 *   project's tolerance standard (tests/hf/test_cengsetup.py::test_numerov_inward_bitwise).
 *
 * The build also compiles nx2_omp.c and nx2_preeq.c into the same library, unchanged: the flags
 * alone (fma() inlined, the (row, j) loops vectorised) change their speed and not their bits.
 *
 * TALYS: directecis.f90:1 (directecis), ecist.f:18285 (inri), ecist.f:5775 (fcou)
 * Test: tests/hf/test_cengsetup.py */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#if defined(__AVX2__)
#include <immintrin.h>
#endif

/* ------------------------------------------------------------------------------------- DWBA */

/* H+ and k H+' at rho for L = 0..lmax, eta = 0 (nx2_dwba_neutral) */
static void cs_dwba_neutral(double rho, int64_t lmax, int64_t ltop, double k, double *fbuf,
                            double *out, int64_t nlj, const int64_t *l)
{
    const double inv = 1.0 / rho;
    double f = (double)(ltop + 1) * inv;
    for (int64_t L = ltop; L >= 1; L--) {
        const double S = (double)L * inv;
        double d = S + f;
        if (fabs(d) < 1.0e-290)
            d = 1.0e-290;
        f = S - 1.0 / d;
        if (L - 1 <= lmax)
            fbuf[L - 1] = f;
    }
    double *G = fbuf + (lmax + 1), *dG = fbuf + 2 * (lmax + 1);
    G[0] = cos(rho);
    dG[0] = -sin(rho);
    for (int64_t L = 1; L <= lmax; L++) {
        const double S = inv * (double)L;
        G[L] = S * G[L - 1] - dG[L - 1];
        dG[L] = G[L - 1] - S * G[L];
    }
    for (int64_t c = 0; c < nlj; c++) {
        const int64_t L = l[c];
        const double F = 1.0 / (fbuf[L] * G[L] - dG[L]);
        const double dF = fbuf[L] * F;
        out[4 * c] = G[L];
        out[4 * c + 1] = F;
        out[4 * c + 2] = dG[L] * k;
        out[4 * c + 3] = dF * k;
    }
}

#ifndef CS_CHUNK
#define CS_CHUNK 4
#endif
/* rows stepped together (one AVX2 vector) */

typedef struct {
    double *er, *ei;               /* 1 / D_i per (row, step), stride S */
    double *yr, *yi;               /* y per (row, step), stride S */
} cs_waves_buf;

/* nx2_dwba_waves: y (row, step; re and im arrays) and 1 / C per row */
static void cs_dwba_waves(int64_t n, double h, const double *f, double k2, double kabs,
                          const double *y1, const double *hp, int64_t nrow, const int64_t *rows,
                          cs_waves_buf *b, double *invc)
{
    const int64_t S = n + 1;
    const double c = h * h / 12.0;
    for (int64_t m = 0; m < nrow; m++) {
        const double *restrict fr = f + 2 * S * rows[m];
        double *restrict emr = b->er + S * m, *restrict emi = b->ei + S * m;
        for (int64_t i = 1; i < S; i++) {
            const double dr = 1.0 - c * (fr[2 * i] - k2), di = -c * fr[2 * i + 1];
            const double s = 1.0 / (dr * dr + di * di);
            emr[i] = dr * s;
            emi[i] = -di * s;
        }
    }
    for (int64_t m0 = 0; m0 < nrow; m0 += CS_CHUNK) {
        const int ch = (int)(nrow - m0 < CS_CHUNK ? nrow - m0 : CS_CHUNK);
        double z0r[CS_CHUNK], z0i[CS_CHUNK], z1r[CS_CHUNK], z1i[CS_CHUNK];
        const double *er[CS_CHUNK], *ei[CS_CHUNK];
        double *yr[CS_CHUNK], *yi[CS_CHUNK];
        for (int j = 0; j < ch; j++) {
            const int64_t m = m0 + j;
            const double *fr = f + 2 * S * rows[m];
            er[j] = b->er + S * m;
            ei[j] = b->ei + S * m;
            yr[j] = b->yr + S * m;
            yi[j] = b->yi + S * m;
            const double y1m = y1[rows[m]];
            yr[j][0] = 0.0;
            yi[j][0] = 0.0;
            yr[j][1] = y1m;
            yi[j][1] = 0.0;
            z0r[j] = 0.0;
            z0i[j] = 0.0;
            z1r[j] = (1.0 - c * (fr[2] - k2)) * y1m;
            z1i[j] = -c * fr[3] * y1m;
        }
#if defined(__AVX2__)
        if (ch == 4 && n > 1) {
            /* the same step on one vector of the four rows */
            const __m256d twelve = _mm256_set1_pd(12.0), ten = _mm256_set1_pd(10.0);
            __m256d vz0r = _mm256_loadu_pd(z0r), vz0i = _mm256_loadu_pd(z0i);
            __m256d vz1r = _mm256_loadu_pd(z1r), vz1i = _mm256_loadu_pd(z1i);
            __m256d cer = _mm256_set_pd(er[3][1], er[2][1], er[1][1], er[0][1]);
            __m256d cei = _mm256_set_pd(ei[3][1], ei[2][1], ei[1][1], ei[0][1]);
            double tr_[4], ti_[4];
            for (int64_t i = 1; i < n; i++) {
                const __m256d tr = _mm256_sub_pd(_mm256_mul_pd(twelve, cer), ten);
                const __m256d ti = _mm256_mul_pd(twelve, cei);
                const __m256d nr = _mm256_sub_pd(
                    _mm256_sub_pd(_mm256_mul_pd(tr, vz1r), _mm256_mul_pd(ti, vz1i)), vz0r);
                const __m256d ni = _mm256_sub_pd(
                    _mm256_add_pd(_mm256_mul_pd(tr, vz1i), _mm256_mul_pd(ti, vz1r)), vz0i);
                vz0r = vz1r;
                vz0i = vz1i;
                vz1r = nr;
                vz1i = ni;
                cer = _mm256_set_pd(er[3][i + 1], er[2][i + 1], er[1][i + 1], er[0][i + 1]);
                cei = _mm256_set_pd(ei[3][i + 1], ei[2][i + 1], ei[1][i + 1], ei[0][i + 1]);
                _mm256_storeu_pd(tr_, _mm256_sub_pd(_mm256_mul_pd(nr, cer), _mm256_mul_pd(ni, cei)));
                _mm256_storeu_pd(ti_, _mm256_add_pd(_mm256_mul_pd(nr, cei), _mm256_mul_pd(ni, cer)));
                for (int j = 0; j < 4; j++) {
                    yr[j][i + 1] = tr_[j];
                    yi[j][i + 1] = ti_[j];
                }
            }
            continue;
        }
#endif
        for (int64_t i = 1; i < n; i++) {
            for (int j = 0; j < ch; j++) {
                const double tr = 12.0 * er[j][i] - 10.0, ti = 12.0 * ei[j][i];
                const double zr = z1r[j], zi = z1i[j];
                const double nr = (tr * zr - ti * zi) - z0r[j];
                const double ni = (tr * zi + ti * zr) - z0i[j];
                z0r[j] = zr;
                z0i[j] = zi;
                z1r[j] = nr;
                z1i[j] = ni;
                const double ern = er[j][i + 1], ein = ei[j][i + 1];
                yr[j][i + 1] = nr * ern - ni * ein;
                yi[j][i + 1] = nr * ein + ni * ern;
            }
        }
    }
    for (int64_t m = 0; m < nrow; m++) {
        const double *fr = f + 2 * S * rows[m];
        const double *H = hp + 4 * rows[m];
        const double *yr = b->yr + S * m, *yi = b->yi + S * m;
        double a2 = 0.0;
        for (int64_t i = n - 2; i <= n; i++) {
            const double a = yr[i] * yr[i] + yi[i] * yi[i];
            a2 = a > a2 ? a : a2;
        }
        double amax = sqrt(a2);
        if (!(amax >= 1.0e-300))
            amax = 1.0e-300;
        const double sc = 1.0 / amax;
        const double fpr = fr[2 * n] - k2, fpi = fr[2 * n + 1];
        const double fqr = fr[2 * (n - 2)] - k2, fqi = fr[2 * (n - 2) + 1];
        const double ynr = yr[n] * sc, yni = yi[n] * sc;
        const double yqr = yr[n - 2] * sc, yqi = yi[n - 2] * sc;
        const double ymr = yr[n - 1] * sc, ymi = yi[n - 1] * sc;
        const double er_ = 1.0 - 2.0 * c * fpr, ei_ = -2.0 * c * fpi;
        const double gr = 1.0 - 2.0 * c * fqr, gi = -2.0 * c * fqi;
        const double dyr = ((ynr * er_ - yni * ei_) - (yqr * gr - yqi * gi)) / (2.0 * h);
        const double dyi = ((ynr * ei_ + yni * er_) - (yqr * gi + yqi * gr)) / (2.0 * h);
        const double numr = (ymr * H[2] - ymi * H[3]) - (dyr * H[0] - dyi * H[1]);
        const double numi = (ymr * H[3] + ymi * H[2]) - (dyr * H[1] + dyi * H[0]);
        const double cr = numi / (2.0 * kabs), ci = -numr / (2.0 * kabs);
        const double t = 1.0 / (cr * cr + ci * ci);
        invc[2 * m] = cr * t * sc;
        invc[2 * m + 1] = -ci * t * sc;
    }
}

/* nx2_dwba_dot on split arrays: sum_i u_i v_i over S radii, nx2's four lanes */
static inline void cs_dwba_dot(const double *ur, const double *ui, const double *vr,
                               const double *vi, int64_t S, double *re, double *im)
{
    double sr[4] = {0.0, 0.0, 0.0, 0.0}, si[4] = {0.0, 0.0, 0.0, 0.0};
    int64_t i = 0;
#if defined(__AVX2__)
    __m256d ar = _mm256_setzero_pd(), ai = _mm256_setzero_pd();
    for (; i + 4 <= S; i += 4) {
        const __m256d a = _mm256_loadu_pd(ur + i), b = _mm256_loadu_pd(ui + i);
        const __m256d p = _mm256_loadu_pd(vr + i), q = _mm256_loadu_pd(vi + i);
        ar = _mm256_add_pd(ar, _mm256_sub_pd(_mm256_mul_pd(a, p), _mm256_mul_pd(b, q)));
        ai = _mm256_add_pd(ai, _mm256_add_pd(_mm256_mul_pd(a, q), _mm256_mul_pd(b, p)));
    }
    _mm256_storeu_pd(sr, ar);
    _mm256_storeu_pd(si, ai);
#else
    for (; i + 4 <= S; i += 4)
        for (int m = 0; m < 4; m++) {
            sr[m] += ur[i + m] * vr[i + m] - ui[i + m] * vi[i + m];
            si[m] += ur[i + m] * vi[i + m] + ui[i + m] * vr[i + m];
        }
#endif
    for (; i < S; i++) {
        sr[0] += ur[i] * vr[i] - ui[i] * vi[i];
        si[0] += ur[i] * vi[i] + ui[i] * vr[i];
    }
    *re = (sr[0] + sr[1]) + (sr[2] + sr[3]);
    *im = (si[0] + si[1]) + (si[2] + si[3]);
}

int cs_dwba_levels(int64_t nlj, int64_t n, double h, const double *f, const double *y1,
                   const int64_t *l, int64_t nk, const double *kappa2, const double *eta,
                   const double *hp_in, double rm, const double *ww, int64_t ntab,
                   const double *tab, const int64_t *tab_of, double *out)
{
    const int64_t S = n + 1;
    int64_t lmax = 0;
    for (int64_t c = 0; c < nlj; c++)
        if (l[c] > lmax)
            lmax = l[c];
    int64_t qmax = 0;
    for (int64_t t = 0; t < ntab * nlj * nlj; t++)
        if (tab[t] != 0.0 && t % nlj + 1 > qmax)
            qmax = t % nlj + 1;
    const size_t nr = (size_t)(nlj > 0 ? nlj : 1), SS = (size_t)S;
    double *hp = NULL, *fbuf = NULL;
    cs_waves_buf b = {0};
    double *wbuf = malloc(sizeof(double) * 4 * SS * nr);
    double *vr = malloc(sizeof(double) * SS * nr), *vi = malloc(sizeof(double) * SS * nr);
    double *invc = malloc(sizeof(double) * 2 * nr);
    int64_t *rows = calloc(nr, sizeof(int64_t));
    int rc = -1;
    if (wbuf == NULL || vr == NULL || vi == NULL || invc == NULL || rows == NULL)
        goto done;
    b.er = wbuf;
    b.ei = wbuf + SS * nr;
    b.yr = wbuf + 2 * SS * nr;
    b.yi = wbuf + 3 * SS * nr;
    if (hp_in == NULL) {
        double rho_max = 0.0;
        for (int64_t k = 0; k < nk; k++) {
            if (eta[k] != 0.0) {
                rc = -2;
                goto done;
            }
            const double rho = sqrt(fabs(kappa2[k])) * rm;
            rho_max = rho > rho_max ? rho : rho_max;
        }
        const int64_t ltop = lmax + (int64_t)rho_max + 60;
        hp = malloc(sizeof(double) * 4 * (size_t)(nk * nlj));
        fbuf = malloc(sizeof(double) * (size_t)(3 * (lmax + 1) + ltop + 1));
        if (hp == NULL || fbuf == NULL)
            goto done;
        for (int64_t k = 0; k < nk; k++) {
            const double kk = sqrt(fabs(kappa2[k]));
            cs_dwba_neutral(kk * rm, lmax, ltop, kk, fbuf, hp + 4 * k * nlj, nlj, l);
        }
    }
    const double *H = hp_in != NULL ? hp_in : hp;
    /* entrance channels 0..qmax-1: v_q = u_q W wt */
    for (int64_t q = 0; q < qmax; q++)
        rows[q] = q;
    if (qmax > 0) {
        cs_dwba_waves(n, h, f, kappa2[0], sqrt(fabs(kappa2[0])), y1, H, qmax, rows, &b, invc);
        for (int64_t q = 0; q < qmax; q++) {
            const double cr = invc[2 * q], ci = invc[2 * q + 1];
            double *restrict oq_r = vr + S * q, *restrict oq_i = vi + S * q;
            const double *restrict yr = b.yr + S * q, *restrict yi = b.yi + S * q;
            for (int64_t i = 0; i < S; i++) {
                const double y_r = yr[i], y_i = yi[i];
                const double ar = y_r * cr - y_i * ci;
                const double ai = y_r * ci + y_i * cr;
                oq_r[i] = ar * ww[2 * i] - ai * ww[2 * i + 1];
                oq_i[i] = ar * ww[2 * i + 1] + ai * ww[2 * i];
            }
        }
    }
    for (int64_t k = 1; k < nk; k++) {
        const double *w = tab + tab_of[k - 1] * nlj * nlj;
        int64_t np = 0;
        for (int64_t p = 0; p < nlj; p++)
            for (int64_t q = 0; q < qmax; q++)
                if (w[p * nlj + q] != 0.0) {
                    rows[np++] = p;
                    break;
                }
        double sum = 0.0;
        if (np > 0) {
            cs_dwba_waves(n, h, f, kappa2[k], sqrt(fabs(kappa2[k])), y1, H + 4 * k * nlj, np,
                          rows, &b, invc);
            for (int64_t m = 0; m < np; m++) {
                const double *wp = w + rows[m] * nlj;
                const double cr = invc[2 * m], ci = invc[2 * m + 1];
                for (int64_t q = 0; q < qmax; q++) {
                    if (wp[q] == 0.0)
                        continue;
                    double tr, ti;
                    cs_dwba_dot(b.yr + S * m, b.yi + S * m, vr + S * q, vi + S * q, S, &tr, &ti);
                    const double ir = tr * cr - ti * ci, ii = tr * ci + ti * cr;
                    sum += wp[q] * (ir * ir + ii * ii);
                }
            }
        }
        out[k - 1] = sum;
    }
    rc = 0;
done:
    free(hp); free(fbuf); free(wbuf); free(vr); free(vi); free(invc);
    free(rows);
    return rc;
}

/* ---------------------------------------------------------------- inward Coulomb Numerov */

/* hfnative's numerov_scalar */
static void cs_numerov_scalar(const double ee, const double ra, const double r_b, const double gb,
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

#define CS_LANES 8
/* numerov_scalar on CS_LANES columns of one step count nn, stepped together */
static void cs_numerov_lanes(const double *ee, const double *ra, const double *rb, const double *gb,
                             const double *gb1, int64_t nn, double out[CS_LANES][6])
{
    double h[CS_LANES], c[CS_LANES], c5[CS_LANES], e2[CS_LANES], u1[CS_LANES], u2[CS_LANES],
           q1[CS_LANES], prev[CS_LANES];
    for (int j = 0; j < CS_LANES; j++) {
        h[j] = (rb[j] - ra[j]) / (double)nn;
        c[j] = h[j] * h[j] / 12.0;
        c5[j] = 5.0 * c[j];
        e2[j] = 2.0 * ee[j];
        u2[j] = gb[j];
        u1[j] = gb1[j];
        prev[j] = 0.0;
        q1[j] = 1.0 - e2[j] / (rb[j] - (double)1 * h[j]);
    }
    for (int64_t i = 2; i < nn + 2; i++) {
        const double dm = (double)(i - 1), d0 = (double)i;
        for (int j = 0; j < CS_LANES; j++) {
            const double x1 = rb[j] - dm * h[j];
            const double x0 = rb[j] - d0 * h[j];
            const double q0 = 1.0 - e2[j] / x0;
            const double A = 2.0 * (1.0 - c5[j] * q1[j]);
            const double B = 1.0 + c[j] * (1.0 - e2[j] / (x1 + h[j]));
            const double C = 1.0 + c[j] * q0;
            const double t = A * u1[j] - B * u2[j];
            u2[j] = u1[j];
            u1[j] = t / C;
            q1[j] = q0;
        }
        if (i == nn - 1)
            for (int j = 0; j < CS_LANES; j++)
                prev[j] = u1[j];
    }
    for (int j = 0; j < CS_LANES; j++) {
        out[j][0] = u2[j];
        out[j][1] = u1[j];
        out[j][2] = prev[j];
        out[j][3] = h[j];
        out[j][4] = c[j];
        out[j][5] = e2[j];
    }
}

/* flush one group of `cnt` equal-count columns `idx` through the lanes */
static void cs_numerov_group(const double *ee, const double *ra, const double *rb,
                             const double *gb, const double *gb1, int64_t nn, const int64_t *idx,
                             int cnt, double *outs[6])
{
    double lee[CS_LANES], lra[CS_LANES], lrb[CS_LANES], lgb[CS_LANES], lgb1[CS_LANES],
           o[CS_LANES][6];
    for (int j = 0; j < CS_LANES; j++) {
        const int64_t c = idx[j < cnt ? j : cnt - 1]; /* pad with the last column */
        lee[j] = ee[c];
        lra[j] = ra[c];
        lrb[j] = rb[c];
        lgb[j] = gb[c];
        lgb1[j] = gb1[c];
    }
    cs_numerov_lanes(lee, lra, lrb, lgb, lgb1, nn, o);
    for (int j = 0; j < cnt; j++)
        for (int f = 0; f < 6; f++)
            outs[f][idx[j]] = o[j][f];
}

void cs_numerov_inward(int64_t m, const double *ee, const double *ra, const double *rb,
                       const double *gb, const double *gb1, const int64_t *n, double *ga,
                       double *u1o, double *prevo, double *ho, double *co, double *e2o)
{
    double *outs[6] = {ga, u1o, prevo, ho, co, e2o};
    if (m <= 0)
        return;
    const int64_t nn = n[0];
    int64_t idx[CS_LANES];
    int cnt = 0;
    for (int64_t a = 0; a < m; a++) {
        if (n[a] != nn) {
            double o[6];
            cs_numerov_scalar(ee[a], ra[a], rb[a], gb[a], gb1[a], n[a], o);
            for (int f = 0; f < 6; f++)
                outs[f][a] = o[f];
            continue;
        }
        idx[cnt++] = a;
        if (cnt == CS_LANES) {
            cs_numerov_group(ee, ra, rb, gb, gb1, nn, idx, cnt, outs);
            cnt = 0;
        }
    }
    if (cnt > 0)
        cs_numerov_group(ee, ra, rb, gb, gb1, nn, idx, cnt, outs);
}
