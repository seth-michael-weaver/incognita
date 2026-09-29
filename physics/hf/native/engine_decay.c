/* CENGDECAY (ROUTE100 WP5): the warm decay core of one (nuclide, incident energy) in one call.
 *
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * Task: CENGDECAY (the speed work; no physics of its own). Acceptance test:
 * tests/hf/test_engine_c.py and the WP5 gate (docs/results/hf-cengdecay.md), which hold it to the
 * nx path it replaces (`engine.ChainedFull` with MACSPEED_FAST's kernels).
 *
 * TALYS routines computed here, in the NATIVEX arrangement:
 *     multiple.f90:1 (multiple)       -- the loop over cascade nuclei, popexcl, feedexcl, xsfeed
 *     cascade.f90:1 (cascade)         -- discrete gamma cascades under S_n
 *     densprepare.f90:1 (densprepare) -- primary = .false. rows, through `nx_widths`
 *     compound.f90:1 (compound)       -- a bin's decay, through `nx_walk`
 *     fstrength.f90:1 (fstrength)     -- the photon rows, through `nx2_psf_photon`
 *
 * `ce_cascade` is `emission.multiple.multiple_emission` over every nucleus of one energy with
 * `multiple_native.decay_nucleus`, `widths_native.NativeWidths` and `decay_fast.nexmax_rows` as
 * their numpy statements, operation for operation, around the same compiled kernels (called
 * through the pointers `ce_set_kernels` is handed, i.e. the very functions of libnativex/libnx2):
 * the cells are the nx path's to the bit. Python keeps what is per nucleus and parameter-built
 * (the excitation grids and rhogrid, the fission ladder) and hands it over packed.
 *
 * Layout (int64 `ip`, double `dp`, pointer `pp`):
 *   ip: 0 maxz, 1 maxn, 2 nspec, 3 k0, 4 lmaxinc, 5 maxen, 6 Ltl, 7 Tl rows, 8 egrid length,
 *       9 L0 (gammax + 1), 10 index width W (spec index of (zix, nix) = idx[zix * W + nix])
 *   dp: 0 transeps, 1 popeps, 2 twopi
 *   pp: 0 Tl (6, rows, Ltl), 1 lmax (6, rows), 2 head0 (6), 3 egrid, 4 egrid float32 (maxen + 1),
 *       5 ebegin (6, types 1..6), 6 min(eendmax, maxen) (6), 7 idx, 8 spec ints (nspec, SI),
 *       9 spec doubles (nspec, SD), 10 spec pointers (nspec, SP), 11 PSF packs (npack, 7),
 *       12 outputs (nspec, SO), 13 fission callback, 14 spec callback, 15 PSF callback,
 *       16 multiple pre-equilibrium callback (0 below `emulpre`)
 *   ip: 11 P + 1 of the particle-hole populations (0 below `emulpre`)
 */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define NJ 41 /* NUMJ + 1 */
#define SI 16
#define SD 18
#define SP 14
#define SO 8
#define NUMZCHAN 6
#define NUMNCHAN 10

static const int64_t PARZ[7] = {0, 0, 1, 1, 1, 2, 2};
static const int64_t PARN[7] = {0, 1, 0, 1, 2, 1, 2};
static const int64_t PARSPIN2[7] = {0, 1, 1, 2, 1, 1, 0};

typedef int (*widths_fn)(const int64_t *, const uint64_t *, const double *, const uint64_t *,
                         int64_t *);
typedef int (*walk_fn)(const int64_t *, const uint64_t *, double *, int64_t, int64_t, int64_t,
                       double);
typedef int (*photon_fn)(const int64_t *, const double *, const double *, const double *,
                         const double *, const double *, const double *, int64_t, const double *,
                         int64_t, const double *, const int64_t *, double, double, double *);
/* fission widths of spec s for bins (m): (m, nj_fis, 2) in *out, nj_fis in *nj; 0 ok, 1 refuse,
 * 2 the nucleus does not fission */
typedef int (*fis_fn)(int64_t s, int64_t m, const int64_t *bins, uint64_t *out, int64_t *nj);
/* the spec index of (zix, nix), packed on demand (-1 refuses) */
typedef int64_t (*spec_fn)(int64_t zix, int64_t nix);
/* the 7 PSF pack pointers of spec s's photon strength; 0 ok */
typedef int (*psf_fn)(int64_t s, uint64_t *out);
/* `attach_mpe` of spec s: mother, flags, acc (types 1, 2), accf, mul in; the (mi, md, mp) block
 * pointer out; 0 ok, 1 refuse */
typedef int (*mpe_fn)(int64_t s, const uint64_t *arrs, uint64_t *block);

static widths_fn k_widths;
static walk_fn k_walk;
static photon_fn k_photon;

int64_t ce_version(void) { return 2; }

void ce_set_kernels(void *widths, void *walk, void *photon)
{
    k_widths = (widths_fn)widths;
    k_walk = (walk_fn)walk;
    k_photon = (photon_fn)photon;
}

/* spec ints: 0 zix, 1 nix, 2 Z, 3 A, 4 maxex, 5 nlast (unclamped), 6 nlast_grid, 7 ntop,
 *            8 rhogrid rows, 9 in the nucleus set, 12 status out, 13 mulpre (in/out)
 * spec doubles: 0 exmax, 1 discfactor, 2..8 sep(0..6), 9..16 fisom(-1..6), 17 xspopnuc (in: the
 *            binary seed, out: the surviving population)
 * spec pointers: 0 ex, 1 dex, 2 maxj (int64), 3 parlev (int64), 4 jdis, 5 tau, 6 rhogrid,
 *            7 branch offsets (maxex + 2), 8 branch level, 9 branch ratio, 10 X (rows, NJ, 2),
 *            11 XE, 12 particle-hole populations (rows, P4), 13 their presence (uint8, rows)
 * outputs (per spec): 0 popexcl (maxex + 2), 1 fisfeed (maxex + 2), 2 fisfeed flags (uint8),
 *            3 xsfeed (8, index type + 1), 4 xsfeed flags, 5 feed values (7 pointers),
 *            6 feed present (7 pointers), 7 doubles: 0 gamdis, 1..7 table created (1.0) */

typedef struct {
    const int64_t *ip;
    const double *dp;
    const uint64_t *pp;
    const int64_t *idx;
    int64_t *si;
    double *sd;
    const uint64_t *sp;
    const uint64_t *so;
} Ctx;

#define SPI(c, s) ((c)->si + (s) * SI)
#define SPD(c, s) ((c)->sd + (s) * SD)
#define SPP(c, s) ((c)->sp + (s) * SP)
#define SPO(c, s) ((c)->so + (s) * SO)

static int64_t spec_of(const Ctx *c, int64_t zix, int64_t nix)
{
    int64_t W = c->ip[10];
    if (zix < 0 || nix < 0 || nix >= W) return -1;
    return c->idx[zix * W + nix];
}

static int64_t need_spec(const Ctx *c, int64_t zix, int64_t nix)
{
    int64_t s = spec_of(c, zix, nix);
    if (s < 0 && c->pp[14]) s = ((spec_fn)c->pp[14])(zix, nix);
    return s;
}

static int records(int64_t zc, int64_t nc, int t)
{
    if (zc > NUMZCHAN || nc > NUMNCHAN) return 0;
    return !(zc == 0 && nc == 0 && t > 0);
}

static void fe_set(double *val, uint8_t *pres, int64_t ncols, int64_t a, int64_t b, double v)
{
    int64_t q = a * ncols + b;
    val[q] = (pres[q] ? val[q] : 0.0) + v;
    pres[q] = 1;
}

