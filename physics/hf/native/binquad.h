/* BINQUAD (`binquad y`, default n = TALYS): population-weighted in-bin quadrature of the emission
 * transmissions, shared by nativex.c (`nx_widths`, the cascade's mother bins) and engine_decay.c
 * (`ce_densprepare`, the primary decay).
 *
 * TALYS (densprepare.f90) feeds a residual bin [y0, y1] from a mother bin [x0, x1] with
 * T_l(eps_mid) * Rboundary * rhogrid: rhogrid is the level density integrated exactly over the
 * residual bin (exgrid.f90), but the transmission is read at ONE emission energy, the midpoint of the
 * eps = x - S - y range, and Rboundary is a symmetric-triangle overlap. Inside the two bins the
 * population is not uniform: the residual's levels pile up as rho(y) ~ exp(beta y) and the mother's
 * population as rho_m(x) ~ exp(alpha x) (beta, alpha = the local d ln rho / dE of each nucleus's own
 * rhogrid). Here eps is distributed as
 *     g(eps) = int du exp(alpha (u - uc)) exp(beta (u - eps - yc)),  u = x - S in [u0, u1],
 *              y = u - eps in [y0, y1]
 * (a tilted trapezoid with kinks at u1 - y1 and u0 - y0), T_l is averaged over g on the accessible
 * part eps > 0 with Q-point Gauss-Legendre per smooth piece, and Rboundary = mass(eps > 0) / mass.
 * A zero-width bin (a discrete level, the primary's incident point) is the one-dimensional limit.
 * Quadrature only, no physics parameter. */
#ifndef BINQUAD_H
#define BINQUAD_H

#include <math.h>
#include <stdint.h>

#define BQ_QMAX 4
#define BQ_KMAX (5 * BQ_QMAX) /* <= 5 pieces (emin, two kinks, 0, emax) x Q nodes */

static const double BQ_X[BQ_QMAX + 1][BQ_QMAX] = {
    {0, 0, 0, 0},
    {0.0, 0, 0, 0},
    {-0.5773502691896257, 0.5773502691896257, 0, 0},
    {-0.7745966692414834, 0.0, 0.7745966692414834, 0},
    {-0.8611363115940526, -0.3399810435848563, 0.3399810435848563, 0.8611363115940526}};
static const double BQ_W[BQ_QMAX + 1][BQ_QMAX] = {
    {0, 0, 0, 0},
    {2.0, 0, 0, 0},
    {1.0, 1.0, 0, 0},
    {0.5555555555555556, 0.8888888888888888, 0.5555555555555556, 0},
    {0.3478548451374538, 0.6521451548625461, 0.6521451548625461, 0.3478548451374538}};

/* int_a^b exp(c v) dv, stable for c -> 0 */
static inline double bq_expint(double c, double a, double b)
{
    double d = b - a;
    if (d <= 0.0) return 0.0;
    double z = c * d;
    if (fabs(z) < 1e-8) return exp(c * a) * d * (1.0 + 0.5 * z);
    return exp(c * a) * expm1(z) / c;
}

/* g(eps) up to a constant (see the header comment); centred at uc, yc */
static inline double bq_g(double eps, double u0, double u1, double y0, double y1, double alpha,
                          double beta, double uc, double yc, int upt, int ypt)
{
    if (upt && ypt) return 1.0;
    if (upt) { /* mother is a point u0: y = u0 - eps */
        double y = u0 - eps;
        return (y < y0 - 1e-12 || y > y1 + 1e-12) ? 0.0 : exp(beta * (y - yc));
    }
    if (ypt) { /* residual is a point y0: u = eps + y0 */
        double u = eps + y0;
        return (u < u0 - 1e-12 || u > u1 + 1e-12) ? 0.0 : exp(alpha * (u - uc));
    }
    double lo = u0 > y0 + eps ? u0 : y0 + eps, hi = u1 < y1 + eps ? u1 : y1 + eps;
    if (hi <= lo) return 0.0;
    /* exp(alpha (u - uc) + beta (u - eps - yc)) = exp((alpha + beta)(u - uc)) exp(beta (uc - eps - yc)) */
    return exp(beta * (uc - eps - yc)) * bq_expint(alpha + beta, lo - uc, hi - uc);
}

