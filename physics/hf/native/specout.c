/* SPECOUT (output only): compemission.f90 for one cascade nucleus, the compiled twin of physics/hf/specout.py's
 * `compemission` (tests/hf/test_specout.py holds the two together).
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * iv: 0 maxex, 1 Nlast, 2 E (egrid length), 3 xrows (mother rows), 4..10 drows[t] (0 = absent), 11..17 daughter maxex,
 *     18..24 daughter Nlast, 25..31 ebegin, 32..38 eend
 * dv: 0 speceps, 1..7 sep[t]
 * pv: 0 ex, 1 dex, 2 egrid, 3 Ebottom, 4 Etop, 5 deltaE, 6..12 daughter ex, 13..19 daughter dex, 20..26 mc (xrows, drows),
 *     27..33 mpe (xrows, drows) or 0, 34 out compound (7, E), 35 out multiple pre-equilibrium (7, E), 36 work (E doubles)
 */
#include <stdint.h>
#include <string.h>

int64_t so_version(void) { return 1; }

static int64_t locate_(const double *xx, int64_t ib, int64_t ie, double x)
{
    if (ib > ie) return 0;
    int64_t jl = ib - 1, ju = ie + 1;
    int ascend = xx[ie] >= xx[ib];
    while (ju - jl > 1) {
        int64_t jm = (ju + jl) / 2;
        if (ascend == (x >= xx[jm])) jl = jm;
        else ju = jm;
    }
    if (x == xx[ib]) return ib;
    if (x == xx[ie]) return ie - 1;
    return jl;
}

