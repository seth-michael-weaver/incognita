/* CENGLD (ROUTE100 WP6): level densities, matching and rhogrid in one C call each, for the analytical
 * constant-temperature + Fermi-gas model (ldmodel 1) without collective enhancement or fission
 * barriers, off the autograd graph -- the nuclei NATIVEX2's `nx2_ld.c` kernels already carry.
 *
 *   ceng_ld_match    densitymatch.f90:1 for barrier 0 as `density.matching.densitymatch`: the
 *                    Fermi-gas tables, the empirical Tmemp/Exmemp, `matching` (zbrak + rtbis),
 *                    the Tadjust/E0adjust passes and the fallbacks. It replaces ~100
 *                    zero-dim torch operations and two ctypes calls per nucleus.
 *   ceng_ld_rhogrid  exgrid.f90:241-285 as `nx2_ld_rhogrid`, with rho(J) evaluated only up to each
 *                    bin's maxJ (the rest is never written) and a bin's top row and its logs
 *                    reused as the next bin's bottom when the two energies are the same double.
 *                    Bit-identical to `nx2_ld_rhogrid`.
 *   ceng_ld_ignatyuk, ceng_ld_spincut
 *                    ignatyuk.f90 and spincut.f90 over an array of energies, as
 *                    `parameters._ignatyuk_fast` / `_spincut_fast`'s numpy branches
 *                    (binary.f90:229-230's per-bin a and spin cutoff).
 *
 * The +, -, *, / are the Python expressions' own, in their order, with contraction off; float32
 * steps are float32 here. Held to 1e-13 against the torch/numpy path (tests/hf/test_cengld.py).
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md. */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "ld.h"

int64_t nx2_ld_match_root(const double *logrho, const double *temprho, int64_t n, double x1,
                          double x2, int64_t nseg, double E0save, double NLo, double NP, double EL,
                          double EP, double sentinel, double xacc, double *roots);

/* The inputs of `ceng_ld_match` besides the kernel scalars (density/ld_ceng.py `_M_*`). */
enum {
    M_A = 0, M_NEX, M_FLAGLDGLOBAL, M_FLAGCTMGLOB, M_LDPAREXIST, M_FLAGCOL, M_GAMMALD, M_DW,
    M_EXADJ, M_TADJ, M_E0ADJ, M_T, M_E0, M_EX, M_LIGHT_T_ON, M_LIGHT_T, M_LIGHT_E0_ON, M_LIGHT_E0,
    M_LIGHT_EX_ON, M_LIGHT_EX, M_NLOW, M_NTOP, M_EL, M_EP, M_XACC, M_SENTINEL, M_N
};

#define NSEG 100

/* `nx2_ld_fermi_tables`, bit for bit, with each half-grid energy evaluated once: the top point of
 * entry k and the bottom point of entry k+1 are the same double dEx * (k + 1/2). */
static int64_t fermi_tables(const double *p, int64_t nEx, double dEx, double *logrho,
                            double *temprho, double *half)
{
    double sc;
    double prev = 0.0;
    for (int64_t k = 0; k < nEx + 2; k++) {
        logrho[k] = 0.0;
        temprho[k] = 0.0;
    }
    /* half[m] holds the point dEx * (m / 2), m = 1..2 nEx + 1: entry k reads m = 2k - 1, 2k, 2k + 1 */
    for (int64_t m = 1; m <= 2 * nEx + 1; m++) {
        int64_t k = m / 2;
        int j = (int)(m - 2 * k);
        double eex = dEx * ((double)k + 0.5 * j);
        double U = eex - p[P_PAIR];
        if (U > 0.0) {
            double ald = ignatyuk(p, eex);
            half[m] = log(fermi(p, ald, eex, p[P_PAIR], &sc));
        } else {
            half[m] = 0.0;
        }
    }
    for (int64_t k = nEx; k >= 1; k--) {
        double lo = half[2 * k - 1], hi = half[2 * k + 1];
        logrho[k] = half[2 * k];
        double raw = hi != lo ? dEx / (hi - lo) : 0.0;
        temprho[k] = raw <= 0.1 ? prev : raw;
        prev = temprho[k];
    }
    int64_t nstart = 1;
    for (int64_t k = nEx - 1; k >= 1; k--) {
        if (temprho[k] >= temprho[k + 1]) {
            nstart = k + 1;
            break;
        }
    }
    return nstart;
}

