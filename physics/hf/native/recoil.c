/* KWCOV B12 (RECOIL): the LAB-frame scatter of TALYS's recoil module, OUTPUT ONLY.
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * TALYS routines ported here (file:line of the subroutine statement):
 *   cm2lab.f90:1      (cm2lab)      the four corners of a CM (energy, angle) bin in the LAB, ejectile and recoil
 *   labsurface.f90:1  (labsurface)  the LAB triangle's area and its share in every LAB (energy, unfolded cosine) bin
 *   binsurface.f90:1  (binsurface)  triangle x bin overlap, as written (intri.f90, invect.f90, intersection.f90,
 *                                   sideline.f90 with its vertical / horizontal-side quirk)
 *   belongs.f90:1     (belongs)
 *   binaryrecoil.f90 / angdisrecoil.f90 / comprecoil.f90: the per-cell bodies (renormalisation of the last LAB bin,
 *                     the two triangles, the deposits into ddxrec / ddxrectot / ddxejlab)
 * physics/hf/recoil.py drives it (and holds the same code in Python: recoil.scatter_py, used when the library is not
 * built and by tests/hf/test_kwcov_b12.py to check this file, in double precision). Arithmetic in single precision
 * as TALYS (real(sgl)): a CM cell whose edges meet a LAB bin edge is binned by the last bit (Fe-56 1 MeV gamma LAB
 * spectrum: 25 % per bin in double, 0.2 % in single); -DRC_DOUBLE builds it in double.
 *
 * Build: scripts/build_recoil_native.sh -> physics/hf/native/lib/librecoil.so
 */
#include <math.h>
#include <stdlib.h>
#include <string.h>

typedef double rl;  /* state arrays (shared with numpy) */
#ifndef RC_DOUBLE  /* default: TALYS's single precision (-DRC_DOUBLE for double) */
typedef float cl;    /* arithmetic in TALYS's single precision (real(sgl)) */
#define ACOS acosf
#define COS cosf
#define SQRT sqrtf
#define FABS fabsf
#else
typedef double cl;
#define ACOS acos
#define COS cos
#define SQRT sqrt
#define FABS fabs
#endif

int rc_version(void) { return 1; }

static const cl PI = (cl)3.14159265358979323846;

static int belongs(cl x, cl x1, cl x2) {
    cl x1x = x - x1, x1x2 = x2 - x1;
    cl norm12 = FABS(x1x2), norm1x = FABS(x1x);
    cl eps = norm12 / 1.0e14;
    if (x1x * x1x2 < -eps) return 0;
    if (norm1x - norm12 > eps) return 0;
    return 1;
}

/* sideline.f90: which side of the segment (xs,ys)-(xe,ye) the point is on: -1 / 0 / 1 for a sloped segment, but the
 * signed DISTANCE x - xs (y - ys) for a vertical (horizontal) one -- intri.f90 then compares these values for
 * equality, so a corner is "inside" a triangle with a vertical or horizontal side only when it lies on that line. */
static cl sideline(cl x, cl y, cl xs, cl ys, cl xe, cl ye) {
    cl xdlim = (FABS(xs) < FABS(xe) ? FABS(xs) : FABS(xe)) / (cl)1.e14;
    cl ydlim = (FABS(ys) < FABS(ye) ? FABS(ys) : FABS(ye)) / (cl)1.e14;
    cl sl;
    if (FABS(xs - xe) <= xdlim) {
        sl = x - xs;
        if (FABS(sl) <= xdlim) sl = 0;
        return sl;
    }
    if (FABS(ys - ye) <= ydlim) {
        sl = y - ys;
        if (FABS(sl) <= ydlim) sl = 0;
        return sl;
    }
    cl a = (ys - ye) / (xs - xe);
    cl b = ys - a * xs;
    sl = y - (a * x + b);
    if (FABS(sl) <= (cl)1.e-12) return 0;
    return sl < 0 ? (cl)-1 : (cl)1;
}

/* intri.f90 */
static int intri(cl x, cl y, cl x1, cl y1, cl x2, cl y2, cl x3, cl y3) {
    cl xg = (x1 + x2 + x3) / (cl)3.0, yg = (y1 + y2 + y3) / (cl)3.0;
    cl s1 = sideline(x, y, x1, y1, x2, y2), g1 = sideline(xg, yg, x1, y1, x2, y2);
    cl s2 = sideline(x, y, x2, y2, x3, y3), g2 = sideline(xg, yg, x2, y2, x3, y3);
    cl s3 = sideline(x, y, x3, y3, x1, y1), g3 = sideline(xg, yg, x3, y3, x1, y1);
    return (s1 == g1 || s1 == 0) && (s2 == g2 || s2 == 0) && (s3 == g3 || s3 == 0);
}

