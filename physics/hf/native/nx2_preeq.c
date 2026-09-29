/* NATIVEX2 lever `preeq`: the two-component particle-hole state density `phdens2` (finite-well
 * correction included) over broadcast arrays, and the four exciton-model transition rates.
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * TALYS: phdens2.f90:1 (phdens2), finitewell.f90:1 (finitewell), preeqinit.f90:1 (Apauli2),
 *        lambdapiplus.f90:1, lambdanuplus.f90:1, lambdapinu.f90:1, lambdanupi.f90:1
 * Python side: physics/hf/preeq/preeq_nx2.py; test: tests/hf/test_nx2_preeq.py.
 *
 * Every element sees the operations of density/particle_hole._phdens2_arr / _finitewell_arr and
 * of preeq/exciton.py's transition-rate functions in their order (the k-sum as native/nativex.c
 * nx_sum_terms); the per-element hole limit h replaces the numpy path's array-wide hmax, which
 * only adds skipped terms, and the nine well-depth weights of the surface average are kept while
 * the well depth repeats (they do not depend on the energy). Held to closeness (libm pow/exp
 * against numpy's and torch's), not to bits. */
#include <math.h>
#include <stdint.h>

typedef struct {
    const double *nfac; /* n! for n = 0..nfac_top */
    int64_t nfac_top;
    const double *tab;  /* (-1)^k C(h,k): rows k = 1..hmax, columns h = 0..ncols-1 */
    int64_t ncols, hmax;
    double efermi, floor_;
} phconst;

typedef struct { /* values kept while their arguments repeat (pure functions of them) */
    int valid; /* the surface average's weights for the well depth `ewell` */
    double ewell, wd, wtsum, wt[9], ew[9];
    int64_t npi, nnu; /* gp^npi and gn^nnu */
    double gp, gn, pgp, pgn;
} wellcache;

/* 1 + sum_{k=1..h} (-1)^k C(h,k) ((e - k ew)/e)^nm1 over the kept terms (finitewell.f90:96-105) */
static double sum_terms(double e, double ew, int64_t h, double nm1, const phconst *pc)
{
    double a = 1.0;
    int64_t hc = h < 0 ? 0 : (h > pc->ncols - 1 ? pc->ncols - 1 : h);
    if (e > 0.0) {
        int64_t top = h < pc->hmax ? h : pc->hmax;
        for (int64_t k = 1; k <= top; k++) {
            double ek = e - k * ew;
            if (ek > 0.0) a += pc->tab[(k - 1) * pc->ncols + hc] * pow(ek / e, nm1);
        }
    }
    return a;
}

/* finitewell(p, h, Eex, Ewell, surfwell) (finitewell.f90:48-107) */
static double finitewell(int64_t p, int64_t h, double eex, double ewell, int surf,
                         const phconst *pc, wellcache *wc)
{
    int64_t n = p + h;
    double nm1 = (double)(n - 1), ef = pc->efermi;
    if (!(surf && ewell < ef - 0.5)) {
        if (eex <= ewell || (h == 1 && n == 1)) return 1.0;
        return sum_terms(eex, ewell, h, nm1, pc);
    }
    if (!wc->valid || wc->ewell != ewell) {
        double widthdis = ewell * (ef - ewell) / (2.0 * ef);
        double wd = widthdis > 0.0 ? widthdis : 1.0, wtsum = 0.0;
        for (int j = 0; j < 9; j++) {
            double ewj = ewell + (double)(j - 4) * widthdis;
            int inrange = ewj <= ef && ewj >= 0.0 && widthdis > 0.0;
            double x = inrange ? (ewj - ewell) / wd : 0.0;
            wc->wt[j] = (inrange && x <= 80.0) ? 1.0 / ((1.0 + exp(x)) * (1.0 + exp(-x))) : 0.0;
            wc->ew[j] = inrange ? ewj : 1.0;
            wtsum = wtsum + wc->wt[j];
        }
        wc->valid = 1;
        wc->ewell = ewell;
        wc->wd = wd;
        wc->wtsum = wtsum;
    }
    if (p == 0 && h == 1) { /* the single surface hole, finitewell.f90:66-73 */
        double hole = 1.0 / (1.0 + exp((eex - ewell) / wc->wd));
        if (eex < ewell) hole = 1.0;
        if (eex > 1.16 * ef) hole = 0.0;
        return hole;
    }
    double fwtsum = 0.0; /* the average over nine well depths, finitewell.f90:75-94 */
    for (int j = 0; j < 9; j++) {
        double fw = eex > 0.0 ? sum_terms(eex, wc->ew[j], h, nm1, pc) : 0.0;
        fwtsum = fwtsum + wc->wt[j] * fw;
    }
    return wc->wtsum > 0.0 ? fwtsum / wc->wtsum : 1.0;
}

