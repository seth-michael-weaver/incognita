/* NATIVEX2 lever `dwba`: the DWBA level cross sections of `ecis.dwba.dwba_cross_sections` for one
 * incident energy in one call (physics/hf/ecis/dwba_nx2.py builds the inputs).
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 * ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license.
 *
 * nx2_dwba_levels -- for the entrance channel (row 0) and every solved exit level (rows 1..nk-1):
 *   1. the uncoupled Numerov of `distorted_waves` (ecist.f:18285, inri), u(0) = 0, u(h) = h^(l+1).
 *      With g_i = f_i - k^2 and D_i = 1 - c g_i, `distorted_waves`' step
 *          D_{i+1} y_{i+1} = 2 (1 + 5 c g_i) y_i - D_{i-1} y_{i-1}
 *      is, for z_i = D_i y_i, the same recurrence z_{i+1} = (12 / D_i - 10) z_i - z_{i-1}
 *      (1 + 5 c g_i = 6 - 5 D_i), and y_i = z_i / D_i. All channels of one energy advance a step
 *      together, so the independent recurrences overlap in the processor.
 *   2. `_normalise`: the Numerov-consistent derivative at r = (n-1) h and the Wronskian scale
 *      C = (y H+' - y' H+) / (2 i k), u = y / C (no cancellation for a barely-open high-l channel;
 *      see `_normalise`). `_normalise` first divides y by max_r |y|; that is a conditioning step
 *      only (the constant cancels in y / C), and here the scale is the largest |y| of the three
 *      matching points, which keeps the matching arithmetic of order one the same way without a
 *      pass over the radii. u = y / C is never formed: 1 / C multiplies the overlap.
 *   3. the overlap I[p, q] = sum_r u^(b)_p(r) W(r) wt(r) u^(0)_q(r), only where the level's
 *      Clebsch-Gordan weight table is non-zero, and S_b = sum_{p,q} weight[p,q] |I[p,q]|^2.
 * Only the channels a weight reads are integrated: entrance channels up to the last column with a
 * non-zero weight, exit channels whose row has one. No (levels, channels, radii) array.
 * H+ = G + i F at r_match: taken from `hp_in` (nk, nlj, 4: Re hp, Im hp, Re dhp, Im dhp) when
 * given, else computed here for eta = 0 rows as `coulomb_functions` does (ecist.f:5775, fcou):
 * G_0 = cos rho, G_0' = -sin rho, G_L by upward recurrence, F'_L/F_L by the backward continued
 * fraction from L = lmax + int(max rho) + 60, and F = 1 / (f G - G').
 * Held to closeness with the torch path, not to bits.
 * Returns 0, or -1 (allocation failed), -2 (a charged row without `hp_in`). */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* H+ and k H+' at rho for L = 0..lmax, eta = 0, into out (nlj, 4); fbuf holds 3 (lmax+1). */
