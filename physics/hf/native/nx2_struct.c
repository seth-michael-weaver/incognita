/* NATIVEX2 lever `struct`: one block of a `levels/<table>/<Sym>.lev` file read with levels.f90's
 * formats (physics/hf/structure/levels.py `_level_block` builds the inputs and the result).
 * Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
 * Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
 *
 * nx2_struct_levels -- levels.f90:172-176 and :215 (the `read` statements of levels):
 *   level     '(4x, f11.6, f6.1, 3x, i2, i3, 18x, e10.3, 3a1, a18)'
 *   branch    '(29x, i3, f10.6, e10.3, 5x, a1)'
 *   level2    '(4x, f11.6, f6.1, 3x, i2, i3, 18x, e10.3, 3a1)'
 * for levels 0..nlev2 with their branch records, then levels nlev2+1..nlevmax2 skipping theirs.
 * A record shorter than a format reads blanks (the Python reader's ljust). Only the PLAIN field
 * forms are converted here, and they are the ones `files._make_parser` hands to Python's `float` /
 * `int` unchanged, so the value is the same double:
 *   real: blanks, [+-] digits with exactly one '.' (at least one digit), optional [eE][+-]digits,
 *         blanks -- converted by strtod (correctly rounded, as Python's float); all blank -> 0.0;
 *   int:  blanks, [+-] digits, blanks -- all blank -> 0.
 * Any other form of any field (implied decimals, inner blanks, D exponents, ...), a negative
 * branch count or a record past the block returns a negative code, and the caller reads the whole
 * block with the Python parsers instead.
 * Outputs: lev (nlev2+1, 5) = E, J, P, nb, tau; lchr (nlev2+1, 21) = 3 flags + ENSDF;
 * br (nrec, 3) = klev, ratio, conv; bchr (nrec) = flag; rest (nlevmax2-nlev2, 4) = E, J, P, tau;
 * rchr (nlevmax2-nlev2, 3) = flags. Returns the number of branch records, or < 0. */
#include <stdint.h>
#include <stdlib.h>

enum { NX2S_MAXW = 40 };

/* the blank-padded field [a, b) of record r as a NUL-terminated trimmed string in tmp: start
 * offset returned, *n its length */
static int nx2s_field(const char *buf, const int64_t *ls, const int64_t *le, int64_t r, int a,
                      int b, char *tmp, int *n)
{
    const int64_t s = ls[r], len = le[r] - ls[r];
    int k = 0;
    for (int i = a; i < b; i++)
        tmp[k++] = i < len ? buf[s + i] : ' ';
    int p = 0, q = k;
    while (p < q && tmp[p] == ' ')
        p++;
    while (q > p && tmp[q - 1] == ' ')
        q--;
    tmp[q] = '\0';
    *n = q - p;
    return p;
}

static int nx2s_real(const char *buf, const int64_t *ls, const int64_t *le, int64_t r, int a,
                     int b, double *v)
{
    char tmp[NX2S_MAXW + 1];
    int n;
    const int p = nx2s_field(buf, ls, le, r, a, b, tmp, &n);
    if (n == 0) {
        *v = 0.0;
        return 1;
    }
    const char *t = tmp + p;
    int i = 0, nd = 0, dot = 0;
    if (t[i] == '+' || t[i] == '-')
        i++;
    for (; i < n; i++) {
        if (t[i] >= '0' && t[i] <= '9')
            nd++;
        else if (t[i] == '.' && !dot)
            dot = 1;
        else
            break;
    }
    if (!dot || nd == 0)
        return 0;
    if (i < n) {
        if (t[i] != 'e' && t[i] != 'E')
            return 0;
        i++;
        if (i < n && (t[i] == '+' || t[i] == '-'))
            i++;
        int ne = 0;
        for (; i < n && t[i] >= '0' && t[i] <= '9'; i++)
            ne++;
        if (ne == 0 || i != n)
            return 0;
    }
    char *end;
    *v = strtod(t, &end);
    return end == t + n;
}