static float f32(double x) { return (float)x; }

/* matching.py `_idx`: int(float32(x) / float32(0.1)) */
static int64_t idx32(double x) { return (int64_t)((float)x / 0.1f); }

/* numerics.pol1 */
static double pol1(double x1, double x2, double y1, double y2, double x)
{
    return y1 + (x - x1) / (x2 - x1) * (y2 - y1);
}

typedef struct {
    const double *p;
    const double *logrho, *temprho;
    int64_t nEx, nstart;
    double dEx, P;
    int bad; /* an index Python would raise on: the caller runs the torch path instead */
} Tab;

/* densitymatch's `lower_limit` */
static double lower_limit(const Tab *t, double Exm)
{
    double ald = ignatyuk(t->p, Exm);
    double v = 2.25 / ald + t->P;
    return (v > 0.0 ? v : 0.0) + 0.11;
}

/* densitymatch's `t_from_ex` */
static double t_from_ex(Tab *t, double Exm)
{
    int64_t i = idx32(Exm);
    if (i < 0 || i + 1 > t->nEx + 1) {
        t->bad = 1;
        return 0.0;
    }
    return pol1((double)i * t->dEx, (double)(i + 1) * t->dEx, t->temprho[i], t->temprho[i + 1],
                Exm);
}

/* numerics.locate on xx = temprho[1:] over positions ib..ie: searchsorted's bisection */
static int64_t locate_shifted(const Tab *t, double x, int64_t ib, int64_t ie)
{
    const double *xx = t->temprho + 1;
    if (ib > ie)
        return 0;
    int64_t n = ie - ib + 1, lo = 0, hi = n;
    int ascend = xx[ie] >= xx[ib];
    while (lo < hi) {
        int64_t mid = lo + (hi - lo) / 2;
        /* ascending: searchsorted(seg, x, right=True); descending: searchsorted(-seg, -x) */
        if (ascend ? (xx[ib + mid] <= x) : (-xx[ib + mid] < -x))
            lo = mid + 1;
        else
            hi = mid;
    }
    int64_t j = ib - 1 + lo;
    if (x == xx[ib])
        j = ib;
    else if (x == xx[ie])
        j = ie - 1;
    return j;
}

/* densitymatch's `ex_from_t`: returns i, the value through *e when i > 0 */
static int64_t ex_from_t(Tab *t, double Tm, double *e)
{
    int64_t i = locate_shifted(t, Tm, t->nstart, t->nEx - 1);
    if (i > 0) {
        if (i + 1 > t->nEx + 1) {
            t->bad = 1;
            return 0;
        }
        *e = pol1(t->temprho[i], t->temprho[i + 1], (double)i * t->dEx, (double)(i + 1) * t->dEx,
                  Tm);
    }
    return i;
}

/* matching.py `matching` */
static double matching(Tab *t, const double *m, double Exmemp, double E0save, double xacc)
{
    double ald = ignatyuk(t->p, Exmemp);
    double lo = 2.25 / ald + t->P;
    double x1 = (double)f32((lo > 0.0 ? lo : 0.0) + 0.11);
    double x2 = (double)f32(19.0 + 300.0 / m[M_A]);
    float dx = (f32(x2) - f32(x1)) / (float)NSEG;
    if (E0save == m[M_SENTINEL] && (int64_t)m[M_NLOW] == (int64_t)m[M_NTOP] && m[M_EL] != 0.0 &&
        m[M_EL] == m[M_EP])
        return (double)(f32(x1) + dx);
    double roots[2];
    int64_t nb = nx2_ld_match_root(t->logrho, t->temprho, t->nEx + 2, x1, x2, NSEG, E0save,
                                   m[M_NLOW], m[M_NTOP], m[M_EL], m[M_EP], m[M_SENTINEL], xacc,
                                   roots);
    if (nb == 0)
        return 0.0;
    double Exm = roots[0];
    if (nb > 1)
        Exm = fabs(roots[0] - Exmemp) > fabs(roots[1] - Exmemp) ? roots[1] : roots[0];
    if (Exm < x1 || Exm > x2)
        Exm = 0.0;
    return Exm;
}