/* Apauli2(ppi, hpi, pnu, hnu) with the given g's (preeqinit.f90:100-119) */
static double apauli2(int64_t ip, int64_t ih, int64_t jp, int64_t jh, double gp, double gn)
{
    if (ip == -1 || ih == -1 || jp == -1 || jh == -1) return 0.0;
    double ipf = (double)ip, ihf = (double)ih, jpf = (double)jp, jhf = (double)jh;
    double mp = ipf > ihf ? ipf : ihf, mn = jpf > jhf ? jpf : jhf;
    double eppi = mp * mp / gp, epnu = mn * mn / gn;
    double factorp = (ipf * ipf + ihf * ihf + ipf + ihf) / (4.0 * gp);
    double factorn = (jpf * jpf + jhf * jhf + jpf + jhf) / (4.0 * gn);
    return eppi + epnu - factorp - factorn;
}

/* phdens2(ppi, hpi, pnu, hnu, gsp, gsn, Eex, Ewell, surfwell) with the Pauli term `ap` given
 * (phdens2.f90:40-79) */
static double phdens2(int64_t ip, int64_t ih, int64_t jp, int64_t jh, double gp, double gn,
                      double e, double ewell, int surf, double ap, const phconst *pc,
                      wellcache *wc)
{
    double ipf = (double)ip, ihf = (double)ih, jpf = (double)jp, jhf = (double)jh;
    double factorn = (jpf * jpf + jhf * jhf + jpf + jhf) / (4.0 * gn);
    double factorp = (ipf * ipf + ihf * ihf + ipf + ihf) / (4.0 * gp);
    int64_t n = ip + ih + jp + jh;
    if (!(ip >= 0 && ih >= 0 && jp >= 0 && jh >= 0 && n != 0 && ap + factorn + factorp < e))
        return 0.0;
    int64_t f[5] = {ip, ih, jp, jh, n - 1};
    for (int a = 0; a < 5; a++) f[a] = f[a] < 0 ? 0 : (f[a] > pc->nfac_top ? pc->nfac_top : f[a]);
    const double *nf = pc->nfac;
    double fac1 = nf[f[0]] * nf[f[1]] * nf[f[2]] * nf[f[3]] * nf[f[4]];
    if (wc->npi != ip + ih || wc->gp != gp) {
        wc->npi = ip + ih;
        wc->gp = gp;
        wc->pgp = pow(gp, (double)(ip + ih));
    }
    if (wc->nnu != jp + jh || wc->gn != gn) {
        wc->nnu = jp + jh;
        wc->gn = gn;
        wc->pgn = pow(gn, (double)(jp + jh));
    }
    double factor = wc->pgp * wc->pgn / fac1;
    double dens = factor * pow(e - ap, (double)(n - 1));
    dens = dens * finitewell(ip + jp, ih + jh, e, ewell, surf, pc, wc);
    return dens < pc->floor_ ? 0.0 : dens;
}