int so_compemission(const int64_t *iv, const double *dv, const uint64_t *pv)
{
    int64_t maxex = iv[0], nl0 = iv[1], E = iv[2], xrows = iv[3];
    const double *ex = (const double *)pv[0], *dex = (const double *)pv[1];
    const double *eg = (const double *)pv[2], *eb = (const double *)pv[3], *et = (const double *)pv[4];
    const double *de = (const double *)pv[5];
    double *outc = (double *)pv[34], *outm = (double *)pv[35], *weight = (double *)pv[36];
    double speceps = dv[0];
    for (int64_t nex = maxex; nex > nl0; nex--) {
        double exinc = ex[nex], dexinc = dex[nex];
        double ex0plus = exinc + 0.5 * dexinc, ex0min = exinc - 0.5 * dexinc;
        int64_t nexmax[7];
        for (int t = 0; t < 7; t++) {
            nexmax[t] = -1;
            if (!iv[4 + t] || t == 0) continue;
            const double *exd = (const double *)pv[6 + t], *dexd = (const double *)pv[13 + t];
            double exm = ex0plus - dv[1 + t];
            if (t > 1) exm -= eg[iv[25 + t]];
            for (int64_t nexout = iv[11 + t]; nexout >= 0; nexout--) {
                if (nexout >= iv[4 + t]) continue;
                if (exd[nexout] - 0.5 * dexd[nexout] < exm) { nexmax[t] = nexout; break; }
            }
        }
        if (iv[4]) nexmax[0] = nex - 1;
        for (int t = 0; t < 7; t++) {
            int64_t nxm = nexmax[t], dr = iv[4 + t];
            int64_t ebt = iv[25 + t], eet = iv[32 + t];
            if (!dr || nxm < 0 || ebt >= eet) continue;
            int64_t NL = iv[18 + t];
            double SS = dv[1 + t];
            const double *exd = (const double *)pv[6 + t], *dexd = (const double *)pv[13 + t];
            const double *mc = (const double *)pv[20 + t], *mp = (const double *)pv[27 + t];
#define MCX(a, b) (((a) < 0 || (b) < 0 || (a) >= xrows || (b) >= dr) ? 0.0 \
                   : mc[(a) * dr + (b)] + (mp ? mp[(a) * dr + (b)] : 0.0))
            double *oc = outc + t * E, *om = outm + t * E;
            for (int64_t nexout = 0; nexout <= nxm; nexout++) {
                if (nexout == 0 && NL == 0) continue;
                double xso00 = MCX(nex, nexout);
                if (xso00 <= speceps) continue;
                double exout = exd[nexout], dEx = dexd[nexout];
                double emin, emax, eout, exm = 0.0;
                if (nexout > NL) {
                    double ex1min = exout - 0.5 * dEx, ex1plus = exout + 0.5 * dEx;
                    if (nexout == nxm && t >= 1) {
                        ex1plus = ex0plus - SS;
                        exout = 0.5 * (ex1plus + ex1min);
                    }
                    emin = ex0min - SS - ex1plus;
                    if (emin < 0.0) emin = 0.0;
                    emax = ex0plus - SS - ex1min;
                    eout = 0.5 * (emin + emax);
                } else {
                    exm = exout + SS;
                    if (exm <= ex0plus && exm > ex0min) {
                        eout = 0.5 * (ex0plus + exm) - SS - exout;
                        emin = 0.0;
                    } else {
                        eout = exinc - SS - exout;
                        emin = ex0min - SS - exout;
                    }
                    emax = ex0plus - SS - exout;
                }
                int64_t nenbeg = locate_(eb, ebt, eet, emin), nenend = locate_(eb, ebt, eet, emax);
                if (nenbeg < 1) nenbeg = 1;
                if (nenend < nenbeg) continue;
                double dE = emax - emin, dEhalf = 0.5 * dE;
                double xsom0 = MCX(nex - 1, nexout), xsop0 = MCX(nex + 1, nexout);
                if (nexout > NL) {
                    double xso0m = MCX(nex, nexout - 1), xsopm = MCX(nex + 1, nexout - 1);
                    double xsomp = MCX(nex - 1, nexout + 1), xso0p = MCX(nex, nexout + 1);
                    for (int64_t nen = nenbeg; nen <= nenend; nen++) {
                        double term, term1, term2, edist;
                        if (eg[nen] <= eout) {
                            edist = eout - eg[nen];
                            if (emin <= 0.0001) term = xso00 * (1.0 - edist / dEhalf);
                            else {
                                term1 = xso00 + 0.5 * edist / dE * (xsom0 - xso00);
                                term2 = xso0p + 0.5 * edist / dE * (xsomp - xso0p);
                                term = term1 + 0.5 * edist / dE * (term2 - term1);
                            }
                        } else {
                            edist = eg[nen] - eout;
                            if (xsop0 == 0.0) {
                                term1 = xso00 * (1.0 - 0.5 * edist / dEhalf);
                                term2 = 0.0;
                            } else {
                                term1 = xso00 + 0.5 * edist / dE * (xsop0 - xso00);
                                term2 = xso0m + 0.5 * edist / dE * (xsopm - xso0m);
                            }
                            term = term1 + 0.5 * edist / dE * (term2 - term1);
                        }
                        weight[nen] = (term > 0.0 ? term : 0.0) * de[nen];
                    }
                } else {
                    int inside = exm <= ex0plus && exm > ex0min;
                    for (int64_t nen = nenbeg; nen <= nenend; nen++) {
                        double term, edist;
                        if (eg[nen] <= eout) {
                            edist = eout - eg[nen];
                            term = inside ? xso00 * (1.0 - edist / dEhalf) : xso00 + edist / dE * (xsom0 - xso00);
                        } else {
                            edist = eg[nen] - eout;
                            term = xsop0 == 0.0 ? xso00 * (1.0 - edist / dEhalf)
                                                : xso00 + edist / dexinc * (xsop0 - xso00);
                        }
                        weight[nen] = (term > 0.0 ? term : 0.0) * de[nen];
                    }
                }
                double fracbot = (emin - eb[nenbeg]) / de[nenbeg];
                double fractop = (et[nenend] - emax) / de[nenend];
                if (nexout == NL + 1) fractop = 0.0;
                if (nenend == nenbeg) weight[nenbeg] *= 1.0 - fracbot - fractop;
                else {
                    weight[nenbeg] *= 1.0 - fracbot;
                    weight[nenend] *= 1.0 - fractop;
                }
                double sumweight = 0.0;
                for (int64_t nen = nenbeg; nen <= nenend; nen++) sumweight += weight[nen];
                if (sumweight == 0.0) continue;
                double fracmpe = (mp ? mp[nex * dr + nexout] : 0.0) / xso00;
                double factor = xso00 / sumweight;
                for (int64_t nen = nenbeg; nen <= nenend; nen++) {
                    double emisfac = factor * weight[nen] / de[nen];
                    if (nen >= ebt && nen <= eet) {
                        oc[nen] += (1.0 - fracmpe) * emisfac;
                        om[nen] += fracmpe * emisfac;
                    }
                }
            }
#undef MCX
        }
    }
    return 0;
}