static void nx2_dwba_neutral(double rho, int64_t lmax, int64_t ltop, double k, double *fbuf,
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

/* The raw Numerov waves y (nrow, n+1, 2) of the `nrow` channels `rows` at one energy, and 1 / C
 * per row (nrow, 2), so that u = y / C. f (nlj, n+1, 2), y1 (nlj,), hp (nlj, 4) of this energy;
 * e (nrow, n+1, 2) and st (nrow, 4) are scratch. */
static void nx2_dwba_waves(int64_t n, double h, const double *f, double k2, double kabs,
                           const double *y1, const double *hp, int64_t nrow,
                           const int64_t *rows, double *e, double *st, double *y, double *invc)
{
    const int64_t S = n + 1;
    const double c = h * h / 12.0;
    for (int64_t m = 0; m < nrow; m++) {
        const double *fr = f + 2 * S * rows[m];
        double *em = e + 2 * S * m;
        for (int64_t i = 1; i < S; i++) {
            const double dr = 1.0 - c * (fr[2 * i] - k2), di = -c * fr[2 * i + 1];
            const double s = 1.0 / (dr * dr + di * di);
            em[2 * i] = dr * s; /* 1 / D_i */
            em[2 * i + 1] = -di * s;
        }
        double *ym = y + 2 * S * m;
        const double y1m = y1[rows[m]];
        ym[0] = ym[1] = 0.0;
        ym[2] = y1m;
        ym[3] = 0.0;
        /* z_0 = 0, z_1 = D_1 y_1 */
        st[4 * m] = 0.0;
        st[4 * m + 1] = 0.0;
        st[4 * m + 2] = (1.0 - c * (fr[2] - k2)) * y1m;
        st[4 * m + 3] = -c * fr[3] * y1m;
    }
    for (int64_t i = 1; i < n; i++) {
        for (int64_t m = 0; m < nrow; m++) {
            double *sm = st + 4 * m;
            const double *em = e + 2 * S * m;
            const double tr = 12.0 * em[2 * i] - 10.0, ti = 12.0 * em[2 * i + 1];
            const double zr = sm[2], zi = sm[3];
            const double nr = (tr * zr - ti * zi) - sm[0];
            const double ni = (tr * zi + ti * zr) - sm[1];
            sm[0] = zr;
            sm[1] = zi;
            sm[2] = nr;
            sm[3] = ni;
            const double er = em[2 * i + 2], ei = em[2 * i + 3];
            double *ym = y + 2 * S * m;
            ym[2 * i + 2] = nr * er - ni * ei;
            ym[2 * i + 3] = nr * ei + ni * er;
        }
    }
    for (int64_t m = 0; m < nrow; m++) {
        const double *ym = y + 2 * S * m;
        const double *fr = f + 2 * S * rows[m];
        const double *H = hp + 4 * rows[m];
        double a2 = 0.0;
        for (int64_t i = n - 2; i <= n; i++) {
            const double a = ym[2 * i] * ym[2 * i] + ym[2 * i + 1] * ym[2 * i + 1];
            a2 = a > a2 ? a : a2;
        }
        double amax = sqrt(a2);
        if (!(amax >= 1.0e-300))
            amax = 1.0e-300;
        const double sc = 1.0 / amax;
        const double fpr = fr[2 * n] - k2, fpi = fr[2 * n + 1];
        const double fqr = fr[2 * (n - 2)] - k2, fqi = fr[2 * (n - 2) + 1];
        const double ynr = ym[2 * n] * sc, yni = ym[2 * n + 1] * sc;
        const double yqr = ym[2 * (n - 2)] * sc, yqi = ym[2 * (n - 2) + 1] * sc;
        const double ymr = ym[2 * (n - 1)] * sc, ymi = ym[2 * (n - 1) + 1] * sc;
        const double er = 1.0 - 2.0 * c * fpr, ei = -2.0 * c * fpi;
        const double gr = 1.0 - 2.0 * c * fqr, gi = -2.0 * c * fqi;
        const double dyr = ((ynr * er - yni * ei) - (yqr * gr - yqi * gi)) / (2.0 * h);
        const double dyi = ((ynr * ei + yni * er) - (yqr * gi + yqi * gr)) / (2.0 * h);
        /* C = (um dhp - dy hp) / (2 i k), of the scaled y */
        const double numr = (ymr * H[2] - ymi * H[3]) - (dyr * H[0] - dyi * H[1]);
        const double numi = (ymr * H[3] + ymi * H[2]) - (dyr * H[1] + dyi * H[0]);
        const double cr = numi / (2.0 * kabs), ci = -numr / (2.0 * kabs);
        /* u = (y sc) / C */
        const double t = 1.0 / (cr * cr + ci * ci);
        invc[2 * m] = cr * t * sc;
        invc[2 * m + 1] = -ci * t * sc;
    }
}

/* sum_r u(r) v(r) for complex rows (S, 2), in four accumulation lanes */
static void nx2_dwba_dot(const double *u, const double *v, int64_t S, double *re, double *im)
{
    double sr[4] = {0.0, 0.0, 0.0, 0.0}, si[4] = {0.0, 0.0, 0.0, 0.0};
    int64_t i = 0;
    for (; i + 4 <= S; i += 4)
        for (int m = 0; m < 4; m++) {
            const double ur = u[2 * (i + m)], ui = u[2 * (i + m) + 1];
            const double vr = v[2 * (i + m)], vi = v[2 * (i + m) + 1];
            sr[m] += ur * vr - ui * vi;
            si[m] += ur * vi + ui * vr;
        }
    for (; i < S; i++) {
        sr[0] += u[2 * i] * v[2 * i] - u[2 * i + 1] * v[2 * i + 1];
        si[0] += u[2 * i] * v[2 * i + 1] + u[2 * i + 1] * v[2 * i];
    }
    *re = (sr[0] + sr[1]) + (sr[2] + sr[3]);
    *im = (si[0] + si[1]) + (si[2] + si[3]);
}

int nx2_dwba_levels(int64_t nlj, int64_t n, double h, const double *f, const double *y1,
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
    const size_t nr = (size_t)(nlj > 0 ? nlj : 1);
    double *hp = NULL, *fbuf = NULL;
    double *e = malloc(sizeof(double) * 2 * (size_t)S * nr);
    double *v = malloc(sizeof(double) * 2 * (size_t)S * nr);
    double *u = malloc(sizeof(double) * 2 * (size_t)S * nr);
    double *st = malloc(sizeof(double) * 4 * nr);
    double *invc = malloc(sizeof(double) * 2 * nr);
    int64_t *rows = calloc(nr, sizeof(int64_t));
    int rc = -1;
    if (e == NULL || v == NULL || u == NULL || st == NULL || invc == NULL || rows == NULL)
        goto done;
    if (hp_in == NULL) {
        double rho_max = 0.0;
        for (int64_t b = 0; b < nk; b++) {
            if (eta[b] != 0.0) {
                rc = -2;
                goto done;
            }
            const double rho = sqrt(fabs(kappa2[b])) * rm;
            rho_max = rho > rho_max ? rho : rho_max;
        }
        const int64_t ltop = lmax + (int64_t)rho_max + 60;
        hp = malloc(sizeof(double) * 4 * (size_t)(nk * nlj));
        fbuf = malloc(sizeof(double) * (size_t)(3 * (lmax + 1) + ltop + 1));
        if (hp == NULL || fbuf == NULL)
            goto done;
        for (int64_t b = 0; b < nk; b++) {
            const double k = sqrt(fabs(kappa2[b]));
            nx2_dwba_neutral(k * rm, lmax, ltop, k, fbuf, hp + 4 * b * nlj, nlj, l);
        }
    }
    const double *H = hp_in != NULL ? hp_in : hp;
    /* entrance channels 0..qmax-1: v_q = u_q W wt */
    for (int64_t q = 0; q < qmax; q++)
        rows[q] = q;
    nx2_dwba_waves(n, h, f, kappa2[0], sqrt(fabs(kappa2[0])), y1, H, qmax, rows, e, st, v, invc);
    for (int64_t q = 0; q < qmax; q++) {
        double *vq = v + 2 * S * q;
        const double cr = invc[2 * q], ci = invc[2 * q + 1];
        for (int64_t i = 0; i < S; i++) {
            const double ar = vq[2 * i] * cr - vq[2 * i + 1] * ci;
            const double ai = vq[2 * i] * ci + vq[2 * i + 1] * cr;
            vq[2 * i] = ar * ww[2 * i] - ai * ww[2 * i + 1];
            vq[2 * i + 1] = ar * ww[2 * i + 1] + ai * ww[2 * i];
        }
    }
    for (int64_t b = 1; b < nk; b++) {
        const double *w = tab + tab_of[b - 1] * nlj * nlj;
        int64_t np = 0;
        for (int64_t p = 0; p < nlj; p++)
            for (int64_t q = 0; q < qmax; q++)
                if (w[p * nlj + q] != 0.0) {
                    rows[np++] = p;
                    break;
                }
        nx2_dwba_waves(n, h, f, kappa2[b], sqrt(fabs(kappa2[b])), y1, H + 4 * b * nlj, np, rows,
                       e, st, u, invc);
        double sum = 0.0;
        for (int64_t m = 0; m < np; m++) {
            const double *wp = w + rows[m] * nlj;
            const double cr = invc[2 * m], ci = invc[2 * m + 1];
            for (int64_t q = 0; q < qmax; q++) {
                if (wp[q] == 0.0)
                    continue;
                double tr, ti;
                nx2_dwba_dot(u + 2 * S * m, v + 2 * S * q, S, &tr, &ti);
                const double ir = tr * cr - ti * ci, ii = tr * ci + ti * cr;
                sum += wp[q] * (ir * ir + ii * ii);
            }
        }
        out[b - 1] = sum;
    }
    rc = 0;
done:
    free(hp); free(fbuf); free(e); free(v); free(u); free(st); free(invc); free(rows);
    return rc;
}