/* phdens2 over the broadcast shape `shape` (4 axes). Inputs, each with 4 element strides in
 * `st` (row i = input i, 0 on a broadcast axis): 0 ppi, 1 hpi, 2 pnu, 3 hnu (int64), 4 gsp,
 * 5 gsn, 6 ex, 7 ewell, 9 ap2 (double), 8 surfwell (uint8). Output contiguous. Returns 0. */
int nx2_preeq_phdens2(const int64_t *shape, const int64_t *st, const int64_t *ppi,
                      const int64_t *hpi, const int64_t *pnu, const int64_t *hnu,
                      const double *gsp, const double *gsn, const double *ex, const double *ewell,
                      const uint8_t *surf, const double *ap2, double efermi, double floor_,
                      const double *nfac, int64_t nfac_top, const double *tab, int64_t ncols,
                      int64_t hmax, double *out)
{
    phconst pc = {nfac, nfac_top, tab, ncols, hmax, efermi, floor_};
    wellcache wc = {0, 0.0, 0.0, 0.0, {0.0}, {0.0}, -1, -1, 0.0, 0.0, 0.0, 0.0};
    int64_t o[10], x = 0;
    for (int64_t i0 = 0; i0 < shape[0]; i0++)
    for (int64_t i1 = 0; i1 < shape[1]; i1++)
    for (int64_t i2 = 0; i2 < shape[2]; i2++)
    for (int64_t i3 = 0; i3 < shape[3]; i3++, x++) {
        for (int a = 0; a < 10; a++)
            o[a] = i0 * st[4 * a] + i1 * st[4 * a + 1] + i2 * st[4 * a + 2] + i3 * st[4 * a + 3];
        out[x] = phdens2(ppi[o[0]], hpi[o[1]], pnu[o[2]], hnu[o[3]], gsp[o[4]], gsn[o[5]],
                         ex[o[6]], ewell[o[7]], surf[o[8]] != 0, ap2[o[9]], &pc, &wc);
    }
    return 0;
}

/* The exciton state (s) shifted by (a, b, c, d) */
#define ST(a, b, c, d) ppi[s] + (a), hpi[s] + (b), pnu[s] + (c), hnu[s] + (d)

/* The four transition rates lambdapiplus, lambdanuplus, lambdapinu, lambdanupi [s^-1] for C cases
 * and S exciton states, into out (4, C, S) contiguous. ppi..hnu (S,), gsp, gsn (C,), u, edepth,
 * m2pipi, m2nunu, m2pinu, m2nupi (C, S) contiguous doubles, surf (C, S) uint8. `numeric` 1 is
 * preeqmode 2 (the bin integrals, closed form for n = 1), 0 the closed form everywhere;
 * `nexcbins` the integration bins. Returns 0. */