/* multiple_native._cascade_only: a nucleus with no bin to decay */
static double cascade_only(Ctx *c, int64_t s, int64_t zc, int64_t nc, double smin)
{
    int64_t *I = SPI(c, s);
    const uint64_t *P = SPP(c, s);
    const uint64_t *O = SPO(c, s);
    int64_t maxex = I[4], nlast = I[6], xrows = maxex + 1;
    const double *ex = (const double *)P[0], *tau = (const double *)P[5], *jdis = (const double *)P[4];
    const int64_t *parlev = (const int64_t *)P[3];
    const int64_t *boff = (const int64_t *)P[7], *bk = (const int64_t *)P[8];
    const double *br = (const double *)P[9];
    double *X = (double *)P[10], *XE = (double *)P[11];
    double *popexcl = (double *)O[0];
    double *dbl = (double *)O[7];
    int rec = records(zc, nc, 0);
    double *val = (double *)((const uint64_t *)O[5])[0];
    uint8_t *pres = (uint8_t *)((const uint64_t *)O[6])[0];
    double gamdis = 0.0;
    for (int64_t nex = maxex; nex >= 1; nex--) {
        popexcl[nex] = XE[nex];
        if (nex <= nlast && ex[nex] <= smin && tau[nex] == 0.0) {
            int64_t jj = (int64_t)jdis[nex];
            double xsjp = X[(nex * NJ + jj) * 2 + (parlev[nex] == -1 ? 0 : 1)];
            int64_t b0 = boff[nex], b1 = boff[nex + 1];
            for (int64_t b = b0; b < b1; b++) {
                int64_t k = bk[b];
                double intens = xsjp * br[b];
                X[(k * NJ + (int64_t)jdis[k]) * 2 + (parlev[k] == -1 ? 0 : 1)] += intens;
                XE[k] += intens;
                XE[nex] -= intens;
            }
            if (b1 > b0 && rec) {
                /* the dict `contrib`: first-occurrence order, last intensity */
                dbl[1] = 1.0;
                for (int64_t b = b0; b < b1; b++) {
                    int64_t k = bk[b], seen = 0;
                    for (int64_t b2 = b0; b2 < b; b2++) if (bk[b2] == k) seen = 1;
                    if (seen) continue;
                    int64_t last = b;
                    for (int64_t b2 = b + 1; b2 < b1; b2++) if (bk[b2] == k) last = b2;
                    double v = xsjp * br[last];
                    fe_set(val, pres, xrows, nex, k, v);
                    gamdis += v;
                }
            }
        }
    }
    return gamdis;
}

/* the (m, 7) `nexmax_rows` of mother spec s for `bins` */
static void nexmax_rows(const Ctx *c, int64_t s, int64_t m, const int64_t *bins, int64_t *out,
                        const int64_t *dspec)
{
    const int64_t *I = SPI(c, s);
    const double *D = SPD(c, s);
    const uint64_t *P = SPP(c, s);
    const double *ex = (const double *)P[0], *dex = (const double *)P[1];
    const double *egrid = (const double *)c->pp[3];
    const int64_t *ebeg = (const int64_t *)c->pp[5];
    (void)I;
    for (int64_t b = 0; b < m; b++) out[b * 7] = bins[b] - 1;
    for (int t = 1; t < 7; t++) {
        const int64_t *dI = SPI(c, dspec[t]);
        const uint64_t *dP = SPP(c, dspec[t]);
        const double *dx = (const double *)dP[0], *ddx = (const double *)dP[1];
        int64_t nb = dI[4] + 1;
        for (int64_t b = 0; b < m; b++) {
            double exm = ex[bins[b]] + 0.5 * dex[bins[b]] - D[2 + t];
            if (t > 1) exm = exm - egrid[ebeg[t - 1]];
            int64_t last = -1;
            for (int64_t k = nb - 1; k >= 0; k--)
                if (dx[k] - 0.5 * ddx[k] < exm) { last = k; break; }
            out[b * 7 + t] = last;
        }
    }
}

typedef struct {
    double *buf[11];
} Bufs;

/* NativeWidths + fast_widths' fission + _Walk + decay_nucleus for one nucleus with bins from
 * `first` down; returns gamdis, or NAN on a kernel refusal */