/* densitymatch.f90 for barrier 0. p: the kernel scalars of the unmatched nucleus (P_N; its spin
 * cutoff scalars read Exmatch, so only the tables and ignatyuk use them), m: M_N inputs. out: T,
 * E0, Exmatch. Returns 0, or -1 where the Python path would raise (the caller then runs it). */
int ceng_ld_match(const double *p, const double *m, double *out)
{
    int64_t nEx = (int64_t)m[M_NEX];
    double A = m[M_A];
    double *buf = (double *)malloc(sizeof(double) * 4 * (size_t)(nEx + 2));
    if (!buf)
        return -1;
    Tab t = {p, buf, buf + nEx + 2, nEx, 0, (double)0.1f, p[P_PAIR], 0};
    t.nstart = fermi_tables(p, nEx, t.dEx, buf, buf + nEx + 2, buf + 2 * (nEx + 2));
    const double S = m[M_SENTINEL];
    double T_cur = m[M_T], E0_cur = m[M_E0], Ex_cur = m[M_EX];
    if (A <= 18.0) {
        if (m[M_LIGHT_T_ON] != 0.0)
            T_cur = m[M_LIGHT_T];
        if (m[M_LIGHT_E0_ON] != 0.0)
            E0_cur = m[M_LIGHT_E0];
        if (m[M_LIGHT_EX_ON] != 0.0)
            Ex_cur = m[M_LIGHT_EX];
    }
    double gdw = m[M_GAMMALD] * m[M_DW];
    double c0, c1, c2;
    if (m[M_FLAGCOL] != 0.0) {
        c0 = -0.22; c1 = 9.4; c2 = 2.67;
    } else {
        c0 = -0.25; c1 = 10.2; c2 = 2.33;
    }
    double arg = A * (1.0 + gdw);
    double Tmemp = c0 + c1 / sqrt(arg > 1.0 ? arg : 1.0);
    double Exmemp = c2 + 253.0 / A + t.P;
    Tmemp = (double)f32(Tmemp > 0.1 ? Tmemp : 0.1);
    Exmemp = (double)f32(Exmemp > 0.1 ? Exmemp : 0.1);
    for (int pass = 0; pass < 3; pass++) {
        double Tm = T_cur;
        double Exm = m[M_EXADJ] * Ex_cur;
        double E0m = E0_cur;
        double E0save = E0m;
        double e;
        int64_t i;
        if (m[M_FLAGLDGLOBAL] != 0.0) {
            Tm = Tmemp;
            Exm = Exmemp;
        }
        if (Tm == 0.0 && Exm == 0.0) {
            if (m[M_LDPAREXIST] != 0.0 && m[M_FLAGCTMGLOB] == 0.0) {
                Exm = matching(&t, m, Exmemp, E0save, m[M_XACC]);
                if (Exm > 0.0) {
                    Tm = t_from_ex(&t, Exm);
                } else {
                    Tm = Tmemp;
                    i = ex_from_t(&t, Tm, &e);
                    if (i > 0 && i <= nEx - 1)
                        Exm = e;
                }
            } else {
                Tm = Tmemp;
                i = ex_from_t(&t, Tm, &e);
                if (i > 0)
                    Exm = e;
            }
            if (Exm <= lower_limit(&t, Exm))
                Exm = 0.0;
            if (Exm > 3.0 * Exmemp)
                Exm = 0.0;
        }
        if (Exm == 0.0) {
            if (Tm == 0.0)
                Tm = Tmemp;
            i = ex_from_t(&t, Tm, &e);
            if (i > 0)
                Exm = e;
            if (Exm <= lower_limit(&t, Exm))
                Exm = Exmemp;
            if (Exm == 0.0)
                Exm = Exmemp;
            if (Exm > 3.0 * Exmemp)
                Exm = Exmemp;
        }
        if (Tm == 0.0) {
            if (Exm <= lower_limit(&t, Exm))
                Exm = Exmemp;
            if (Exm > 3.0 * Exmemp)
                Exm = Exmemp;
            if (idx32(Exm) > 0)
                Tm = t_from_ex(&t, Exm);
        }
        if (E0m == S) {
            i = idx32(Exm);
            if (i > 0) {
                if (i + 1 > nEx + 1) {
                    t.bad = 1;
                } else {
                    double lr = pol1((double)i * t.dEx, (double)(i + 1) * t.dEx, t.logrho[i],
                                     t.logrho[i + 1], Exm);
                    E0m = Exm - Tm * log(Tm * exp(lr));
                }
            }
        }
        if (t.bad)
            break;
        if (Tm == 0.0)
            Tm = Tmemp;
        if (T_cur == 0.0 && m[M_TADJ] != 1.0) {
            T_cur = m[M_TADJ] * Tm;
            continue;
        }
        T_cur = Tm;
        if (E0_cur == S && m[M_E0ADJ] != 1.0) {
            E0_cur = m[M_E0ADJ] * E0m;
            continue;
        }
        E0_cur = E0m;
        Ex_cur = Exm;
        break;
    }
    free(buf);
    if (t.bad)
        return -1;
    out[0] = T_cur;
    out[1] = E0_cur;
    out[2] = Ex_cur;
    return 0;
}