/* invect.f90 */
static int invect(cl x, cl y, cl x1, cl y1, cl x2, cl y2) {
    cl x1x = x - x1, y1x = y - y1, x12 = x2 - x1, y12 = y2 - y1;
    cl norm1 = x1x * x1x + y1x * y1x, norm2 = x12 * x12 + y12 * y12;
    cl eps = norm2 / (cl)1.0e14;
    if (x12 * x1x + y12 * y1x < -eps) return 0;
    if (norm1 - norm2 > eps) return 0;
    return 1;
}

/* intersection.f90: the line through (xs,ys)-(xe,ye) with the four sides of the bin */
static int intersection(cl xs, cl ys, cl xe, cl ye, cl xl, cl yl, cl xu, cl yu, cl *xr, cl *yr) {
    int ir = 0;
    cl xdlim = (FABS(xs) < FABS(xe) ? FABS(xs) : FABS(xe)) / (cl)1.e14;
    cl ydlim = (FABS(ys) < FABS(ye) ? FABS(ys) : FABS(ye)) / (cl)1.e14;
    if (FABS(xs - xe) <= xdlim) {
        if (belongs(xs, xu, xl)) { xr[0] = xs; xr[1] = xs; yr[0] = yu; yr[1] = yl; return 2; }
        return 0;
    }
    if (FABS(ys - ye) <= ydlim) {
        if (belongs(ys, yu, yl)) { xr[0] = xu; xr[1] = xl; yr[0] = ys; yr[1] = ys; return 2; }
        return 0;
    }
    cl a = (ys - ye) / (xs - xe), b = ys - a * xs;
    cl ya = a * xl + b, yb = a * xu + b, xc = (yl - b) / a, xd = (yu - b) / a;
    if (belongs(ya, yu, yl)) { xr[ir] = xl; yr[ir] = ya; ir++; }
    if (belongs(yb, yu, yl)) { xr[ir] = xu; yr[ir] = yb; ir++; }
    if (belongs(xc, xu, xl)) { xr[ir] = xc; yr[ir] = yl; ir++; }
    if (belongs(xd, xu, xl)) { xr[ir] = xd; yr[ir] = yu; ir++; }
    return ir;
}

/* binsurface.f90 as written: the polygon of bin corners inside the triangle, side intersections and triangle summits
 * inside the bin (merged within epsx / epsy), sorted by angle around its centre of gravity, fan area */