static double walk_nucleus(Ctx *c, int64_t s, int64_t zc, int64_t nc, int64_t first, double smin,
                           double popepsA, fis_fn fis_cb)
{
    int64_t *I = SPI(c, s);
    double *Dd = SPD(c, s);
    const uint64_t *P = SPP(c, s);
    const uint64_t *O = SPO(c, s);
    const int64_t *ip = c->ip;
    const double *dp = c->dp;
    int64_t maxex = I[4], nlast_grid = I[6], xrows = maxex + 1;
    const double *ex = (const double *)P[0], *dex = (const double *)P[1];
    const int64_t *maxj_all = (const int64_t *)P[2];
    double result = NAN;

    /* bins: first..1, less the discrete levels under S_n */
    int64_t *bins = malloc((size_t)(first + 1) * sizeof(int64_t));
    int64_t m = 0;
    for (int64_t b = first; b >= 1; b--)
        if (!(b <= nlast_grid && ex[b] <= smin)) bins[m++] = b;
    int64_t dspec[7];
    for (int t = 0; t < 7; t++) {
        dspec[t] = need_spec(c, zc + PARZ[t], nc + PARN[t]);
        if (dspec[t] < 0) {
            free(bins);
            return NAN;
        }
    }
    double *exinc = malloc((size_t)m * sizeof(double)), *dexinc = malloc((size_t)m * sizeof(double));
    int64_t *mj = malloc((size_t)m * sizeof(int64_t));
    int64_t *nxm = malloc((size_t)(m * 7) * sizeof(int64_t));
    int64_t nj = 0;
    for (int64_t b = 0; b < m; b++) {
        exinc[b] = ex[bins[b]];
        dexinc[b] = dex[bins[b]];
        mj[b] = maxj_all[bins[b]];
        if (mj[b] + 1 > nj) nj = mj[b] + 1;
    }
    nexmax_rows(c, s, m, bins, nxm, dspec);
    int64_t ns[7];
    for (int t = 0; t < 7; t++) {
        int64_t mx = 0;
        for (int64_t b = 0; b < m; b++) {
            int64_t v = nxm[b * 7 + t] > 0 ? nxm[b * 7 + t] : 0;
            if (v > mx) mx = v;
        }
        ns[t] = mx + 1;
    }
    for (int t = 0; t < 7; t++)
        if (dspec[t] < 0 || SPI(c, dspec[t])[8] < ns[t]) goto done0; /* rhogrid shape */
    const double *fnorm = Dd + 9; /* index type + 1 */
    /* photon rows */
    int64_t L0 = ip[9], Ltl = ip[6];
    double *tg = calloc((size_t)(m * ns[0] * L0 * 2), sizeof(double));
    {
        const int64_t *d0I = SPI(c, dspec[0]);
        const double *ex0 = (const double *)SPP(c, dspec[0])[0];
        (void)d0I;
        int64_t n = ns[0], any = 0;
        int64_t *nx0 = malloc((size_t)m * sizeof(int64_t));
        for (int64_t b = 0; b < m; b++) {
            nx0[b] = nxm[b * 7] > 0 ? nxm[b * 7] : 0;
            for (int64_t k = 0; k < n && !any; k++)
                if (exinc[b] - ex0[k] > 0.0 && k <= nx0[b]) any = 1;
        }
        if (any) {
            uint64_t pack[7];
            if (!c->pp[15] || ((psf_fn)c->pp[15])(s, pack) != 0) { free(nx0); goto done; }
            k_photon((const int64_t *)pack[0], (const double *)pack[1], (const double *)pack[2],
                     (const double *)pack[3], (const double *)pack[4], (const double *)pack[5],
                     (const double *)pack[6], m, exinc, n, ex0, nx0, Dd[2 + 1],
                     dp[2] * fnorm[1], tg);
        }
        free(nx0);
    }
    {
        int64_t wip[16 + 8 * 7] = {0};
        uint64_t wpp[20 + 8 * 7] = {0};
        double wdp[8] = {0};
        uint64_t outp[12 * 7] = {0};
        int64_t meta[8 * 7] = {0};
        double sepv[7], fnv[6];
        for (int t = 0; t < 7; t++) sepv[t] = Dd[2 + t];
        for (int t = 1; t < 7; t++) fnv[t - 1] = fnorm[t + 1];
        wpp[0] = (uint64_t)exinc;
        wpp[1] = (uint64_t)dexinc;
        wpp[2] = (uint64_t)nxm;
        wpp[3] = (uint64_t)sepv;
        wpp[4] = c->pp[0];
        wpp[5] = c->pp[1];
        wpp[6] = c->pp[2];
        wpp[7] = c->pp[3];
        wpp[8] = c->pp[4];
        wpp[9] = c->pp[5];
        wpp[10] = c->pp[6];
        wpp[11] = (uint64_t)fnv;
        wpp[12] = (uint64_t)tg;
        wip[0] = m; wip[1] = nj; wip[2] = I[3] % 2; wip[3] = ip[3]; wip[4] = ip[4]; wip[5] = ip[5];
        wip[6] = Ltl; wip[7] = ip[7]; wip[8] = ip[8]; wip[9] = L0;
        wdp[0] = dp[0];
        Bufs bufs[7];
        int64_t *ird[7], *pdv[7], *nrows[7], *lb[7], *le[7];
        int64_t *jd2[7], *jdi[7];
        for (int t = 0; t < 7; t++) {
            const int64_t *dI = SPI(c, dspec[t]);
            const double *dD = SPD(c, dspec[t]);
            const uint64_t *dP = SPP(c, dspec[t]);
            int64_t n = ns[t], nl = dI[5];
            int64_t ndd = (nl < n - 1 ? nl : n - 1) + 1;
            if (ndd < 0) ndd = 0;
            const double *jd = (const double *)dP[4];
            jd2[t] = malloc((size_t)(ndd > 0 ? ndd : 1) * sizeof(int64_t));
            jdi[t] = malloc((size_t)(ndd > 0 ? ndd : 1) * sizeof(int64_t));
            for (int64_t k = 0; k < ndd; k++) {
                jd2[t][k] = (int64_t)(2.0f * (float)jd[k]);
                jdi[t][k] = (int64_t)jd[k];
            }
            int64_t *q = wip + 16 + 8 * t;
            q[0] = n; q[1] = nl; q[2] = dI[7]; q[3] = dI[8]; q[4] = ndd; q[5] = PARSPIN2[t];
            uint64_t *pq = wpp + 20 + 8 * t;
            pq[0] = dP[0]; pq[1] = dP[1]; pq[2] = dP[2]; pq[3] = (uint64_t)jd2[t];
            pq[4] = (uint64_t)jdi[t]; pq[5] = dP[3]; pq[6] = dP[6];
            wdp[1 + t] = dD[1];
            int64_t Lb = t == 0 ? L0 : Ltl, n1 = ndd > 1 ? ndd : 1;
            bufs[t].buf[0] = malloc((size_t)(m * n * NJ * 2) * sizeof(double));
            bufs[t].buf[1] = malloc((size_t)(m * 2 * n * Lb) * sizeof(double));
            bufs[t].buf[2] = malloc((size_t)(m * nj * n1) * sizeof(double));
            bufs[t].buf[3] = malloc((size_t)(m * nj * n1) * sizeof(double));
            bufs[t].buf[4] = malloc((size_t)(m * n1) * sizeof(double));
            bufs[t].buf[7] = malloc((size_t)(m * nj * 2) * sizeof(double));
            ird[t] = malloc((size_t)n1 * sizeof(int64_t));
            pdv[t] = malloc((size_t)n1 * sizeof(int64_t));
            nrows[t] = malloc((size_t)m * sizeof(int64_t));
            lb[t] = malloc((size_t)(nj * NJ) * sizeof(int64_t));
            le[t] = malloc((size_t)(nj * NJ) * sizeof(int64_t));
            uint64_t *o = outp + 12 * t;
            o[0] = (uint64_t)bufs[t].buf[0]; o[1] = (uint64_t)bufs[t].buf[1];
            o[2] = (uint64_t)bufs[t].buf[2]; o[3] = (uint64_t)bufs[t].buf[3];
            o[4] = (uint64_t)bufs[t].buf[4]; o[5] = (uint64_t)ird[t]; o[6] = (uint64_t)pdv[t];
            o[7] = (uint64_t)bufs[t].buf[7]; o[8] = (uint64_t)nrows[t]; o[9] = (uint64_t)lb[t];
            o[10] = (uint64_t)le[t];
        }
        k_widths(wip, wpp, wdp, outp, meta);
        /* dsum6, zero6 */
        double *dsum6 = calloc((size_t)(m * nj * 2), sizeof(double));
        uint8_t *zero6 = malloc((size_t)(m * nj * 2));
        memset(zero6, 1, (size_t)(m * nj * 2));
        for (int t = 0; t < 6; t++) {
            if (meta[8 * t]) continue;
            const double *D = bufs[t].buf[7];
            for (int64_t x = 0; x < m * nj * 2; x++) {
                dsum6[x] = dsum6[x] + D[x];
                zero6[x] = zero6[x] & (D[x] == 0.0);
            }
        }
        double *fis = NULL;
        uint64_t fptr = 0;
        int64_t fnj = 0;
        int frc = fis_cb ? fis_cb(s, m, bins, &fptr, &fnj) : 2;
        if (frc == 1) goto freebufs;
        if (frc == 0) {
            const double *F = (const double *)fptr;
            fis = calloc((size_t)(m * nj * 2), sizeof(double));
            int64_t kj = fnj < nj ? fnj : nj;
            for (int64_t b = 0; b < m; b++)
                for (int64_t j = 0; j < kj; j++)
                    for (int x = 0; x < 2; x++) fis[(b * nj + j) * 2 + x] = F[(b * fnj + j) * 2 + x];
            for (int64_t x = 0; x < m * nj * 2; x++) {
                dsum6[x] = dsum6[x] + fis[x];
                zero6[x] = zero6[x] & (fis[x] == 0.0);
            }
        }
        {
            /* _Walk */
            int64_t aip[16 + 16 * 7] = {0};
            uint64_t app[160] = {0};
            double dpar[10] = {0};
            int64_t *lvl = malloc((size_t)xrows * sizeof(int64_t));
            int64_t *jint = malloc((size_t)xrows * sizeof(int64_t));
            int64_t *rowmap = malloc((size_t)xrows * sizeof(int64_t));
            const int64_t *parlev = (const int64_t *)P[3];
            const double *jdis = (const double *)P[4];
            for (int64_t k = 0; k < xrows; k++) {
                lvl[k] = parlev[k] == -1 ? 0 : 1;
                jint[k] = (int64_t)jdis[k];
                rowmap[k] = -1;
            }
            for (int64_t b = 0; b < m; b++) rowmap[bins[b]] = b;
            int64_t n0 = ns[0];
            int64_t *l0jd = malloc((size_t)n0 * sizeof(int64_t)), *l0pi = malloc((size_t)n0 * sizeof(int64_t));
            {
                const double *jd0 = (const double *)SPP(c, dspec[0])[4];
                const int64_t *pl0 = (const int64_t *)SPP(c, dspec[0])[3];
                for (int64_t k = 0; k < n0; k++) {
                    l0jd[k] = (int64_t)(2.0f * (float)jd0[k]);
                    l0pi[k] = pl0[k] == -1 ? 0 : 1;
                }
            }
            app[0] = P[0]; app[1] = P[5]; app[2] = (uint64_t)jint; app[3] = (uint64_t)lvl;
            app[4] = P[7]; app[5] = P[8]; app[6] = P[9]; app[7] = (uint64_t)rowmap;
            app[8] = (uint64_t)mj; app[9] = (uint64_t)dsum6; app[10] = (uint64_t)zero6;
            int has_d6 = !meta[8 * 6];
            if (has_d6) app[11] = (uint64_t)bufs[6].buf[7];
            if (fis) app[12] = (uint64_t)fis;
            app[13] = (uint64_t)l0jd; app[14] = (uint64_t)l0pi;
            app[15] = P[10]; app[16] = P[11]; app[17] = P[1];
            aip[0] = xrows; aip[1] = maxex; aip[2] = nlast_grid; aip[3] = m; aip[4] = nj;
            aip[5] = has_d6; aip[6] = fis != NULL;
            int64_t vmax = 1, dpmax = 1, nmax = 1;
            const uint64_t *fev = (const uint64_t *)O[5], *fep = (const uint64_t *)O[6];
            double *created = (double *)O[7];
            for (int t = 0; t < 7; t++) {
                int64_t ds = dspec[t];
                if (ds < 0 || !SPI(c, ds)[9]) continue; /* not in the nucleus set */
                int64_t *st = aip + 16 + 16 * t;
                uint64_t *q = app + 20 + 16 * t;
                int64_t drows = SPI(c, ds)[4] + 1;
                int rec = records(zc, nc, t);
                int closed = (int)meta[8 * t];
                st[0] = 1; st[1] = drows; st[2] = rec; st[3] = closed;
                if (t > 0) {
                    q[0] = SPP(c, ds)[10];
                    q[1] = SPP(c, ds)[11];
                }
                dpar[3 + t] = t == 0 ? 1.0 : (double)(PARSPIN2[t] + 1);
                q[6] = (uint64_t)nrows[t];
                if (rec) {
                    q[12] = fev[t];
                    q[13] = fep[t];
                    st[10] = maxex + 2;
                    st[11] = drows;
                }
                if (closed) continue;
                int64_t n = ns[t], jx = meta[8 * t + 1], Lc = meta[8 * t + 2], nd = meta[8 * t + 3];
                st[4] = n; st[5] = jx; st[6] = 2; st[7] = Lc; st[8] = t >= 1 ? 1 : 2; st[9] = nd;
                q[2] = (uint64_t)bufs[t].buf[0];
                q[3] = (uint64_t)bufs[t].buf[1];
                q[4] = (uint64_t)lb[t];
                q[5] = (uint64_t)le[t];
                if (nd) {
                    q[7] = (uint64_t)bufs[t].buf[2];
                    q[8] = (uint64_t)bufs[t].buf[3];
                    q[9] = (uint64_t)bufs[t].buf[4];
                    q[10] = (uint64_t)ird[t];
                    q[11] = (uint64_t)pdv[t];
                }
                if (jx * 2 * Lc > vmax) vmax = jx * 2 * Lc;
                if (n * jx * 2 > dpmax) dpmax = n * jx * 2;
                if (n > nmax) nmax = n;
            }
            if (xrows > nmax) nmax = xrows;
            if (xrows * NJ * 2 > dpmax) dpmax = xrows * NJ * 2;
            double *part = calloc((size_t)(7 * xrows), sizeof(double));
            uint8_t *partf = calloc((size_t)(7 * xrows), 1);
            double xspopnuc[7] = {0};
            uint8_t cr[7] = {0};
            app[136] = O[0]; app[137] = (uint64_t)part; app[138] = (uint64_t)partf;
            app[139] = O[1]; app[140] = O[2]; app[141] = O[3]; app[142] = O[4];
            app[143] = (uint64_t)xspopnuc; app[144] = (uint64_t)cr;
            double *V = malloc((size_t)vmax * sizeof(double));
            double *dpw = malloc((size_t)dpmax * sizeof(double));
            double *mcw = malloc((size_t)nmax * sizeof(double));
            double *feed = malloc((size_t)(nj * 2) * sizeof(double));
            double *feed6 = malloc((size_t)(nj * 2) * sizeof(double));
            uint8_t *dead = malloc((size_t)(nj * 2));
            uint64_t work[6] = {(uint64_t)V, (uint64_t)dpw, (uint64_t)mcw, (uint64_t)feed,
                                (uint64_t)feed6, (uint64_t)dead};
            app[145] = (uint64_t)work;
            dpar[0] = smin;
            dpar[1] = popepsA;
            for (int t = 0; t < 7; t++) {
                int64_t ds = dspec[t];
                if (ds >= 0 && SPI(c, ds)[9]) xspopnuc[t] = SPD(c, ds)[17];
            }
            /* multiple_native.decay_nucleus: attach_mpe */
            int64_t P1 = ip[11], P4 = P1 * P1 * P1 * P1;
            double *mother = NULL, *acc[2] = {NULL, NULL};
            uint8_t *mflags = NULL, *accf[2] = {NULL, NULL}, mul[2] = {0, 0};
            int64_t drow2[2] = {0, 0};
            int rc = 0, attached = 0;
            if (P4 > 0 && I[13] && !(zc == 0 && nc == 0)) {
                const double *ph = (const double *)P[12];
                const uint8_t *phf = (const uint8_t *)P[13];
                int any = 0;
                for (int64_t k = 1; k <= maxex; k++) any |= phf[k];
                if (any) {
                    mother = calloc((size_t)(xrows * P4), sizeof(double));
                    mflags = calloc((size_t)xrows, 1);
                    for (int64_t k = 1; k <= maxex; k++)
                        if (phf[k]) {
                            memcpy(mother + k * P4, ph + k * P4, (size_t)P4 * sizeof(double));
                            mflags[k] = 1;
                        }
                    for (int di = 0; di < 2; di++) {
                        int64_t ds = dspec[di + 1];
                        if (!SPI(c, ds)[9]) continue;
                        drow2[di] = SPI(c, ds)[4] + 1;
                        acc[di] = calloc((size_t)(drow2[di] * P4), sizeof(double));
                        accf[di] = calloc((size_t)drow2[di], 1);
                    }
                    uint64_t arrs[8] = {(uint64_t)mother, (uint64_t)mflags, (uint64_t)acc[0],
                                        (uint64_t)acc[1], (uint64_t)accf[0], (uint64_t)accf[1],
                                        (uint64_t)mul, 0};
                    uint64_t block = 0;
                    if (!c->pp[16] || ((mpe_fn)c->pp[16])(s, arrs, &block) != 0) rc = -9;
                    else { app[146] = block; attached = 1; }
                }
            }
            if (rc == 0 && maxex >= 1) rc = k_walk(aip, app, dpar, maxex, 1, 0, 0.0);
            if (rc == 0 && attached) {
                /* detach_mpe: the daughters' particle-hole additions and mulpre */
                for (int di = 0; di < 2; di++) {
                    int64_t ds = dspec[di + 1];
                    if (!acc[di]) continue;
                    double *dph = (double *)SPP(c, ds)[12];
                    uint8_t *dphf = (uint8_t *)SPP(c, ds)[13];
                    for (int64_t j = 0; j < drow2[di]; j++) {
                        if (!accf[di][j]) continue;
                        double *row = dph + j * P4;
                        const double *a = acc[di] + j * P4;
                        if (!dphf[j]) {
                            for (int64_t x = 0; x < P4; x++) row[x] = 0.0;
                            dphf[j] = 1;
                        }
                        for (int64_t x = 0; x < P4; x++) row[x] += a[x];
                    }
                    if (mul[di]) SPI(c, ds)[13] = 1;
                }
            }
            free(mother); free(mflags); free(acc[0]); free(acc[1]); free(accf[0]); free(accf[1]);
            if (rc == 0) {
                for (int t = 0; t < 7; t++) {
                    int64_t ds = dspec[t];
                    if (ds >= 0 && SPI(c, ds)[9]) SPD(c, ds)[17] = xspopnuc[t];
                    if (cr[t]) created[1 + t] = 1.0;
                }
                result = dpar[2];
            }
            free(V); free(dpw); free(mcw); free(feed); free(feed6); free(dead);
            free(part); free(partf); free(lvl); free(jint); free(rowmap); free(l0jd); free(l0pi);
        }
        free(fis);
    freebufs:
        free(dsum6); free(zero6);
        for (int t = 0; t < 7; t++) {
            free(bufs[t].buf[0]); free(bufs[t].buf[1]); free(bufs[t].buf[2]); free(bufs[t].buf[3]);
            free(bufs[t].buf[4]); free(bufs[t].buf[7]); free(ird[t]); free(pdv[t]); free(nrows[t]);
            free(lb[t]); free(le[t]); free(jd2[t]); free(jdi[t]);
        }
    }
done:
    free(tg);
done0:
    free(bins); free(exinc); free(dexinc); free(mj); free(nxm);
    return result;
}