/* rho(J) for J = rodd + 0..top at one energy, and log(rho(J) * (1 + 1e-10)) for the edges */
static void edge_row(const double *p, double eex, double rodd, int64_t top, double *r, double *lq)
{
    rho_row(p, eex, rodd, top, r);
    for (int64_t j = 0; j <= top; j++) {
        double q = r[j] * (1.0 + 1.0e-10);
        lq[j] = q > 0 ? log(q) : 0.0;
    }
}

/* `nx2_ld_rhogrid`, bit for bit, on the bins nlast + 1 .. n - 1 with maxj >= 0 (its `sel`) */
int ceng_ld_rhogrid(const double *p, const double *ex, const double *dex, const int64_t *maxj,
                    int64_t nlast, int64_t n, int64_t numj, double rodd, double *out)
{
    double r1[128], r2[128], r3[128], l1s[128], l3s[128];
    if (numj + 1 > 128)
        return -1;
    int64_t nj = numj + 1;
    double e3prev = NAN;
    int64_t top3prev = -1;
    for (int64_t k = nlast + 1 > 0 ? nlast + 1 : 0; k < n; k++) {
        double e = ex[k], dx = dex[k];
        int64_t top = maxj[k] < numj ? maxj[k] : numj;
        if (top < 0)
            continue;
        double eb = e - 0.5 * dx, et = e + 0.5 * dx;
        if (eb == e3prev && top <= top3prev) {
            /* the previous bin's top row, already evaluated at this energy for spins 0..top */
            memcpy(r1, r3, sizeof(double) * (size_t)(top + 1));
            memcpy(l1s, l3s, sizeof(double) * (size_t)(top + 1));
        } else {
            edge_row(p, eb, rodd, top, r1, l1s);
        }
        rho_row(p, e, rodd, top, r2);
        edge_row(p, et, rodd, top, r3, l3s);
        e3prev = et;
        top3prev = top;
        for (int64_t j = 0; j <= top; j++) {
            double a2 = r2[j];
            double q1 = r1[j] * (1.0 + 1.0e-10);
            double q3 = r3[j] * (1.0 + 1.0e-10);
            double v = dx * a2;
            if (q1 > 0 && a2 > 0 && q3 > 0) {
                double l1 = l1s[j], l2 = log(a2), l3 = l3s[j];
                if (l2 != l1 && l2 != l3)
                    v = 0.5 * dx * ((q1 - a2) / (l1 - l2) + (a2 - q3) / (l2 - l3));
            }
            out[(k * nj + j) * 2] = v;
            out[(k * nj + j) * 2 + 1] = v;
        }
    }
    return 0;
}

/* parameters._ignatyuk_fast's array branch, element by element. f: `_ign_floats` (delta, alimit,
 * gammald, deltaW, colldamp, A/13, Ufermi, cfermi). */