static cl binsurface(cl x1, cl y1, cl x2, cl y2, cl x3, cl y3, cl xl, cl xu, cl yl, cl yu, cl epsx, cl epsy,
                     cl surfbin) {
    cl xs[24], ys[24], xp[16], yp[16], xr[4], yr[4], an[24];
    int is = 0, ip = 0, nr;
    cl cx[4] = {xl, xl, xu, xu}, cy[4] = {yl, yu, yl, yu};
    for (int k = 0; k < 4; k++)
        if (intri(cx[k], cy[k], x1, y1, x2, y2, x3, y3)) { xs[is] = cx[k]; ys[is] = cy[k]; is++; }
    if (is == 4) return surfbin;
    cl sx[3] = {x1, x2, x3}, sy[3] = {y1, y2, y3};
    for (int e = 0; e < 3; e++) {
        cl ax = sx[e], ay = sy[e], bx = sx[(e + 1) % 3], by = sy[(e + 1) % 3];
        nr = intersection(ax, ay, bx, by, xl, yl, xu, yu, xr, yr);
        for (int r = 0; r < nr; r++)
            if (invect(xr[r], yr[r], ax, ay, bx, by)) { xp[ip] = xr[r]; yp[ip] = yr[r]; ip++; }
    }
    for (int k = 0; k < 3; k++)
        if (belongs(sx[k], xu, xl) && belongs(sy[k], yu, yl)) { xp[ip] = sx[k]; yp[ip] = sy[k]; ip++; }
    if (is == 0 && ip > 0) { xs[0] = xp[0]; ys[0] = yp[0]; is = 1; }
    for (int p = 0; p < ip; p++) {
        int dup = 0;
        for (int r = 0; r < is; r++)
            if (FABS(xp[p] - xs[r]) <= epsx && FABS(yp[p] - ys[r]) <= epsy) { dup = 1; break; }
        if (!dup) { xs[is] = xp[p]; ys[is] = yp[p]; is++; }
    }
    if (is <= 2) return 0;
    if (is == 3)
        return FABS((cl)0.5 * ((xs[2] - xs[1]) * (ys[0] - ys[1]) - (xs[0] - xs[1]) * (ys[2] - ys[1])));
    cl xg = 0, yg = 0;
    for (int p = 0; p < is; p++) { xg += xs[p]; yg += ys[p]; }
    cl w = (cl)1.0 / (cl)is;
    xg *= w; yg *= w;
    cl r1x = xs[0] - xg, r1y = ys[0] - yg, n1 = r1x * r1x + r1y * r1y;
    an[0] = 0;
    for (int p = 1; p < is; p++) {
        cl r2x = xs[p] - xg, r2y = ys[p] - yg, n2 = r2x * r2x + r2y * r2y, n12 = n1 * n2, c12, a12;
        c12 = n12 == 0 ? (cl)1 : (r1x * r2x + r1y * r2y) / SQRT(n12);
        if (c12 <= -1) a12 = PI;
        else if (c12 >= 1) a12 = 0;
        else a12 = ACOS(c12);
        if (r1x * r2y - r2x * r1y < 0) a12 = (cl)2.0 * PI - a12;
        an[p] = a12;
    }
    for (int p = 0; p < is - 1; p++)
        for (int r = p + 1; r < is; r++) {
            if (an[r] > an[p]) continue;
            cl tx = xs[p], ty = ys[p], ta = an[p];
            xs[p] = xs[r]; ys[p] = ys[r]; an[p] = an[r];
            xs[r] = tx; ys[r] = ty; an[r] = ta;
        }
    cl sf = FABS((cl)0.5 * ((xg - xs[is - 1]) * (ys[0] - ys[is - 1]) - (xs[0] - xs[is - 1]) * (yg - ys[is - 1])));
    for (int p = 0; p < is - 1; p++)
        sf += FABS((cl)0.5 * ((xg - xs[p + 1]) * (ys[p] - ys[p + 1]) - (xs[p] - xs[p + 1]) * (yg - ys[p + 1])));
    return sf;
}

typedef struct {
    int ix0, ixmax, nang, ej;  /* first / last energy bin, nanglecont or nanglerec, ejectile grid (scov at max(ix,1)) */
    rl *xmin, *xmax;           /* bin edges by ix */
    rl *area;                  /* [ix * (2 nang + 2) + iy] */
    rl *cmin, *cmax;           /* cosine edges, 0 .. 2 nang + 1 */
} Grid;