/* Nodes eps_k and weights w_k (sum over accessible nodes, eps > 0) of the tilted eps distribution of a
 * mother range [u0, u1] (= x - S) and residual range [y0, y1]; returns the node count K and sets *rb to
 * mass(eps > 0) / mass. K = 0 and *rb = 0 when nothing is accessible; -1 when both are points (the
 * caller keeps TALYS's numbers). */
static inline int bq_nodes(double u0, double u1, double y0, double y1, double alpha, double beta, int Q,
                           double *eps, double *w, double *rb)
{
    const double tiny = 1e-9;
    int upt = u1 - u0 < tiny, ypt = y1 - y0 < tiny;
    if (upt && ypt) return -1;
    if (Q < 1) Q = 1;
    if (Q > BQ_QMAX) Q = BQ_QMAX;
    double uc = 0.5 * (u0 + u1), yc = 0.5 * (y0 + y1);
    double emin = u0 - y1, emax = u1 - y0;
    double p[5];
    int np = 0;
    p[np++] = emin;
    if (!upt && !ypt) {
        double k1 = u1 - y1, k2 = u0 - y0;
        if (k1 > emin && k1 < emax) p[np++] = k1;
        if (k2 > emin && k2 < emax) p[np++] = k2;
    }
    if (emin < 0.0 && emax > 0.0) p[np++] = 0.0;
    p[np++] = emax;
    for (int i = 1; i < np; i++) /* sort (<= 5) */
        for (int j = i; j > 0 && p[j] < p[j - 1]; j--) { double t = p[j]; p[j] = p[j - 1]; p[j - 1] = t; }
    double mtot = 0.0, macc = 0.0;
    int K = 0;
    for (int i = 0; i + 1 < np; i++) {
        double a = p[i], b = p[i + 1];
        if (b - a <= 1e-14) continue;
        double hm = 0.5 * (b - a), cm = 0.5 * (a + b);
        int acc = a >= 0.0;
        for (int q = 0; q < Q; q++) {
            double e = cm + hm * BQ_X[Q][q];
            double v = hm * BQ_W[Q][q] * bq_g(e, u0, u1, y0, y1, alpha, beta, uc, yc, upt, ypt);
            mtot += v;
            if (acc && v > 0.0) { macc += v; eps[K] = e; w[K] = v; K++; }
        }
    }
    if (!(mtot > 0.0) || !(macc > 0.0)) { *rb = 0.0; return 0; }
    for (int k = 0; k < K; k++) w[k] /= macc;
    *rb = macc / mtot;
    return K;
}

/* d ln(rho) / dE at row r of a grid whose rows nl+1.. carry rhogrid (rows, NJ, 2) integrated over dex:
 * central difference of ln(sum rhogrid / dex) where both neighbours are continuum, else one-sided, else 0 */
static inline double bq_dens(const double *rhog, const double *dex, int64_t r, int64_t nj2)
{
    double s = 0.0;
    for (int64_t k = 0; k < nj2; k++) s += rhog[r * nj2 + k];
    return dex[r] > 0.0 && s > 0.0 ? s / dex[r] : 0.0;
}

static inline double bq_slope(const double *rhog, const double *ex, const double *dex, int64_t nl,
                              int64_t nrows, int64_t r, int64_t nj2)
{
    int64_t a = r - 1 > nl ? r - 1 : (r > nl ? r : -1), b = r + 1 < nrows ? r + 1 : r;
    if (a < 0 || b <= nl || b == a) {
        if (r > nl && r + 1 < nrows) { a = r; b = r + 1; }
        else return 0.0;
    }
    double da = bq_dens(rhog, dex, a, nj2), db = bq_dens(rhog, dex, b, nj2);
    if (!(da > 0.0) || !(db > 0.0) || !(ex[b] > ex[a])) return 0.0;
    return (log(db) - log(da)) / (ex[b] - ex[a]);
}

/* centroid offset of exp(alpha x) on [-w/2, w/2]: w/2 coth(alpha w/2) - 1/alpha (-> alpha w^2/12) */
static inline double bq_centroid(double alpha, double w)
{
    double z = 0.5 * alpha * w;
    if (!(w > 0.0)) return 0.0;
    if (fabs(z) < 1e-4) return alpha * w * w / 12.0;
    return 0.5 * w / tanh(z) - 1.0 / alpha;
}

#endif