/* multiple_emission without multiple pre-equilibrium. Returns 0, or 1 + s for the spec a kernel
 * refused (nothing after it is valid; the caller reruns the energy on the Python path). */
int64_t ce_cascade(const int64_t *ip, const double *dp, const uint64_t *pp)
{
    Ctx c = {ip, dp, pp, (const int64_t *)pp[7], (int64_t *)pp[8], (double *)pp[9],
             (const uint64_t *)pp[10], (const uint64_t *)pp[12]};
    fis_fn fis_cb = (fis_fn)pp[13];
    int64_t maxz = ip[0], maxn = ip[1];
    double popeps = dp[1];
    for (int64_t zc = 0; zc <= maxz; zc++) {
        for (int64_t nc = 0; nc <= maxn; nc++) {
            int64_t s = spec_of(&c, zc, nc);
            if (s < 0 || !SPI(&c, s)[9]) continue;
            int64_t *I = SPI(&c, s);
            double *D = SPD(&c, s);
            const uint64_t *P = SPP(&c, s);
            double *dbl = (double *)SPO(&c, s)[7];
            if (D[17] < popeps) {
                D[17] = 0.0;
                I[12] = 1;
                dbl[0] = 0.0;
                continue;
            }
            int64_t maxex = I[4], nlast = I[6];
            double popepsA = popeps / (double)(5 * maxex > 1 ? 5 * maxex : 1);
            double smin = D[2 + 1];
            const double *ex = (const double *)P[0], *tau = (const double *)P[5];
            double *XE = (double *)P[11];
            int64_t first = -1;
            for (int64_t nex = maxex; nex >= 1; nex--) {
                if (nex <= nlast && ex[nex] <= smin) continue;
                if (XE[nex] >= popepsA) { first = nex; break; }
            }
            double gamdis;
            if (first < 0) {
                gamdis = cascade_only(&c, s, zc, nc, smin);
                I[12] = 3;
            } else {
                gamdis = walk_nucleus(&c, s, zc, nc, first, smin, popepsA, fis_cb);
                if (isnan(gamdis)) return 1 + s;
                I[12] = 2;
            }
            double pop = XE[0];
            for (int64_t nex = 1; nex <= nlast; nex++)
                if (tau[nex] != 0.0) pop += XE[nex];
            D[17] = pop;
            dbl[0] = gamdis;
        }
    }
    return 0;
}