static int nx2s_int(const char *buf, const int64_t *ls, const int64_t *le, int64_t r, int a, int b,
                    int64_t *v)
{
    char tmp[NX2S_MAXW + 1];
    int n;
    const int p = nx2s_field(buf, ls, le, r, a, b, tmp, &n);
    if (n == 0) {
        *v = 0;
        return 1;
    }
    const char *t = tmp + p;
    int i = 0, neg = 0;
    if (t[i] == '+' || t[i] == '-') {
        neg = t[i] == '-';
        i++;
    }
    if (i == n)
        return 0;
    int64_t x = 0;
    for (; i < n; i++) {
        if (t[i] < '0' || t[i] > '9' || x > 100000000)
            return 0;
        x = 10 * x + (t[i] - '0');
    }
    *v = neg ? -x : x;
    return 1;
}

static char nx2s_chr(const char *buf, const int64_t *ls, const int64_t *le, int64_t r, int i)
{
    return i < le[r] - ls[r] ? buf[ls[r] + i] : ' ';
}

/* E, J, P, nb, tau of a level record; 1 when every field is plain */
static int nx2s_level(const char *buf, const int64_t *ls, const int64_t *le, int64_t r,
                      double *out, int64_t *nb)
{
    int64_t p;
    if (!nx2s_real(buf, ls, le, r, 4, 15, &out[0]) || !nx2s_real(buf, ls, le, r, 15, 21, &out[1])
        || !nx2s_int(buf, ls, le, r, 24, 26, &p) || !nx2s_int(buf, ls, le, r, 26, 29, nb)
        || !nx2s_real(buf, ls, le, r, 47, 57, &out[4]))
        return 0;
    out[2] = (double)p;
    out[3] = (double)*nb;
    return *nb >= 0;
}

int64_t nx2_struct_levels(const char *buf, const int64_t *ls, const int64_t *le, int64_t nrec,
                          int64_t nlev2, int64_t nlevmax2, double *lev, char *lchr, double *br,
                          char *bchr, double *rest, char *rchr)
{
    int64_t pos = 0, nbr = 0;
    for (int64_t i = 0; i <= nlev2; i++) {
        if (pos >= nrec)
            return -3;
        int64_t nb;
        if (!nx2s_level(buf, ls, le, pos, lev + 5 * i, &nb))
            return -1;
        for (int c = 0; c < 21; c++)
            lchr[21 * i + c] = nx2s_chr(buf, ls, le, pos, 57 + c);
        pos++;
        for (int64_t jj = 0; jj < nb; jj++, pos++) {
            if (pos >= nrec)
                return -3;
            int64_t kl;
            if (!nx2s_int(buf, ls, le, pos, 29, 32, &kl)
                || !nx2s_real(buf, ls, le, pos, 32, 42, &br[3 * nbr + 1])
                || !nx2s_real(buf, ls, le, pos, 42, 52, &br[3 * nbr + 2]))
                return -1;
            br[3 * nbr] = (double)kl;
            bchr[nbr] = nx2s_chr(buf, ls, le, pos, 57);
            nbr++;
        }
    }
    for (int64_t i = nlev2 + 1; i <= nlevmax2; i++) {
        if (pos >= nrec)
            return -3;
        double row[5];
        int64_t nb;
        if (!nx2s_level(buf, ls, le, pos, row, &nb))
            return -1;
        const int64_t k = i - nlev2 - 1;
        rest[4 * k] = row[0];
        rest[4 * k + 1] = row[1];
        rest[4 * k + 2] = row[2];
        rest[4 * k + 3] = row[4];
        for (int c = 0; c < 3; c++)
            rchr[3 * k + c] = nx2s_chr(buf, ls, le, pos, 57 + c);
        pos += 1 + nb;
    }
    return nbr;
}