static void labsurface(Grid *g, cl x1, cl c1, cl s1, cl x2, cl c2, cl s2, cl x3, cl c3, cl s3, cl *totsurf,
                       int limx[2], int limy[2], rl *scov) {
    const int acols = 2 * g->nang + 2, iymax = 2 * g->nang + 1;
    int recoilmode = 1, ix1 = 1, ix2 = 1, ix3 = 1, iy1 = 0, iy2 = 0, iy3 = 0;
    cl cs[3] = {c1, c2, c3}, ss[3] = {s1, s2, s3}, xs[3] = {x1, x2, x3}, yc[3];
    int nt[3];
    for (int k = 0; k < 3; k++) {
        cl c = cs[k] < -1.0 ? -1.0 : (cs[k] > 1.0 ? 1.0 : cs[k]);
        cl ang = ACOS(c);
        if (ss[k] < 0.0) ang = 2.0 * PI - ang;
        cl yy = ang; /* + angcm (0) */
        int is = (int)(yy / PI);
        nt[k] = (int)(yy / (2.0 * PI));
        yc[k] = -2.0 * is + ((is % 2) ? -1.0 : 1.0) * COS(yy);
    }
    cl ts = FABS((cl)0.5 * ((xs[0] - xs[2]) * (yc[1] - yc[2]) - (xs[1] - xs[2]) * (yc[0] - yc[2])));
    if (ts < 1.0e-14) { ts = 1.0e-14; recoilmode = 2; }
    *totsurf = ts;
    int ixk[3] = {ix1, ix2, ix3}, iyk[3] = {iy1, iy2, iy3};
    for (int k = 0; k < 3; k++) {
        if (xs[k] > (cl)g->xmax[g->ixmax]) {
            g->xmax[g->ixmax] = xs[k];
            ixk[k] = g->ixmax;
        } else {
            for (int ix = g->ix0; ix <= g->ixmax; ix++)
                if (belongs(xs[k], g->xmin[ix], g->xmax[ix])) { ixk[k] = ix; break; }
        }
    }
    for (int k = 0; k < 3; k++) {
        for (int iy = 0; iy <= iymax; iy++) {
            cl yl = -4.0 * nt[k], yu = -4.0 * nt[k];
            if (iy <= g->nang) { yl += g->cmin[iy]; yu += g->cmax[iy]; }
            else { yl = yl - g->cmin[iy] - 2.0; yu = yu - g->cmax[iy] - 2.0; }
            if (belongs(yc[k], yl, yu)) { iyk[k] = iy + nt[k] * (iymax + 1); break; }
        }
    }
    int ixmin = ixk[0], ixmx = ixk[0], iymin = iyk[0], iysup = iyk[0];
    for (int k = 1; k < 3; k++) {
        if (ixk[k] < ixmin) ixmin = ixk[k];
        if (ixk[k] > ixmx) ixmx = ixk[k];
        if (iyk[k] < iymin) iymin = iyk[k];
        if (iyk[k] > iysup) iysup = iyk[k];
    }
    limx[0] = ixmin; limx[1] = ixmx; limy[0] = iymin; limy[1] = iysup;
#define SC(ix, iy) scov[((g->ej && (ix) < 1) ? 1 : (ix)) * acols + (iy)]
    if (ixmin == ixmx && iymin == iysup) {
        SC(ixmin, iymin % (iymax + 1)) = ts;
        return;
    }
    int nb = (ixmx - ixmin + 1) * (iysup - iymin + 1);
    if (recoilmode == 2) {
        for (int ix = ixmin; ix <= ixmx; ix++)
            for (int iy = iymin; iy <= iysup; iy++) SC(ix, iy % (iymax + 1)) = ts * (1.0 / (cl)nb);
        return;
    }
    cl sumsurf = 0.0;
    for (int ix = ixmin; ix <= ixmx; ix++) {
        cl xl = g->xmin[ix], xu = g->xmax[ix];
        for (int iy = iymin; iy <= iysup; iy++) {
            int ist = iy % (iymax + 1), nturn = iy / (2 * g->nang + 2);
            cl yl = -4.0 * nturn, yu = -4.0 * nturn;
            if (ist <= g->nang) { yl += g->cmin[ist]; yu += g->cmax[ist]; }
            else { yl = yl - g->cmin[ist] - 2.0; yu = yu - g->cmax[ist] - 2.0; }
            cl epsx = (xu - xl) / (cl)100000., epsy = FABS(yu - yl) / (cl)100000.;
            cl s = binsurface(xs[0], yc[0], xs[1], yc[1], xs[2], yc[2], xl, xu, yl, yu, epsx, epsy,
                              (cl)g->area[ix * acols + ist]);
            SC(ix, ist) = s;
            sumsurf += s;
        }
    }
    if (ts != sumsurf) {
        if (sumsurf != 0.0) {
            cl rn = ts / sumsurf;
            for (int ix = ixmin; ix <= ixmx; ix++)
                for (int iy = iymin; iy <= iysup; iy++) SC(ix, iy % (iymax + 1)) *= rn;
        } else {
            for (int ix = ixmin; ix <= ixmx; ix++)
                for (int iy = iymin; iy <= iysup; iy++) SC(ix, iy % (iymax + 1)) = ts * (1.0 / (cl)nb);
        }
    }
#undef SC
}

/* cell: E1 E2 cos1 cos2 sin1 sin2 vcm flux divide iexlo iexhi (11 doubles).
 * iv: [0] ncell [1] type [2] maxenrec [3] nanglerec [4] nexrows [5] renorm_rec [6] ej_on [7] iejlab [8] nanglecont
 *     [9] renorm_ej
 * dv: [0] ejectmass [1] recoilmass   (MeV)
 * pv: [0] cell [1] Erecmin [2] Erecmax [3] areareclab [4] cosrecmin [5] cosrecmax [6] ddxrec [7] ddxrectot
 *     [8] Eejlabmin [9] Eejlabmax [10] dEejlab [11] areaejlab [12] cosangcontmin [13] cosangcontmax
 *     [14] ddx (ejectile deposit) [15] ddx (ejectile renorm)
 * Returns 0, or -1 on allocation failure. */