/* ==== CENGBOOK: channels.f90 / totalxs.f90 / residual.f90 off `ce_cascade`'s arena ============
 *
 * `emission.emit_nx2.exclusive_channels` (with `engine._BuiltInputs.channels`'s records and
 * `multiple._binary_feed`'s binary row) for what `engine_c.run` reads of it: the live channel codes
 * and their `xschannel`, `residual_mb` per cascade index, `xsfistot` and `xsresprod`. The matrix
 * products and the triangular solves go through the very BLAS/LAPACK functions numpy's `@` and
 * scipy's `dtrtrs` call (pointers from scipy's cython_blas / cython_lapack, `ce_set_blas`), in
 * numpy's own shape special cases, so the channels are the Python body's to the bit.
 *
 *   ip: 0 maxz, 1 maxn, 2 zinit, 3 ninit, 4 maxchannel, 5 k0, 6 flagfission, 7 index width W,
 *       8 NUMCHANTOT, 9 idnumfull (in/out), 10 opennum (in/out), 11..17 parskip(0..6),
 *       18..23 parinclude(types 1..6), 24 exmax0 columns
 *   dp: 0 xseps, 1 targetE, 2 S(0, 0, k0), 3 Etotal (Exmax0(0, 0)), 4 xsbinary(-1) (fission of the
 *       primary compound nucleus, 0 without), 5 1.0 if `xsbinary` exists
 *   pp: 0 idx, 1 spec ints, 2 spec doubles, 3 spec pointers, 4 outputs (as `ce_cascade`),
 *       5 Exmax0 (float32, rows of `ip[24]`), 6 chanopen (uint8, CH_KEYS), 7 binary feed rows
 *       (7 double pointers, 0 absent), 8 their lengths (7), 9 out codes (NUMCHANTOT + 1),
 *       10 out xschannel, 11 out residual population ((maxz + 1) (maxn + 1)), 12 out ints: 0 live
 *       channels, 13 out doubles: 0 xsfistot, 1 xsresprod
 *   spec ints (this job): 10 length of ex_mev
 */
#define NUMLEV2 300
#define CH_KEYS (9 * 5 * 3 * 2 * 2 * 4)
static const int64_t CAPS[6] = {8, 4, 2, 1, 1, 3};

typedef void (*gemv_fn)(const char *, const int *, const int *, const double *, const double *,
                        const int *, const double *, const int *, const double *, double *,
                        const int *);
typedef double (*ddot_fn)(const int *, const double *, const int *, const double *, const int *);
typedef void (*trtrs_fn)(const char *, const char *, const char *, const int *, const int *,
                         const double *, const int *, double *, const int *, int *);
static gemv_fn b_gemv;
static ddot_fn b_ddot;
static trtrs_fn b_trtrs;

void ce_set_blas(void *gemv, void *ddot, void *trtrs)
{
    b_gemv = (gemv_fn)gemv;
    b_ddot = (ddot_fn)ddot;
    b_trtrs = (trtrs_fn)trtrs;
}

/* numpy `x @ R` for x (k,), R (k, n) C-ordered, into out (n,) */
static void np_vec_mat(int64_t k, int64_t n, const double *x, const double *R, double *out)
{
    int ik = (int)k, in = (int)n, one = 1;
    if (n == 1) {
        out[0] = b_ddot(&ik, x, &one, R, &one);
    } else if (k == 1) {
        for (int64_t j = 0; j < n; j++) out[j] = 0.0 + x[0] * R[j];
    } else {
        double a = 1.0, b = 0.0;
        b_gemv("N", &in, &ik, &a, R, &in, x, &one, &b, out, &one);
    }
}

/* numpy `U @ x` for U (n, n) C-ordered */
static void np_mat_vec(int64_t n, const double *U, const double *x, double *out)
{
    int in = (int)n, one = 1;
    if (n == 1) {
        out[0] = b_ddot(&in, U, &one, x, &one);
    } else {
        double a = 1.0, b = 0.0;
        b_gemv("T", &in, &in, &a, U, &in, x, &one, &b, out, &one);
    }
}

typedef struct {
    int done;
    double *top, *ratio;
    int64_t mx;
} Src;

static int64_t key_index(int64_t in, int64_t ip, int64_t id, int64_t it, int64_t ih, int64_t ia)
{
    return ((((in * 5 + ip) * 3 + id) * 2 + it) * 2 + ih) * 4 + ia;
}