int ceng_ld_ignatyuk(const double *f, const double *eex, int64_t n, double *out)
{
    double delta = f[0], alimit = f[1], gam = f[2], dW = f[3], aldlow = f[5], uf = f[6], cf = f[7];
    int colldamp = f[4] != 0.0;
    for (int64_t i = 0; i < n; i++) {
        double U = eex[i] - delta;
        int pos = U > 0.0;
        double Us = pos ? U : 1.0;
        double expo = gam * Us;
        double fU = fabs(expo) <= 80.0 ? 1.0 - exp(-expo) : 1.0;
        double damp = pos ? 1.0 + fU * dW / Us : 1.0 + dW * gam;
        double aldlim = alimit;
        if (colldamp) {
            double e = (U - uf) / cf;
            double q = e > -80.0 ? 1.0 / (1.0 + exp(-e)) : 0.0;
            aldlim = aldlow * q + alimit * (1.0 - q);
        }
        double v = aldlim * damp;
        out[i] = v < 1.0 ? 1.0 : v;
    }
    return 0;
}

/* parameters._spincut_fast's array branch, element by element. f: `_sc_floats` (scutconst, Em,
 * Ed, sdisc, s2m, colld, delta) with f[5] read only when colld_on; ald has na = 1 or n entries. */
int ceng_ld_spincut(const double *f, int64_t model1, int64_t colld_on, const double *ald, int64_t na,
                    const double *eex, int64_t n, double *out)
{
    double scutconst = f[0], Em = f[1], Ed = f[2], sdisc = f[3], s2m = f[4], colld = f[5];
    double delta = f[6];
    double denom = Em != Ed ? Em - Ed : 1.0;
    for (int64_t i = 0; i < n; i++) {
        double x = eex[i];
        double a = ald[na == 1 ? 0 : i];
        double below = (Em != Ed && x > Ed) ? sdisc + (x - Ed) / denom * (s2m - sdisc) : sdisc;
        double U = x - delta;
        int okU = U > 0.0;
        double Us = okU ? U : 1.0;
        double above = model1 ? scutconst * sqrt(a * Us) : scutconst * sqrt(Us / a);
        if (!okU)
            above = sdisc;
        double sc = x <= Em ? below : above;
        if (colld_on)
            sc = colld * sc;
        out[i] = sc < sdisc ? sdisc : sc;
    }
    return 0;
}

/* CENGLD2: `feeding.Cascade.spec`'s level-density rows of one cascade nucleus in one call.
 *   maxj  exgrid.f90:239-256 as `feeding._maxj_of`: numJ everywhere, and on the continuum bins
 *         nl + 1 .. n - 1 (when there are any) max_spin_index of spincut at a = A/8 -- the
 *         double spin cutoff of `_spincut_np`, its float32 cast, sqrt and truncation.
 *   rho   `ceng_ld_rhogrid` on those bins (the caller's zeros stay where it writes nothing).
 * sc: `feeding._spincut_parts` (scutconst, Em, sdisc, s2m, Ed, denom, interp, delta, model).
 * p: the kernel scalars (`ld_nx2._par`); NULL is allowed only for a grid with no continuum bin.
 * Returns 0, or 1 when `p` is NULL and a continuum bin needs it (nothing written to rho). */
int ceng_ld_spec(const double *p, const double *sc, const double *ex, const double *dex,
                 int64_t nl, int64_t n, int64_t numj, int64_t A, int64_t *maxj, double *rho)
{
    for (int64_t k = 0; k < n; k++)
        maxj[k] = numj;
    if (nl + 1 >= n)
        return 0;
    double scutconst = sc[0], Em = sc[1], sdisc = sc[2], s2m = sc[3], Ed = sc[4], denom = sc[5];
    int interp = sc[6] != 0.0, model1 = sc[8] == 1.0;
    double delta = sc[7];
    double ald = (double)A / 8.0;
    for (int64_t k = nl + 1 > 0 ? nl + 1 : 0; k < n; k++) {
        double x = ex[k];
        double below = (interp && x > Ed) ? sdisc + (x - Ed) / denom * (s2m - sdisc) : sdisc;
        double U = x - delta;
        int okU = U > 0.0;
        double Us = okU ? U : 1.0;
        double root = sqrt(model1 ? ald * Us : Us / ald);
        double above = okU ? scutconst * root : sdisc;
        double s = x <= Em ? below : above;
        s = s < sdisc ? sdisc : s;
        float r = sqrtf((float)s);
        int64_t j = (int64_t)(4.0f + 3.0f * r);
        maxj[k] = j < numj ? j : numj;
    }
    if (p == NULL)
        return 1;
    return ceng_ld_rhogrid(p, ex, dex, maxj, nl, n, numj, 0.5 * (double)(A % 2), rho);
}
