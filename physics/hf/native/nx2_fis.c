/* NATIVEX2: the WKB penetrabilities of a fission path at every tabulation energy
 * (fission/wkb.py's `wkbfis` loop inside `wkb`), in one call.
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * TALYS routines: wkb.f90:212 (wkbfis), wkb.f90:445 (Vdef), wkb.f90:505 (rmiudef),
 * wkb.f90:534 (FindIntersect), wkbfunctions.f:1 (Fmoment), wkbfunctions.f:33 (GaussLegendre41).
 * The arithmetic is fission/wkb.py's, term by term; double precision, held to closeness.
 *
 * Path arrays beta, vfis, rmiu are 1-based with a dummy element 0 (nbeta + 2 entries are read:
 * the interpolation reads one past nbeta). iiextr[0..nextr+1]. vh, vw: 2*NUMBAR+2 entries.
 * Out, per energy b: tff[b*7 + k], phase[b*7 + k] for k = 0..6, tdir[b].
 */
#include <math.h>
#include <stdint.h>

/* wkb._interp1: the bracket [idef, idef+1] with idef = #(beta[1..nbeta] <= eps) clamped to
 * 1..nbeta */
static double interp1(const double *xs, const double *ys, int64_t nbeta, double eps) {
    int64_t lo = 0, hi = nbeta; /* searchsorted(right) over xs[1..nbeta] */
    while (lo < hi) {
        int64_t mid = (lo + hi) / 2;
        if (xs[1 + mid] <= eps)
            lo = mid + 1;
        else
            hi = mid;
    }
    int64_t idef = lo < 1 ? 1 : (lo > nbeta ? nbeta : lo);
    double ei = xs[idef], eip = xs[idef + 1], vi = ys[idef], vip = ys[idef + 1];
    if (ei == eip)
        return vi;
    return vi + (eps - ei) / (eip - ei) * (vip - vi);
}

typedef struct {
    const double *beta, *vfis, *rmiu;
    int64_t nbeta;
    double u;
} path_t;

static double fmoment(const path_t *p, double eps) {
    double rm = interp1(p->beta, p->rmiu, p->nbeta, eps);
    double v = interp1(p->beta, p->vfis, p->nbeta, eps);
    return 2.0 * sqrt(rm / 2.0) * sqrt(fabs(p->u - v));
}

static double gauss_legendre41(const path_t *p, double ea, double eb, const double *xgk,
                               const double *wgk, const double *wg) {
    double centr = 0.5 * (ea + eb), hlgth = 0.5 * (eb - ea);
    double fm[20], fp[20];
    double f0 = fmoment(p, centr);
    for (int j = 0; j < 20; j++) {
        double a = hlgth * xgk[j];
        fm[j] = fmoment(p, centr - a);
        fp[j] = fmoment(p, centr + a);
    }
    double resg = 0.0, resk = wgk[20] * f0;
    for (int j = 1; j <= 10; j++) {
        int jtw = 2 * j - 1, jtwm1 = 2 * j - 2;
        double fsum = fm[jtw] + fp[jtw];
        resg = resg + wg[j - 1] * fsum;
        resk = resk + wgk[jtw] * fsum + wgk[jtwm1] * (fm[jtwm1] + fp[jtwm1]);
    }
    return resk * hlgth;
}

static double find_intersect(const path_t *p, double uexc, int64_t ja, int64_t jb, int iswell) {
    const double *v = p->vfis, *beta = p->beta;
    int is0 = uexc - v[ja] >= 0.0 ? 1 : -1;
    for (int64_t j = ja; j <= jb; j++) {
        int is1 = uexc - v[j] >= 0.0 ? 1 : -1;
        if (is1 == is0)
            continue;
        return beta[j - 1] + (beta[j] - beta[j - 1]) * (uexc - v[j - 1]) / (v[j] - v[j - 1]);
    }
    double slope = v[jb] - v[ja];
    if (iswell)
        return slope >= 0 ? beta[jb] : beta[ja];
    return slope >= 0 ? beta[ja] : beta[jb];
}

int nx2_fis_wkb(const double *beta, const double *vfis, const double *rmiu, int64_t nbeta,
                const int64_t *iiextr, int64_t nextr, const double *vh, const double *vw,
                int64_t nb, const double *uexc, double pi, const double *xgk, const double *wgk,
                const double *wg, double *tff, double *phase, double *tdir) {
    if (nextr > 6)
        return -1;
    path_t p = {beta, vfis, rmiu, nbeta, 0.0};
    for (int64_t b = 0; b < nb; b++) {
        double *tf = tff + 7 * b, *ph = phase + 7 * b;
        double td[7];
        for (int k = 0; k < 7; k++)
            tf[k] = ph[k] = td[k] = 0.0;
        double u = uexc[b];
        p.u = u;
        for (int64_t k = 1; k <= nextr; k++) {
            if (k % 2 == 1) {
                if (u >= vh[k]) {
                    double dmom = vw[k] > 0 ? pi * (vh[k] - u) / vw[k] : -50.0;
                    ph[k] = dmom < 50.0 ? dmom : 50.0;
                    tf[k] = 1.0 / (1.0 + exp(2.0 * dmom));
                } else {
                    double ea = find_intersect(&p, u, iiextr[k - 1], iiextr[k], 0);
                    double eb = find_intersect(&p, u, iiextr[k], iiextr[k + 1], 0);
                    double dmom = gauss_legendre41(&p, ea, eb, xgk, wgk, wg);
                    ph[k] = dmom < 50.0 ? dmom : 50.0;
                    tf[k] = 1.0 / (1.0 + exp(2.0 * ph[k]));
                }
            } else if (u > vh[k]) {
                double ea = find_intersect(&p, u, iiextr[k - 1], iiextr[k], 1);
                double eb = find_intersect(&p, u, iiextr[k], iiextr[k + 1], 1);
                double dmom = gauss_legendre41(&p, ea, eb, xgk, wgk, wg);
                ph[k] = dmom < 50.0 ? dmom : 50.0;
            }
        }
        if (nextr > 0)
            td[nextr] = tf[nextr];
        for (int64_t k = nextr - 2; k > 0; k -= 2) {
            double dmom = (1.0 - tf[k]) * (1.0 - td[k + 2]);
            td[k] = tf[k] * td[k + 2] / (1.0 + dmom);
        }
        tdir[b] = td[1];
    }
    return 0;
}