int64_t ce_channels(int64_t *ip, const double *dp, const uint64_t *pp)
{
    int64_t maxz = ip[0], maxn = ip[1], k0 = ip[5], flagfission = ip[6], W = ip[7];
    int64_t numchantot = ip[8], idnumfull = ip[9], opennum = ip[10], e0cols = ip[24];
    const int64_t *idx = (const int64_t *)pp[0];
    Ctx cc = {ip, dp, pp, idx, (int64_t *)pp[1], (double *)pp[2], (const uint64_t *)pp[3],
              (const uint64_t *)pp[4]};
    Ctx *c = &cc;
    const float *exmax0 = (const float *)pp[5];
    uint8_t *chanopen = (uint8_t *)pp[6];
    const uint64_t *fbp = (const uint64_t *)pp[7];
    const int64_t *fbn = (const int64_t *)pp[8];
    int64_t *ocode = (int64_t *)pp[9];
    double *oxs = (double *)pp[10], *ores = (double *)pp[11];
    int64_t *oint = (int64_t *)pp[12];
    double *odbl = (double *)pp[13];
    double xseps = dp[0];
    int64_t NZ = maxz + 1, NN = maxn + 1;
    if (!b_gemv || !b_ddot || !b_trtrs) return -1;

    int64_t nch = numchantot + 1;
    double **xsexcl = calloc((size_t)nch, sizeof(double *));
    double **gamexcl = calloc((size_t)nch, sizeof(double *));
    int64_t *idchannel = calloc((size_t)nch, sizeof(int64_t));
    double *xschannel = calloc((size_t)nch, sizeof(double));
    double *qx = calloc((size_t)nch, sizeof(double));
    int64_t *slot = malloc(CH_KEYS * sizeof(int64_t));
    Src *srcc = calloc((size_t)(NZ * NN * 7), sizeof(Src));
    double *tmp = NULL;
    int64_t tmpn = 0;
    int64_t rc = 0;
    for (int64_t q = 0; q < CH_KEYS; q++) slot[q] = -1;

#define REC_S(zc, nc) ((zc) >= 0 && (nc) >= 0 && (zc) <= maxz && (nc) <= maxn ? idx[(zc) * W + (nc)] : -1)
    int64_t s00 = REC_S(0, 0);
    if (s00 < 0) { rc = -2; goto out; }
    double q00 = SPD(c, s00)[2 + k0] + dp[1];
    int64_t zend = maxz < ip[2] ? maxz : ip[2], nend = maxn < ip[3] ? maxn : ip[3];
    if (zend > NUMZCHAN) zend = NUMZCHAN;
    if (nend > NUMNCHAN) nend = NUMNCHAN;
    int64_t idnum = -1;
    int64_t live_t[7], nlive = 0;
    for (int t = 0; t < 7; t++) if (!ip[11 + t]) live_t[nlive++] = t;

    for (int64_t zix = 0; zix <= zend; zix++) {
        for (int64_t nix = 0; nix <= nend; nix++) {
            /* _limits / _channel_keys */
            int64_t aix = zix + nix, lim[6] = {0, 0, 0, 0, 0, 0}, mc = ip[4];
            if (aix != 0) {
                int64_t cand[6] = {nix, zix, 2 * zix * nix / aix, 3 * zix * nix / (2 * aix),
                                   3 * zix * nix / (2 * aix), zix * nix / aix};
                for (int i = 0; i < 6; i++) {
                    int64_t v = cand[i] < mc ? cand[i] : mc;
                    if (ip[18 + i]) lim[i] = v;
                }
            }
            for (int i = 0; i < 6; i++) if (lim[i] > CAPS[i]) lim[i] = CAPS[i];
            int64_t s = REC_S(zix, nix);
            int64_t maxex = 0, nlast = 0;
            const double *ex = NULL, *tau = NULL;
            if (s >= 0) {
                maxex = SPI(c, s)[4]; nlast = SPI(c, s)[5];
                ex = (const double *)SPP(c, s)[0]; tau = (const double *)SPP(c, s)[5];
            }
            int64_t nr = maxex + 1;
            int64_t top_iso = maxex < nlast ? maxex : nlast;
            int64_t kk = 0; /* levels with a record: 0..kk-1 */
            if (s >= 0) {
                int64_t m1 = nlast < NUMLEV2 ? nlast : NUMLEV2;
                if (SPI(c, s)[10] - 1 < m1) m1 = SPI(c, s)[10] - 1;
                kk = m1 + 1;
            }
            int64_t *iso = malloc((size_t)(top_iso + 1) * sizeof(int64_t)), niso = 0;
            for (int64_t k = top_iso; k >= 1; k--)
                if (k < kk && tau[k] != 0.0) iso[niso++] = k;
            iso[niso++] = 0;
            int has_edis0 = kk > 0;
            double edis0 = has_edis0 ? ex[0] : 0.0;
            /* sources */
            int64_t st_there[7];
            double st_sep[7];
            for (int64_t li = 0; li < nlive; li++) {
                int t = (int)live_t[li];
                int64_t zc = zix - PARZ[t], nc = nix - PARN[t];
                int there = zc >= 0 && nc >= 0 && zc <= maxz && nc <= maxn;
                int64_t ms = there ? REC_S(zc, nc) : -1;
                st_there[li] = there;
                st_sep[li] = ms >= 0 ? SPD(c, ms)[2 + t] : 0.0;
            }
            if (nr > tmpn) { free(tmp); tmp = malloc((size_t)nr * sizeof(double)); tmpn = nr; }

            for (int64_t ih = 0; ih <= lim[4]; ih++)
            for (int64_t it = 0; it <= lim[3]; it++)
            for (int64_t idd_ = 0; idd_ <= lim[2]; idd_++)
            for (int64_t ia = 0; ia <= lim[5]; ia++) {
                int64_t ipn = zix - idd_ - it - 2 * ih - 2 * ia;
                int64_t inn = nix - idd_ - 2 * it - ih - 2 * ia;
                if (!(ipn >= 0 && ipn <= lim[1] && inn >= 0 && inn <= lim[0])) continue;
                int64_t npart = inn + ipn + idd_ + it + ih + ia;
                if (npart > mc) continue;
                int64_t kidx = key_index(inn, ipn, idd_, it, ih, ia);
                if (idnumfull && !chanopen[kidx]) continue;
                if (idnum == numchantot) continue;
                int64_t ident = 100000 * inn + 10000 * ipn + 1000 * idd_ + 100 * it + 10 * ih + ia;
                int64_t cnt[7] = {0, inn, ipn, idd_, it, ih, ia};
                idnum++;
                idchannel[idnum] = ident;
                slot[kidx] = idnum;
                qx[idnum] = 0.0;
                qx[0] = q00;
                double qv = qx[idnum];
                int64_t org_t[7], org_id[7], norg = 0;
                for (int64_t li = 0; li < nlive; li++) {
                    int t = (int)live_t[li];
                    int64_t idorg;
                    if (t == 0) {
                        idorg = idnum;
                    } else {
                        int64_t p10 = 1;
                        for (int e = 0; e < 6 - t; e++) p10 *= 10;
                        if (ident - p10 < 0) continue;
                        if (cnt[t] == 0) continue; /* a borrowed code: never formed */
                        int64_t c2[7];
                        memcpy(c2, cnt, sizeof c2);
                        c2[t]--;
                        idorg = slot[key_index(c2[1], c2[2], c2[3], c2[4], c2[5], c2[6])];
                        if (idorg < 0 || idorg > idnum || idchannel[idorg] != ident - p10) continue;
                    }
                    if (qv == 0.0 && st_there[li]) qv = (idorg == idnum ? qv : qx[idorg]) - st_sep[li];
                    if (has_edis0) qv = qv - edis0;
                    if (st_there[li]) { org_t[norg] = t; org_id[norg++] = idorg; }
                }
                qx[idnum] = qv;

                double *xe = NULL, *ge = NULL;
                const double *ug = NULL;
                for (int64_t o = 0; o < norg; o++) {
                    int t = (int)org_t[o];
                    int64_t zc = zix - PARZ[t], nc = nix - PARN[t];
                    Src *S = srcc + (zc * NN + nc) * 7 + t;
                    if (!S->done) {
                        S->done = 1;
                        int64_t ms = REC_S(zc, nc);
                        int64_t mst = ms >= 0 && SPI(c, ms)[9] ? SPI(c, ms)[12] : 0;
                        int is_root = zc == 0 && nc == 0;
                        if (is_root && fbp[t]) {
                            int64_t n = fbn[t] < nr ? fbn[t] : nr, any = 0;
                            const double *row = (const double *)fbp[t];
                            for (int64_t j = 0; j < n; j++) any |= row[j] != 0.0;
                            if (any) {
                                S->top = calloc((size_t)nr, sizeof(double));
                                memcpy(S->top, row, (size_t)n * sizeof(double));
                            }
                        }
                        int table = mst == 2 || (mst == 3 && t == 0 &&
                                                 ((const double *)SPO(c, ms)[7])[1] != 0.0);
                        if (table && !(is_root && t > 0)) {
                            int64_t mx = SPI(c, ms)[4];
                            const double *val = (const double *)((const uint64_t *)SPO(c, ms)[5])[t];
                            const double *popx = (const double *)SPO(c, ms)[0];
                            if (mx >= 1 && val) {
                                int64_t cols = nr, any = 0;
                                double *ratio = calloc((size_t)(mx * nr), sizeof(double));
                                for (int64_t nex = 1; nex <= mx; nex++) {
                                    double pop = popx[nex];
                                    if (pop == 0.0) continue;
                                    const double *f = val + nex * cols;
                                    for (int64_t j = 0; j < nr; j++)
                                        if (f[j] != 0.0) {
                                            ratio[(nex - 1) * nr + j] = f[j] / pop;
                                            any = 1;
                                        }
                                }
                                if (any) { S->ratio = ratio; S->mx = mx; }
                                else free(ratio);
                            }
                        }
                    }
                    if (S->top) {
                        if (!xe) { xe = calloc((size_t)nr, sizeof(double)); ge = calloc((size_t)nr, sizeof(double)); }
                        for (int64_t j = 0; j < nr; j++) xe[j] = xe[j] + S->top[j];
                        if (t == 0) for (int64_t j = 0; j < nr; j++) ge[j] = ge[j] + S->top[j];
                    }
                    if (!S->ratio) continue;
                    if (t == 0) { ug = S->ratio; continue; }
                    if (!xe) { xe = calloc((size_t)nr, sizeof(double)); ge = calloc((size_t)nr, sizeof(double)); }
                    int64_t id0 = org_id[o];
                    np_vec_mat(S->mx, nr, xsexcl[id0] + 1, S->ratio, tmp);
                    for (int64_t j = 0; j < nr; j++) xe[j] = xe[j] + tmp[j];
                    np_vec_mat(S->mx, nr, gamexcl[id0] + 1, S->ratio, tmp);
                    for (int64_t j = 0; j < nr; j++) ge[j] = ge[j] + tmp[j];
                }
                if (ug) {
                    if (!xe) { xe = calloc((size_t)nr, sizeof(double)); ge = calloc((size_t)nr, sizeof(double)); }
                    /* gamma_system: U[:, 1:k+1] = ug[:k, :nr].T, strict upper; A = I - U */
                    int64_t k = nr - 1 < maxex ? nr - 1 : maxex;
                    double *U = calloc((size_t)(nr * nr), sizeof(double));
                    double *A = malloc((size_t)(nr * nr) * sizeof(double));
                    for (int64_t j = 1; j <= k; j++)
                        for (int64_t i = 0; i < j; i++) U[i * nr + j] = ug[(j - 1) * nr + i];
                    for (int64_t i = 0; i < nr; i++)
                        for (int64_t j = 0; j < nr; j++)
                            A[i * nr + j] = (i == j ? 1.0 : 0.0) - U[i * nr + j];
                    int in = (int)nr, one = 1, info = 0;
                    b_trtrs("L", "T", "U", &in, &one, A, &in, xe, &in, &info);
                    np_mat_vec(nr, U, xe, tmp);
                    for (int64_t j = 0; j < nr; j++) ge[j] = ge[j] + tmp[j];
                    b_trtrs("L", "T", "U", &in, &one, A, &in, ge, &in, &info);
                    free(U); free(A);
                }
                if (!xe) { xe = calloc((size_t)nr, sizeof(double)); ge = calloc((size_t)nr, sizeof(double)); }
                free(xsexcl[idnum]); free(gamexcl[idnum]);
                xsexcl[idnum] = xe; gamexcl[idnum] = ge;
                double xsc = 0.0;
                for (int64_t q = 0; q < niso; q++) xsc += xe[iso[q]];
                if (qv > 0.0 && xsc <= xseps) xsc = xseps;
                xschannel[idnum] = xsc;
                if ((xsc >= xseps && !idnumfull) || npart == 0) {
                    if (!chanopen[kidx]) { chanopen[kidx] = 1; opennum++; }
                }
                if (xsc < xseps && npart > 1 && !chanopen[kidx]) idnum--;
                if (opennum == numchantot - 10) idnumfull = 1;
                if (idnum < 0) continue;
                if (xschannel[idnum] < 0.0) xschannel[idnum] = xseps;
            }
            free(iso);
        }
    }
    oint[0] = idnum + 1;
    for (int64_t i = 0; i <= idnum; i++) { ocode[i] = idchannel[i]; oxs[i] = xschannel[i]; }
    {
        /* totalxs.f90's xsfistot, residual.f90 */
        double fistot = 0.0, resprod = 0.0;
        for (int64_t zc = 0; zc <= maxz; zc++)
            for (int64_t nc = 0; nc <= maxn; nc++) {
                int64_t s = REC_S(zc, nc);
                int inset = s >= 0 && SPI(c, s)[9];
                int64_t status = inset ? SPI(c, s)[12] : 0;
                if (flagfission) {
                    double f = 0.0;
                    int fed = 0;
                    if (status == 2) {
                        const uint8_t *fl = (const uint8_t *)SPO(c, s)[4];
                        for (int q = 0; q < 8; q++) fed |= fl[q];
                        if (fl[0]) f = ((const double *)SPO(c, s)[3])[0];
                    }
                    if (zc == 0 && nc == 0) { f = f + (dp[5] != 0.0 ? dp[4] : 0.0); fed = 1; }
                    if (fed) fistot = fistot + f;
                }
                double pop = inset ? SPD(c, s)[17] : 0.0;
                if (pop != 0.0) resprod += pop;
                double qres = 0.0;
                if (s >= 0) {
                    double e0 = (double)exmax0[zc * e0cols + nc];
                    if (e0 != 0.0) qres = dp[2] + dp[1] + (e0 - dp[3]);
                }
                if (qres > 0.0 && pop <= xseps) pop = xseps;
                ores[zc * NN + nc] = pop;
            }
        odbl[0] = flagfission ? fistot : 0.0;
        odbl[1] = resprod;
    }
    ip[9] = idnumfull;
    ip[10] = opennum;
out:
    for (int64_t i = 0; i < nch; i++) { free(xsexcl[i]); free(gamexcl[i]); }
    if (srcc)
        for (int64_t q = 0; q < NZ * NN * 7; q++) { free(srcc[q].top); free(srcc[q].ratio); }
    free(xsexcl); free(gamexcl); free(idchannel); free(xschannel); free(qx); free(slot);
    free(srcc); free(tmp);
    return rc;
#undef REC_S
}