int nx2_preeq_transition(int64_t C, int64_t S, const int64_t *ppi, const int64_t *hpi,
                         const int64_t *pnu, const int64_t *hnu, const double *gsp,
                         const double *gsn, const double *u_, const double *edepth_,
                         const uint8_t *surf_, const double *m2pipi_, const double *m2nunu_,
                         const double *m2pinu_, const double *m2nupi_, int64_t numeric,
                         int64_t nexcbins, double tph, double efermi, double floor_,
                         const double *nfac, int64_t nfac_top, const double *tab, int64_t ncols,
                         int64_t hmax, double *out)
{
    phconst pc = {nfac, nfac_top, tab, ncols, hmax, efermi, floor_};
    wellcache wc = {0, 0.0, 0.0, 0.0, {0.0}, {0.0}, -1, -1, 0.0, 0.0, 0.0, 0.0};
    /* the collision channels of lambdapiplus / lambdanuplus (lambdapiplus.f90:108-186):
     * shift of the state for L and for the residual (the same), colliding density, M2 (0 pipi,
     * 1 nunu, 2 pinu, 3 nupi), g (0 gsp, 1 gsn) */
    static const int chan[2][4][10] = {
        {{-1, 0, 0, 0, 2, 1, 0, 0, 0, 0}, {0, -1, 0, 0, 1, 2, 0, 0, 0, 0},
         {0, 0, -1, 0, 1, 1, 1, 0, 3, 1}, {0, 0, 0, -1, 1, 1, 0, 1, 3, 1}},
        {{0, 0, -1, 0, 0, 0, 2, 1, 1, 1}, {0, 0, 0, -1, 0, 0, 1, 2, 1, 1},
         {-1, 0, 0, 0, 1, 0, 1, 1, 2, 0}, {0, -1, 0, 0, 0, 1, 1, 1, 2, 0}}};
    for (int64_t c = 0; c < C; c++) {
        double gp = gsp[c], gn = gsn[c];
        for (int64_t s = 0; s < S; s++) {
            int64_t cs = c * S + s;
            double u = u_[cs], ed = edepth_[cs];
            int sw = surf_[cs] != 0;
            double m2[4] = {m2pipi_[cs], m2nunu_[cs], m2pinu_[cs], m2nupi_[cs]};
            int64_t n = ppi[s] + hpi[s] + pnu[s] + hnu[s];
            int64_t p = ppi[s] + pnu[s], h = hpi[s] + hnu[s];
            double nf = (double)n;
            double ap0 = apauli2(ST(0, 0, 0, 0), gp, gn);
            double rate[4];
            if (n == 0) {
                for (int r = 0; r < 4; r++) out[r * C * S + cs] = 0.0;
                continue;
            }
            if (!numeric || n == 1) {
                /* lambdapiplus / lambdanuplus closed form (lambdapiplus.f90:96-107) */
                double fac1 = 2.0 * nf * (nf + 1.0);
                for (int kind = 0; kind < 2; kind++) {
                    double gs = kind == 0 ? gp : gn;
                    double factor1 = tph * gs * gs / fac1;
                    double ap_plus = kind == 0 ? apauli2(ST(1, 1, 0, 0), gp, gn)
                                               : apauli2(ST(0, 0, 1, 1), gp, gn);
                    double npi = (double)(ppi[s] + hpi[s]), nnu = (double)(pnu[s] + hnu[s]);
                    double factor3 = kind == 0 ? npi * gp * m2[0] + 2.0 * nnu * gn * m2[2]
                                               : nnu * gn * m2[1] + 2.0 * npi * gp * m2[3];
                    double term1 = u - ap_plus, term2 = u - ap0;
                    int ok = term1 > 0.0 && term2 > 0.0;
                    double term12 = ok ? term1 / term2 : 1.0;
                    ok = ok && term12 >= 0.01;
                    rate[kind] = 0.0;
                    if (ok) {
                        double factor2 = term1 * term1 * pow(term12, nf - 1.0);
                        rate[kind] = factor1 * factor2 * factor3
                            * finitewell(p + 1, h + 1, u, ed, sw, &pc, &wc);
                    }
                }
                /* lambdapinu / lambdanupi closed form (lambdapinu.f90:72-85) */
                for (int kind = 0; kind < 2; kind++) {
                    double factor1, ap_x;
                    int has;
                    if (kind == 0) {
                        factor1 = tph * (double)(ppi[s] * hpi[s]) * m2[2] / nf * gn * gn;
                        ap_x = apauli2(ST(-1, -1, 1, 1), gp, gn);
                        has = ppi[s] > 0 && hpi[s] > 0;
                    } else {
                        factor1 = tph * (double)(pnu[s] * hnu[s]) * m2[3] / nf * gp * gp;
                        ap_x = apauli2(ST(1, 1, -1, -1), gp, gn);
                        has = pnu[s] > 0 && hnu[s] > 0;
                    }
                    double bfactor = has ? (ap0 > ap_x ? ap0 : ap_x) : ap0;
                    double factor2 = u - bfactor, factor3 = u - ap0;
                    int ok = factor2 > 0.0 && factor3 > 0.0;
                    double factor23 = ok ? factor2 / factor3 : 1.0;
                    ok = ok && factor23 >= 0.01;
                    rate[2 + kind] = 0.0;
                    if (ok) {
                        double factor4 = 2.0 * (u - bfactor) + (has ? nf * fabs(ap0 - ap_x) : 0.0);
                        rate[2 + kind] = factor1 * pow(factor23, nf - 1.0) * factor4
                            * finitewell(p, h, u, ed, sw, &pc, &wc);
                    }
                }
            } else {
                double phtot = phdens2(ST(0, 0, 0, 0), gp, gn, u, ed, sw, ap0, &pc, &wc);
                /* lambdapiplus / lambdanuplus, the bin integrals (lambdapiplus.f90:108-186) */
                for (int kind = 0; kind < 2; kind++) {
                    double ap_target = kind == 0 ? apauli2(ST(1, 1, 0, 0), gp, gn)
                                                 : apauli2(ST(0, 0, 1, 1), gp, gn);
                    double total = 0.0;
                    for (int ch = 0; ch < 4; ch++) {
                        const int *q = chan[kind][ch];
                        double ap_l = apauli2(ST(q[0], q[1], q[2], q[3]), gp, gn);
                        double ap_d = apauli2(q[4], q[5], q[6], q[7], gp, gn);
                        double l1 = ap_target - ap_l, l2 = u - ap_l;
                        double dex = (l2 - l1) / (double)nexcbins;
                        double g = q[9] == 0 ? gp : gn, acc = 0.0;
                        for (int64_t i = 0; i < nexcbins; i++) {
                            double uu = l1 + ((double)(i + 1) - 0.5) * dex;
                            double coll = phdens2(q[4], q[5], q[6], q[7], gp, gn, uu, ed, sw,
                                                  ap_d, &pc, &wc);
                            double lam = tph * m2[q[8]] * coll;
                            double resid = phdens2(ST(q[0], q[1], q[2], q[3]), gp, gn, u - uu, ed,
                                                   sw, ap_l, &pc, &wc);
                            acc = acc + lam * g * dex * resid;
                        }
                        total = total + acc;
                    }
                    rate[kind] = phtot > 0.0 ? total / phtot : 0.0;
                }
                /* lambdapinu / lambdanupi, the bin integrals (lambdapinu.f90:86-137) */
                for (int kind = 0; kind < 2; kind++) {
                    int a = kind == 0 ? 1 : 0, b = 1 - a; /* (1,1,0,0) pair for pinu */
                    double ap_l = kind == 0 ? apauli2(ST(-1, -1, 0, 0), gp, gn)
                                            : apauli2(ST(0, 0, -1, -1), gp, gn);
                    double ap_coll = apauli2(b, b, a, a, gp, gn);
                    double ap_pair = apauli2(a, a, b, b, gp, gn);
                    double l1 = ap0 - ap_l, l2 = u - ap_l;
                    double dex = (l2 - l1) / (double)nexcbins, acc = 0.0;
                    double m2k = m2[2 + kind];
                    for (int64_t i = 0; i < nexcbins; i++) {
                        double uu = l1 + ((double)(i + 1) - 0.5) * dex;
                        double lam = tph * m2k * phdens2(b, b, a, a, gp, gn, uu, ed, sw, ap_coll,
                                                         &pc, &wc);
                        double term = lam * phdens2(a, a, b, b, gp, gn, uu, ed, sw, ap_pair, &pc,
                                                    &wc) * dex;
                        double resid = kind == 0
                            ? phdens2(ST(-1, -1, 0, 0), gp, gn, u - uu, ed, sw, ap_l, &pc, &wc)
                            : phdens2(ST(0, 0, -1, -1), gp, gn, u - uu, ed, sw, ap_l, &pc, &wc);
                        acc = acc + term * resid;
                    }
                    rate[2 + kind] = phtot > 0.0 ? acc / phtot : 0.0;
                }
            }
            for (int r = 0; r < 4; r++) out[r * C * S + cs] = rate[r];
        }
    }
    return 0;
}