int rc_batch(const long *iv, const double *dv, const unsigned long *pv) {
    const int ncell = (int)iv[0], type = (int)iv[1], maxenrec = (int)iv[2], nr = (int)iv[3], nexrows = (int)iv[4];
    const int renorm_rec = (int)iv[5], ej_on = (int)iv[6], iejlab = (int)iv[7], nc = (int)iv[8], renorm_ej = (int)iv[9];
    const cl em = (cl)dv[0], rm = (cl)dv[1];
    const rl *cell = (const rl *)pv[0];
    Grid gr = {0, maxenrec, nr, 0, (rl *)pv[1], (rl *)pv[2], (rl *)pv[3], (rl *)pv[4], (rl *)pv[5]};
    rl *ddxrec = (rl *)pv[6], *ddxrectot = (rl *)pv[7];
    Grid ge = {1, iejlab, nc, 1, (rl *)pv[8], (rl *)pv[9], (rl *)pv[11], (rl *)pv[12], (rl *)pv[13]};
    rl *dEej = (rl *)pv[10], *ddxdep = (rl *)pv[14], *ddxren = (rl *)pv[15];
    const int rcols = 2 * nr + 2, ecols = 2 * nc + 2;
    rl *sr1 = calloc((size_t)(maxenrec + 2) * rcols, sizeof(rl)), *sr2 = calloc((size_t)(maxenrec + 2) * rcols, sizeof(rl));
    rl *se1 = NULL, *se2 = NULL;
    if (ej_on) {
        se1 = calloc((size_t)(iejlab + 2) * ecols, sizeof(rl));
        se2 = calloc((size_t)(iejlab + 2) * ecols, sizeof(rl));
    }
    if (!sr1 || !sr2 || (ej_on && (!se1 || !se2))) { free(sr1); free(sr2); free(se1); free(se2); return -1; }
    const cl ratio = type != 0 ? rm / (em * (em + rm)) : 0.0;
    for (int c = 0; c < ncell; c++) {
        const rl *q = cell + 11 * c;
        cl E1 = (cl)q[0], E2 = (cl)q[1], c1 = (cl)q[2], c2 = (cl)q[3], s1 = (cl)q[4], s2 = (cl)q[5], vcm = (cl)q[6], flux = (cl)q[7], divide = (cl)q[8];
        int iexlo = (int)q[9], iexhi = (int)q[10];
        if (flux == 0.0) continue;
        cl p1, p2, vej1 = 0.0, vej2 = 0.0;
        if (type != 0) {
            p1 = em * SQRT(2.0 * ratio * E1); p2 = em * SQRT(2.0 * ratio * E2);
            vej1 = p1 / em; vej2 = p2 / em;
        } else { p1 = E1; p2 = E2; }
        cl vr1 = p1 / rm, vr2 = p2 / rm;
        /* cm2lab.f90 */
        cl Ee[4], ce[4], se[4], Er[4], cr[4], sr[4];
        cl vEs[4] = {vej1, vej1, vej2, vej2}, vRs[4] = {vr1, vr1, vr2, vr2};
        cl cc[4] = {c1, c2, c1, c2}, sc[4] = {s1, s2, s1, s2}, Ecm[4] = {E1, E1, E2, E2};
        for (int k = 0; k < 4; k++) {
            if (type == 0) { Ee[k] = Ecm[k]; ce[k] = cc[k]; se[k] = sc[k]; }
            else {
                cl vx = vcm + vEs[k] * cc[k], vy = vEs[k] * sc[k], v2 = vx * vx + vy * vy;
                cl v = SQRT(v2); if (v < 1e-20) v = 1e-20;
                ce[k] = vx / v; se[k] = vy / v; Ee[k] = 0.5 * em * v2;
            }
            cl vx = vcm - vRs[k] * cc[k], vy = -vRs[k] * sc[k], v2 = vx * vx + vy * vy;
            cl v = SQRT(v2); if (v < 1e-20) v = 1e-20;
            cr[k] = vx / v; sr[k] = -sc[k]; Er[k] = 0.5 * rm * v2;
        }
        int lx1[2], ly1[2], lx2[2], ly2[2];
        cl t1, t2;
        if (ej_on) {
            if (renorm_ej) {
                cl Emaxi = ge.xmax[iejlab], dEori = Emaxi - ge.xmin[iejlab];
                int irn = 0;
                for (int k = 0; k < 4; k++) if (Ee[k] > Emaxi) { Emaxi = Ee[k]; irn = 1; }
                if (irn) {
                    ge.xmax[iejlab] = Emaxi;
                    cl dEnew = Emaxi - ge.xmin[iejlab];
                    dEej[iejlab] = dEnew;
                    cl rn = dEori / dEnew;
                    for (int ia = 0; ia <= nc; ia++) {
                        ge.area[iejlab * ecols + ia] /= rn;
                        ddxren[iejlab * (nc + 1) + ia] *= rn;
                    }
                }
            }
            labsurface(&ge, Ee[0], ce[0], se[0], Ee[1], ce[1], se[1], Ee[2], ce[2], se[2], &t1, lx1, ly1, se1);
            labsurface(&ge, Ee[2], ce[2], se[2], Ee[3], ce[3], se[3], Ee[1], ce[1], se[1], &t2, lx2, ly2, se2);
            cl ls = t1 + t2;
            if (ls == 0.0) continue;
            cl ddxLAB = flux / ls;
            for (int tri = 0; tri < 2; tri++) {
                int *lx = tri ? lx2 : lx1, *ly = tri ? ly2 : ly1;
                rl *sc_ = tri ? se2 : se1;
                for (int ix = lx[0]; ix <= lx[1]; ix++)
                    for (int iy = ly[0]; iy <= ly[1]; iy++) {
                        int im = iy % ecols, iys = im <= nc ? im : 2 * nc + 1 - im;
                        cl a = ge.area[ix * ecols + im];
                        if (a > 0.0) ddxdep[ix * (nc + 1) + iys] += ddxLAB / a * sc_[(ix < 1 ? 1 : ix) * ecols + im];
                    }
            }
        }
        if (renorm_rec) {
            cl Emaxi = gr.xmax[maxenrec], dEori = Emaxi - gr.xmin[maxenrec];
            int irn = 0;
            for (int k = 0; k < 4; k++) if (Er[k] > Emaxi) { Emaxi = Er[k]; irn = 1; }
            if (irn) {
                gr.xmax[maxenrec] = Emaxi;
                cl dEnew = Emaxi - gr.xmin[maxenrec];
                cl rn = dEori / dEnew;
                for (int ia = 0; ia <= nr; ia++) {
                    gr.area[maxenrec * rcols + ia] /= rn;
                    for (int ie = 0; ie < nexrows; ie++) ddxrec[(ie * (maxenrec + 1) + maxenrec) * (nr + 1) + ia] *= rn;
                }
            }
        }
        labsurface(&gr, Er[0], cr[0], sr[0], Er[1], cr[1], sr[1], Er[2], cr[2], sr[2], &t1, lx1, ly1, sr1);
        labsurface(&gr, Er[2], cr[2], sr[2], Er[3], cr[3], sr[3], Er[1], cr[1], sr[1], &t2, lx2, ly2, sr2);
        cl ls = t1 + t2;
        if (ls == 0.0) continue;
        cl ddxLAB = flux / ls / divide;
        for (int tri = 0; tri < 2; tri++) {
            int *lx = tri ? lx2 : lx1, *ly = tri ? ly2 : ly1;
            rl *sc_ = tri ? sr2 : sr1;
            for (int ix = lx[0]; ix <= lx[1]; ix++)
                for (int iy = ly[0]; iy <= ly[1]; iy++) {
                    int im = iy % rcols;
                    cl a = gr.area[ix * rcols + im];
                    if (a == 0.0) continue;
                    cl fa = ddxLAB * sc_[ix * rcols + im];
                    cl add = fa / a;
                    int iys = im <= nr ? im : 2 * nr + 1 - im;
                    for (int ie = iexlo; ie <= iexhi; ie++) {
                        if (ie < 0 || ie >= nexrows) continue;
                        ddxrec[(ie * (maxenrec + 1) + ix) * (nr + 1) + iys] += add;
                        ddxrectot[ie] += fa;
                    }
                }
        }
    }
    free(sr1); free(sr2); free(se1); free(se2);
    return 0;
}