/* ==== CENGBOOK: the primary densprepare ======================================================
 *
 * `compound.prepare.densprepare(chain.primary_dens_inputs(...))` for the arrays `nx_target` reads
 * (`rho0`, `lmaxhf`, `jdis2`, `Tjlnex` / `Tgam`), with `target._exact_incident_channel` on the
 * incident channel's row: numpy's statements element by element (the primary case: Eout =
 * Exinc - Ex - S, Rboundary = 1, Exout = Ex), the Lagrange interpolation as `nx2_glue_interp`
 * and the photon rows through `nx2_psf_points` itself. Tlnex is not formed: `nx_target` does not
 * read it.
 *
 *   ip: 0 k0, 1 Ltarget, 2 lmaxinc, 3 gammax, 4 rows of Tjlinc, 5 exact incident channel (1/0)
 *   dp: 0 Exinc, 1 transeps, 2 Efs, 3 twopi Fnorm(0)
 *   pp: 0 per type ints (7, 12), 1 per type doubles (7, 4), 2 per type inputs (7, 10),
 *       3 per type outputs (7, 4), 4 PSF pack (7 pointers), 5 Tjlinc (rows, 3)
 *   type ints: 0 nex, 1 Nlast, 2 Ntop, 3 rhogrid rows, 4 ebegin, 5 min(eendmax, maxen), 6 maxen,
 *       7 L of Tjl, 8 egrid length, 9 L out (>= L), 10 Tjl rows, 11 photon points buffer rows
 *   type doubles: 0 discfactor, 1 S(0, 0, type), 2 Fnorm(type)
 *   type inputs: 0 ex, 1 maxJ (int64), 2 parlev (int64), 3 jdis, 4 rhogrid (rows, NJ, 2),
 *       5 egrid, 6 egrid float32, 7 Tjl (rows, L, 3), 8 lmax (int64)
 *   type outputs (zeroed by the caller): 0 rho (nex, NJ, 2), 1 lmaxhf, 2 jdis2, 3 T: photons
 *       (nex, gammax + 1, 2), particles (nex, L out, 3)
 * Returns 0, or 1 + type for a row the numpy body would not take (the caller runs Python). */
typedef int (*points_fn)(const int64_t *, const double *, const double *, const double *,
                         const double *, const double *, const double *, int64_t, const double *,
                         const double *, double, double *);
static points_fn k_points;

void ce_set_front_kernels(void *points) { k_points = (points_fn)points; }

#define DI 12
#define DD 4
#define DP 10
#define DO 4

int64_t ce_densprepare(const int64_t *ip, const double *dp, const uint64_t *pp)
{
    int64_t k0 = ip[0], lt = ip[1], lmaxinc = ip[2], gammax = ip[3], ntjl = ip[4];
    double exinc = dp[0], transeps = dp[1];
    for (int t = 0; t < 7; t++) {
        const int64_t *I = (const int64_t *)pp[0] + t * DI;
        const double *D = (const double *)pp[1] + t * DD;
        const uint64_t *P = (const uint64_t *)pp[2] + t * DP;
        const uint64_t *O = (const uint64_t *)pp[3] + t * DO;
        int64_t nex = I[0], nlast = I[1], ntop = I[2];
        const double *ex = (const double *)P[0], *jdis = (const double *)P[3];
        const int64_t *maxj = (const int64_t *)P[1], *parlev = (const int64_t *)P[2];
        double *rho = (double *)O[0];
        int64_t *lmaxhf = (int64_t *)O[1], *jdis2 = (int64_t *)O[2];
        double *eout = malloc((size_t)(nex > 0 ? nex : 1) * sizeof(double));
        for (int64_t n = 0; n < nex; n++) eout[n] = exinc - ex[n] - D[1];
        /* rho0: continuum rows, then one cell per discrete level */
        if (nlast + 1 < nex && I[3] < nex) { free(eout); return 1 + t; }
        const double *rg = (const double *)P[4];
        for (int64_t n = nlast + 1; n < nex; n++) {
            if (n < 0) continue;
            int64_t mj = maxj[n];
            for (int64_t j = 0; j < NJ && j <= mj; j++)
                for (int p = 0; p < 2; p++) rho[(n * NJ + j) * 2 + p] = 1.0 * rg[(n * NJ + j) * 2 + p];
        }
        int64_t kd = (nlast < nex - 1 ? nlast : nex - 1) + 1;
        for (int64_t k = 0; k < kd; k++)
            if (!isfinite(jdis[k])) { free(eout); return 1 + t; }
        for (int64_t k = 0; k < kd; k++) {
            int64_t ir = (int64_t)jdis[k];
            if (ir < 0 || ir > NJ - 1) continue;
            rho[(k * NJ + ir) * 2 + (parlev[k] == -1 ? 0 : 1)] = k > ntop ? 1.0 * D[0] : 1.0;
        }
        for (int64_t n = 0; n < nex; n++)
            jdis2[n] = n <= nlast ? (int64_t)(2.0f * (float)jdis[n]) : -1;
        if (t == 0) {
            for (int64_t n = 0; n < nex; n++) lmaxhf[n] = gammax;
            int64_t L0 = gammax + 1, m = 0;
            double *T = (double *)O[3];
            int64_t *idx = malloc((size_t)(nex > 0 ? nex : 1) * sizeof(int64_t));
            double *eg = malloc((size_t)(nex > 0 ? nex : 1) * sizeof(double));
            double *efs = malloc((size_t)(nex > 0 ? nex : 1) * sizeof(double));
            for (int64_t n = 0; n < nex; n++) {
                double e = exinc - ex[n];
                if (e > 0.0) { idx[m] = n; eg[m] = e; efs[m] = dp[2]; m++; }
            }
            int rc = 0;
            if (m) {
                const uint64_t *pk = (const uint64_t *)pp[4];
                double *buf = calloc((size_t)(m * L0 * 2), sizeof(double));
                if (!k_points || !pk[0]) rc = 1;
                else {
                    k_points((const int64_t *)pk[0], (const double *)pk[1], (const double *)pk[2],
                             (const double *)pk[3], (const double *)pk[4], (const double *)pk[5],
                             (const double *)pk[6], m, efs, eg, dp[3], buf);
                    for (int64_t q = 0; q < m; q++)
                        for (int64_t l = 1; l < L0; l++)
                            for (int ir = 0; ir < 2; ir++)
                                T[(idx[q] * L0 + l) * 2 + ir] = buf[(q * L0 + l) * 2 + ir];
                }
                free(buf);
            }
            free(idx); free(eg); free(efs);
            if (rc) { free(eout); return 1 + t; }
        } else {
            int64_t ib = I[4], ie = I[5], maxen = I[6], L = I[7], Lo = I[9], rows = I[10];
            const double *egrid = (const double *)P[5];
            const float *xs = (const float *)P[6];
            const double *tjl = (const double *)P[7];
            const int64_t *lmax = (const int64_t *)P[8];
            double *T = (double *)O[3];
            if (ib < ie) {
                for (int64_t q = ib; q < ie; q++)
                    if (!(xs[q + 1] > xs[q])) { free(eout); return 1 + t; }
                double lo = egrid[ib];
                double fn = D[2];
                for (int64_t n = 0; n < nex; n++) {
                    /* _locate_nen */
                    float x = (float)eout[n];
                    int64_t a = 0, b = ie - ib + 1; /* count of xs[ib..ie] <= x */
                    while (a < b) {
                        int64_t mid = (a + b) / 2;
                        if (xs[ib + mid] <= x) a = mid + 1; else b = mid;
                    }
                    int64_t jl = a - 1 + ib;
                    if (x == xs[ib]) jl = ib;
                    else if (x == xs[ie]) jl = ie - 1;
                    int64_t nen = eout[n] < lo ? 0 : jl;
                    int centred = nen > ib + 1 || nen >= maxen - 1;
                    int64_t na = centred ? nen - 1 : nen, nb = na + 1, nc = na + 2;
                    if (na < 0 || nc >= rows || nc >= I[8]) { free(eout); return 1 + t; }
                    int64_t cl = nen < 0 ? 0 : (nen > maxen ? maxen : nen);
                    int64_t lm = lmax[cl];
                    lmaxhf[n] = lm;
                    double e = eout[n], ea = egrid[na], eb = egrid[nb], ec = egrid[nc];
                    double w1 = (e - eb) * (e - ec) / ((ea - eb) * (ea - ec));
                    double w2 = (e - ea) * (e - ec) / ((eb - ea) * (eb - ec));
                    double w3 = (e - ea) * (e - eb) / ((ec - ea) * (ec - eb));
                    const double *ja = tjl + na * L * 3, *jb = tjl + nb * L * 3, *jc = tjl + nc * L * 3;
                    for (int64_t l = 0; l < L; l++) {
                        int keep = l <= lm;
                        for (int64_t k = 0; k < 3; k++) {
                            int64_t q = l * 3 + k;
                            double v = keep ? (w1 * ja[q] + w2 * jb[q]) + w3 * jc[q] : 0.0;
                            T[(n * Lo + l) * 3 + k] = (v < transeps ? 0.0 : v) * fn;
                        }
                    }
                }
            }
            if (t == k0 && ip[5] && lt >= 0 && lt <= nex - 1) {
                int64_t nn = lmaxinc + 1 < ntjl ? lmaxinc + 1 : ntjl;
                const double *inc = (const double *)pp[5];
                for (int64_t l = 0; l < nn && l < Lo; l++)
                    for (int k = 0; k < 3; k++) T[(lt * Lo + l) * 3 + k] = inc[l * 3 + k];
            }
        }
        if (nex - 1 > 0) lmaxhf[nex - 1] = lmaxhf[nex - 2];
        free(eout);
    }
    if (k0 >= 0 && k0 < 7) ((int64_t *)((const uint64_t *)pp[3])[k0 * DO + 1])[0] = lmaxinc;
    return 0;
}
