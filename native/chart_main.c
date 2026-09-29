/* CHARTDRV (ROUTE100's WP10): the one-box chart driver.
 *
 * A C binary with N pthreads that runs the whole CHART1 set on one machine. Each thread owns one
 * persistent warm Python worker (`scripts/hf_route100_chart.py serve`) and speaks one JSON line
 * per task to it. Two kinds of task share the threads:
 *
 *   NUCLIDE  (Z, A)                      -- a whole nuclide on the 20-point grid, the record the
 *                                           Python chart driver writes.
 *   CC block (Z, A, 2J, parity, energy)  -- one coupled-channels (J, parity) block at one
 *                                           incident energy, ROUTE100 section 2's scheduling unit.
 *
 * Why the second kind exists: the coupled-channels stage is 22.6 % of the chart and the largest
 * deformed target's CC is longer than many whole nuclides, so a per-nuclide queue leaves cores
 * idle at the tail. CCGLUE made `solver.sum_blocks` a list of `CCTask(two_j, parity, energy)` and
 * guaranteed a task's numbers do not depend on which other tasks shared its call, so this driver
 * may split a block's energies across threads and add the contributions back in task order. The
 * total-J loop itself -- the per-energy `QUIET_J` convergence, the J cap, the order of addition --
 * runs HERE, in `cc_job`, not in Python: the workers only execute blocks.
 *
 * Inputs: CREC's chart record (`--record ROOT/index.json`, also handed to every worker as
 * CHARTDRV_RECORD so a nuclide can be seeded instead of rebuilt) and the structure database's
 * task file (`--tasks`, `hf_route100_chart.py tasklist`: Z A colltype cls prior), heaviest first.
 *
 * Output: `OUT/cchart/ZZZ_AAA.json` in the Python driver's schema (so the two are comparable cell
 * by cell with `hf_route100_chart.py compare`), `OUT/cc/ZZZ_AAA.json` per coupled-channels target
 * with the assembled result checked against `sum_blocks` itself, and `OUT/chart_main.json`.
 *
 *   cc -O2 -pthread -o native/chart_main native/chart_main.c -lm     (scripts/build_chart_main.sh)
 *   native/chart_main --repo . --python .venv/bin/python --tasks T --out OUT --threads 16
 *
 * TALYS: none (driver policy; the physics is `ecis.solver` and `chartrun`)
 * Test: docs/results/hf-chartdrvb.md
 */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <math.h>
#include <pthread.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define MAXCTX 8
#define MAXTASK 4096

static double now_s(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + 1e-9 * t.tv_nsec;
}

static void die(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fputc('\n', stderr);
    exit(2);
}

static void *xmalloc(size_t n) {
    void *p = malloc(n ? n : 1);
    if (!p) die("out of memory (%zu)", n);
    return p;
}

/* ---------------------------------------------------------------- the wire's JSON, read flat
 * Both ends of this pipe are ours and every reply is a flat object of numbers, strings and
 * number arrays (`hf_route100_chart.serve`), so a key scan is enough: no nesting is ever read. */

static const char *jkey(const char *s, const char *key) {
    char pat[64];
    snprintf(pat, sizeof pat, "\"%s\":", key);
    const char *p = strstr(s, pat);
    return p ? p + strlen(pat) : NULL;
}

static double jnum(const char *s, const char *key, double dflt) {
    const char *p = jkey(s, key);
    if (!p) return dflt;
    char *end;
    double v = strtod(p, &end);
    return end == p ? dflt : v;
}

static int jbool(const char *s, const char *key, int dflt) {
    const char *p = jkey(s, key);
    if (!p) return dflt;
    while (*p == ' ') p++;
    return *p == 't' ? 1 : (*p == 'f' ? 0 : dflt);
}

/* `"key":[a,b,c]` into `out`; returns the count, or -1 if the key is missing. */
static int jarr(const char *s, const char *key, double *out, int max) {
    const char *p = jkey(s, key);
    if (!p) return -1;
    while (*p == ' ') p++;
    if (*p != '[') return -1;
    p++;
    int n = 0;
    for (;;) {
        while (*p == ' ' || *p == ',') p++;
        if (*p == ']' || !*p) break;
        char *end;
        double v = strtod(p, &end);
        if (end == p) break;
        if (n < max) out[n] = v;
        n++;
        p = end;
    }
    return n;
}

/* The string value of `key`, without unescaping: the only strings read are base64 and errors. */
static char *jstr(const char *s, const char *key, size_t *len) {
    const char *p = jkey(s, key);
    if (!p) return NULL;
    while (*p == ' ') p++;
    if (*p != '"') return NULL;
    p++;
    const char *q = p;
    while (*q && *q != '"') q += (*q == '\\' && q[1]) ? 2 : 1;
    size_t n = (size_t)(q - p);
    char *out = xmalloc(n + 1);
    memcpy(out, p, n);
    out[n] = 0;
    if (len) *len = n;
    return out;
}

static const signed char B64[256] = {
    ['A']=0,['B']=1,['C']=2,['D']=3,['E']=4,['F']=5,['G']=6,['H']=7,['I']=8,['J']=9,['K']=10,
    ['L']=11,['M']=12,['N']=13,['O']=14,['P']=15,['Q']=16,['R']=17,['S']=18,['T']=19,['U']=20,
    ['V']=21,['W']=22,['X']=23,['Y']=24,['Z']=25,['a']=26,['b']=27,['c']=28,['d']=29,['e']=30,
    ['f']=31,['g']=32,['h']=33,['i']=34,['j']=35,['k']=36,['l']=37,['m']=38,['n']=39,['o']=40,
    ['p']=41,['q']=42,['r']=43,['s']=44,['t']=45,['u']=46,['v']=47,['w']=48,['x']=49,['y']=50,
    ['z']=51,['0']=52,['1']=53,['2']=54,['3']=55,['4']=56,['5']=57,['6']=58,['7']=59,['8']=60,
    ['9']=61,['+']=62,['/']=63,
};

/* base64 into `out`; returns the byte count or -1. `=` padding ends the stream. */
static long b64dec(const char *in, size_t n, unsigned char *out, size_t max) {
    unsigned int acc = 0;
    int bits = 0;
    size_t m = 0;
    for (size_t i = 0; i < n; i++) {
        char c = in[i];
        if (c == '=') break;
        if (c == '\n' || c == '\r') continue;
        signed char v = B64[(unsigned char)c];
        if (v == 0 && c != 'A') return -1;
        acc = (acc << 6) | (unsigned int)v;
        bits += 6;
        if (bits >= 8) {
            bits -= 8;
            if (m >= max) return -1;
            out[m++] = (unsigned char)((acc >> bits) & 0xFF);
        }
    }
    return (long)m;
}

/* --------------------------------------------------------------------------------- the worker */

typedef struct {
    int idx;
    pid_t pid;
    int wfd;
    FILE *rd;
    char *line;
    size_t cap;
    double hello_cpu_s;
    /* the coupled-channels context this worker currently holds open */
    int cc_job;
    int cc_h;
    int nctx;
} Worker;

static char *g_repo, *g_python, *g_script, *g_out;

static void worker_start(Worker *w) {
    int to[2], from[2];
    if (pipe(to) || pipe(from)) die("pipe: %s", strerror(errno));
    char log[1024];
    snprintf(log, sizeof log, "%s/logs/worker%02d.log", g_out, w->idx);
    pid_t pid = fork();
    if (pid < 0) die("fork: %s", strerror(errno));
    if (pid == 0) {
        dup2(to[0], 0);
        dup2(from[1], 1);
        int e = open(log, O_WRONLY | O_CREAT | O_APPEND, 0644);
        if (e >= 0) dup2(e, 2);
        close(to[0]); close(to[1]); close(from[0]); close(from[1]);
        if (chdir(g_repo)) _exit(70);
        char *argv[] = {g_python, g_script, (char *)"serve", NULL};
        execv(g_python, argv);
        _exit(71);
    }
    close(to[0]);
    close(from[1]);
    w->pid = pid;
    w->wfd = to[1];
    w->rd = fdopen(from[0], "r");
    w->cc_job = -1;
    w->cc_h = 0;
}

static const char B64E[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

/* `n` bytes into a malloc'd base64 string. */
static char *b64enc(const unsigned char *in, size_t n) {
    char *out = xmalloc(4 * ((n + 2) / 3) + 1);
    size_t m = 0;
    for (size_t i = 0; i < n; i += 3) {
        unsigned int v = (unsigned int)in[i] << 16;
        if (i + 1 < n) v |= (unsigned int)in[i + 1] << 8;
        if (i + 2 < n) v |= in[i + 2];
        out[m++] = B64E[(v >> 18) & 63];
        out[m++] = B64E[(v >> 12) & 63];
        out[m++] = (i + 1 < n) ? B64E[(v >> 6) & 63] : '=';
        out[m++] = (i + 2 < n) ? B64E[v & 63] : '=';
    }
    out[m] = 0;
    return out;
}

/* One already-built line out, one reply in (for payloads too big for `worker_call`'s buffer). */
static const char *worker_send(Worker *w, char *line, size_t n) {
    line[n] = '\n';
    for (size_t off = 0; off < n + 1;) {
        ssize_t k = write(w->wfd, line + off, n + 1 - off);
        if (k <= 0) return NULL;
        off += (size_t)k;
    }
    ssize_t got = getline(&w->line, &w->cap, w->rd);
    return got > 0 ? w->line : NULL;
}

/* One task out, one reply in. The reply line stays in `w->line` until the next call. */
static const char *worker_call(Worker *w, const char *fmt, ...) {
    char buf[4096];
    va_list ap;
    va_start(ap, fmt);
    int n = vsnprintf(buf, sizeof buf - 2, fmt, ap);
    va_end(ap);
    if (n < 0 || n >= (int)sizeof buf - 2) return NULL;
    buf[n++] = '\n';
    buf[n] = 0;
    for (int off = 0; off < n;) {
        ssize_t k = write(w->wfd, buf + off, (size_t)(n - off));
        if (k <= 0) return NULL;
        off += (int)k;
    }
    ssize_t got = getline(&w->line, &w->cap, w->rd);
    return got > 0 ? w->line : NULL;
}

/* The worker's resident set, MB (`/proc/PID/statm` field 2, pages). */
static double worker_rss_mb(Worker *w) {
    char p[64];
    snprintf(p, sizeof p, "/proc/%d/statm", (int)w->pid);
    FILE *f = fopen(p, "r");
    if (!f) return -1.0;
    long total = 0, res = 0;
    int got = fscanf(f, "%ld %ld", &total, &res);
    fclose(f);
    (void)total;
    return got == 2 ? (double)res * (double)sysconf(_SC_PAGESIZE) / (1024.0 * 1024.0) : -1.0;
}

static void worker_stop(Worker *w) {
    if (w->pid <= 0) return;
    worker_call(w, "{\"kind\":\"bye\"}");
    close(w->wfd);
    int st;
    for (int i = 0; i < 100; i++) {
        if (waitpid(w->pid, &st, WNOHANG) == w->pid) { w->pid = -1; break; }
        usleep(50000);
    }
    if (w->pid > 0) { kill(w->pid, SIGKILL); waitpid(w->pid, &st, 0); w->pid = -1; }
    if (w->rd) fclose(w->rd);
}

/* ------------------------------------------------------------------------------ the task space */

typedef struct {
    int Z, A;
    char colltype[4], cls[24];
    double prior;
    int cc;
    int skip;               /* --cc-feed: run by the coupled-channels leader, not the queue */                 /* colltype R or V: this nuclide also carries CC block tasks */
    int in_record;
} Nuc;

typedef struct CCJob {
    Nuc *n;
    int nctx;
    int n_e[MAXCTX], n_lev[MAXCTX], lmax[MAXCTX], two_j0[MAXCTX], j_cap[MAXCTX], quiet_j[MAXCTX];
    double j_tol[MAXCTX];
    double *fac[MAXCTX];    /* pi/k_1^2 * MB_PER_FM2 per energy row */
    /* the round in flight */
    int ntask, remaining;
    int r_two_j, r_parity_of[MAXTASK], r_row0[MAXTASK], r_nrow[MAXTASK], r_ctx;
    int r_rows[MAXTASK];    /* the active rows, chunked by --cc-rows into the tasks above */
    double *r_buf[MAXTASK];
    int r_empty[MAXTASK];
    int r_fail;
    int qh, qt;             /* this job's round, waiting for any free thread */
    int live;
    /* results */
    int tasks_run, n_j[MAXCTX];
    double last_frac[MAXCTX], cc_wall_s, open_cpu_s, worst_abs, worst_rel;
    int installed;
    long cells, bitwise;
    int ok;
} CCJob;

static Nuc *g_nuc;
static int g_nnuc;
static CCJob *g_cc;
static int g_ncc;

static pthread_mutex_t g_mu = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t g_cv = PTHREAD_COND_INITIALIZER;
static int g_next_nuc, g_next_cc, g_cc_active, g_cc_max = 1, g_done_n, g_total;

/* The job whose round still has unclaimed (block, energy) tasks, oldest first: any thread that is
 * between nuclides picks one up. `g_mu` is held. */
static CCJob *pending_cc(void) {
    for (int i = 0; i < g_next_cc; i++)
        if (g_cc[i].live && g_cc[i].qh < g_cc[i].qt) return &g_cc[i];
    return NULL;
}
static double g_t0;
static double g_rss_cap;                 /* --rss-cap-mb: restart a worker above it */
static long g_restarts;
static int g_cc_rows = 1;                /* --cc-rows: energies per (block, energy) task */
static int g_cc_feed;                    /* --cc-feed: the CC tasks replace the nuclide's own solve */
static long g_nuc_ok, g_nuc_err;
static double g_nuc_cpu;

/* ------------------------------------------------------------------------------ nuclide tasks */

static void run_nuclide(Worker *w, Nuc *n) {
    double t0 = now_s();
    const char *rep = worker_call(w, "{\"kind\":\"nuclide\",\"Z\":%d,\"A\":%d}", n->Z, n->A);
    double wall = now_s() - t0;
    char path[1024];
    snprintf(path, sizeof path, "%s/cchart/%03d_%03d.json", g_out, n->Z, n->A);
    FILE *f = fopen(path, "w");
    if (!f) die("open %s: %s", path, strerror(errno));
    fprintf(f, "{\"cls\":\"%s\",\"colltype\":\"%s\",\"arm\":\"cchart\",\"slot\":%d,"
               "\"driver_wall_s\":%.6f,\"in_record\":%s,",
            n->cls, n->colltype, w->idx, wall, n->in_record ? "true" : "false");
    if (rep) {
        const char *body = strchr(rep, '{');
        fputs(body ? body + 1 : "\"ok\":false}", f);           /* the worker's own record */
    } else {
        fprintf(f, "\"Z\":%d,\"A\":%d,\"ok\":false,\"err\":\"LostWorker\"}\n", n->Z, n->A);
    }
    fclose(f);
    int ok = rep ? jbool(rep, "ok", 0) : 0;
    double cpu = rep ? jnum(rep, "cpu_s", 0.0) : 0.0;
    /* MERGEX's `MACSPEED_RSS_CAP_MB`, in the driver: a worker whose resident set is over the cap
     * after its cache drop is restarted before its next nuclide, so 16 of them fit the box. */
    double rss = g_rss_cap > 0.0 ? worker_rss_mb(w) : -1.0;
    if (rss > g_rss_cap && !g_cc_active) {
        worker_stop(w);
        worker_start(w);                      /* `worker_start` resets the CC handle it held */
        ssize_t g = getline(&w->line, &w->cap, w->rd);
        if (g <= 0 || !jbool(w->line, "ready", 0)) die("worker %d did not restart", w->idx);
        pthread_mutex_lock(&g_mu);
        g_restarts++;
        pthread_mutex_unlock(&g_mu);
    }
    pthread_mutex_lock(&g_mu);
    if (ok) { g_nuc_ok++; g_nuc_cpu += cpu; } else g_nuc_err++;
    g_done_n++;
    fprintf(stderr, "[%4d/%d %5.1fs t%02d] %d-%d %-10s %s %6.2f cpu-s\n", g_done_n, g_total,
            now_s() - g_t0, w->idx, n->Z, n->A, n->cls, ok ? "ok " : "ERR", cpu);
    pthread_mutex_unlock(&g_mu);
}

/* ------------------------------------------------------------- the coupled-channels block tasks */

/* Open this job's contexts on `w`, so the thread can execute any of its blocks. Every worker that
 * helps a CC job pays this once; the numbers are a function of the target alone, so the contexts
 * are the same on every worker and the driver checks the shapes agree. */
static int cc_ensure(Worker *w, CCJob *j) {
    if (w->cc_job == (int)(j - g_cc)) return 0;
    if (w->cc_h) worker_call(w, "{\"kind\":\"cc_close\",\"h\":%d}", w->cc_h);
    w->cc_h = 0;
    w->cc_job = -1;
    const char *rep = worker_call(w, "{\"kind\":\"cc_open\",\"Z\":%d,\"A\":%d}", j->n->Z, j->n->A);
    if (!rep || !jbool(rep, "ok", 0)) return -1;
    int nctx = (int)jnum(rep, "nctx", -1);
    if (nctx != j->nctx) return -1;
    double a[MAXCTX];
    if (jarr(rep, "n_e", a, MAXCTX) == nctx)
        for (int i = 0; i < nctx; i++)
            if ((int)a[i] != j->n_e[i]) return -1;
    w->cc_h = (int)jnum(rep, "h", 0);
    w->cc_job = (int)(j - g_cc);
    w->nctx = nctx;
    return w->cc_h ? 0 : -1;
}

/* Read the job's shape from a first `cc_open` on `w`, which then keeps the handle. */
static int cc_start(Worker *w, CCJob *j) {
    double t0 = now_s();
    const char *rep = worker_call(w, "{\"kind\":\"cc_open\",\"Z\":%d,\"A\":%d}", j->n->Z, j->n->A);
    if (!rep || !jbool(rep, "ok", 0)) return -1;
    j->nctx = (int)jnum(rep, "nctx", 0);
    if (j->nctx <= 0 || j->nctx > MAXCTX) return -1;
    double a[MAXCTX];
    struct { const char *k; int *d; } ints[] = {
        {"n_e", j->n_e}, {"n_lev", j->n_lev}, {"lmax", j->lmax},
        {"two_j0", j->two_j0}, {"j_cap", j->j_cap}, {"quiet_j", j->quiet_j}};
    for (size_t k = 0; k < sizeof ints / sizeof *ints; k++) {
        if (jarr(rep, ints[k].k, a, MAXCTX) != j->nctx) return -1;
        for (int i = 0; i < j->nctx; i++) ints[k].d[i] = (int)a[i];
    }
    if (jarr(rep, "j_tol", j->j_tol, MAXCTX) != j->nctx) return -1;
    size_t nfac = 0;
    for (int i = 0; i < j->nctx; i++) nfac += (size_t)j->n_e[i];
    size_t len = 0;
    char *b64 = jstr(rep, "fac_b64", &len);
    if (!b64) return -1;
    unsigned char *raw = xmalloc(nfac * 8 + 16);
    long got = b64dec(b64, len, raw, nfac * 8 + 16);
    free(b64);
    if (got != (long)(nfac * 8)) { free(raw); return -1; }
    size_t off = 0;
    for (int i = 0; i < j->nctx; i++) {
        j->fac[i] = xmalloc((size_t)j->n_e[i] * sizeof(double));
        memcpy(j->fac[i], raw + off, (size_t)j->n_e[i] * sizeof(double));
        off += (size_t)j->n_e[i] * 8;
    }
    free(raw);
    w->cc_h = (int)jnum(rep, "h", 0);
    w->cc_job = (int)(j - g_cc);
    w->nctx = j->nctx;
    j->open_cpu_s += now_s() - t0;
    return w->cc_h ? 0 : -1;
}

/* One (block, energy) task: 2J = `r_two_j`, the slot's parity and its chunk of energy rows. */
static void cc_exec(Worker *w, CCJob *j, int slot) {
    int nrow = j->r_nrow[slot];
    int per = nrow * (3 + j->n_lev[j->r_ctx] + 2 * (j->lmax[j->r_ctx] + 1));
    if (cc_ensure(w, j) != 0) { j->r_fail = 1; j->r_empty[slot] = 1; return; }
    char rows[512];
    int rn = 0;
    for (int i = 0; i < nrow && rn < (int)sizeof rows - 12; i++)
        rn += snprintf(rows + rn, sizeof rows - (size_t)rn, "%s%d", i ? "," : "",
                       j->r_rows[j->r_row0[slot] + i]);
    const char *rep = worker_call(
        w, "{\"kind\":\"cc_task\",\"h\":%d,\"ctx\":%d,\"two_j\":%d,\"parity\":%d,\"rows\":[%s]}",
        w->cc_h, j->r_ctx, j->r_two_j, j->r_parity_of[slot], rows);
    if (!rep || !jbool(rep, "ok", 0)) { j->r_fail = 1; j->r_empty[slot] = 1; return; }
    if (jbool(rep, "empty", 0)) { j->r_empty[slot] = 1; return; }
    size_t len = 0;
    char *b64 = jstr(rep, "b64", &len);
    if (!b64) { j->r_fail = 1; j->r_empty[slot] = 1; return; }
    double *buf = xmalloc((size_t)per * sizeof(double));
    long got = b64dec(b64, len, (unsigned char *)buf, (size_t)per * sizeof(double));
    free(b64);
    if (got != (long)((size_t)per * sizeof(double))) {
        free(buf);
        j->r_fail = 1;
        j->r_empty[slot] = 1;
        return;
    }
    j->r_buf[slot] = buf;
}

/* The total-J loop of `solver._sum_blocks_tasks`, run by the driver: each round's (block, energy)
 * tasks go on the queue for any free thread, and the contributions are added back in task order
 * (parity -1 before +1, rows ascending), which is the order `cc_tasks` lists them in. */
static void cc_job(Worker *w, CCJob *j) {
    double t0 = now_s();
    if (cc_start(w, j) != 0) { j->ok = 0; return; }
    j->ok = 1;
    for (int c = 0; c < j->nctx && j->ok; c++) {
        int n_e = j->n_e[c], n_lev = j->n_lev[c], lt = 2 * (j->lmax[c] + 1);
        double *reac = calloc((size_t)n_e, sizeof(double));
        double *tot = calloc((size_t)n_e, sizeof(double));
        double *el = calloc((size_t)n_e, sizeof(double));
        double *dir = calloc((size_t)n_e * n_lev, sizeof(double));
        double *tjl = calloc((size_t)n_e * lt, sizeof(double));
        double *bmax = calloc((size_t)n_e, sizeof(double));
        double *frac = calloc((size_t)n_e, sizeof(double));
        int *quiet = calloc((size_t)n_e, sizeof(int));
        int *active = xmalloc((size_t)n_e * sizeof(int));
        int na = n_e;
        for (int i = 0; i < n_e; i++) active[i] = i;
        int two_j = j->two_j0[c], n_j = 0;
        while (na > 0) {
            memset(bmax, 0, (size_t)n_e * sizeof(double));
            int nt = 0, nr = 0;
            if ((two_j - j->two_j0[c]) / 2 < j->j_cap[c]) {
                int chunk = g_cc_rows > 0 ? g_cc_rows : na;   /* --cc-rows: energies per task */
                for (int p = 0; p < 2; p++)
                    for (int i = 0; i < na; i += chunk) {
                        if (nt >= MAXTASK || nr + na > MAXTASK) break;
                        int m = na - i < chunk ? na - i : chunk;
                        j->r_parity_of[nt] = p ? 1 : -1;
                        j->r_row0[nt] = nr;
                        j->r_nrow[nt] = m;
                        for (int q = 0; q < m; q++) j->r_rows[nr++] = active[i + q];
                        j->r_buf[nt] = NULL;
                        j->r_empty[nt] = 0;
                        nt++;
                    }
            }
            if (nt) {
                pthread_mutex_lock(&g_mu);
                j->r_ctx = c;
                j->r_two_j = two_j;
                j->ntask = nt;
                j->remaining = nt;
                j->qh = 0;
                j->qt = nt;
                pthread_cond_broadcast(&g_cv);
                /* the leader is a worker too: it drains its own round and only waits when
                 * the queue is empty but other threads still hold tasks */
                for (;;) {
                    if (j->qh < j->qt) {
                        int slot = j->qh++;
                        pthread_mutex_unlock(&g_mu);
                        cc_exec(w, j, slot);
                        pthread_mutex_lock(&g_mu);
                        j->remaining--;
                        j->tasks_run++;
                        pthread_cond_broadcast(&g_cv);
                        continue;
                    }
                    if (j->remaining <= 0) break;
                    pthread_cond_wait(&g_cv, &g_mu);
                }
                pthread_mutex_unlock(&g_mu);
                /* in task order (parity -1 before +1, rows ascending): `cc_tasks`'s own order,
                 * which is the order `sum_blocks` adds the blocks in */
                for (int i = 0; i < nt; i++) {
                    if (j->r_empty[i] || !j->r_buf[i]) continue;
                    int m = j->r_nrow[i];
                    const int *rw = &j->r_rows[j->r_row0[i]];
                    double *v = j->r_buf[i];              /* reac|tot|el|direct|tjl, `pack` */
                    for (int q = 0; q < m; q++) {
                        reac[rw[q]] += v[q];
                        double b = fabs(v[q]);
                        if (b > bmax[rw[q]]) bmax[rw[q]] = b;
                    }
                    for (int q = 0; q < m; q++) tot[rw[q]] += v[m + q];
                    for (int q = 0; q < m; q++) el[rw[q]] += v[2 * m + q];
                    const double *d = v + 3 * m, *t = v + 3 * m + (size_t)m * n_lev;
                    for (int q = 0; q < m; q++)
                        for (int k = 0; k < n_lev; k++)
                            dir[(size_t)rw[q] * n_lev + k] += d[(size_t)q * n_lev + k];
                    for (int q = 0; q < m; q++)
                        for (int k = 0; k < lt; k++)
                            tjl[(size_t)rw[q] * lt + k] += t[(size_t)q * lt + k];
                    free(j->r_buf[i]);
                    j->r_buf[i] = NULL;
                }
            }
            n_j++;
            int nn = 0;
            for (int i = 0; i < na; i++) {
                int row = active[i];
                double ref = fabs(reac[row]);
                quiet[row] = (ref > 0.0 && bmax[row] < j->j_tol[c] * ref) ? quiet[row] + 1 : 0;
                frac[row] = bmax[row] / (ref > 1.0e-300 ? ref : 1.0e-300);
                if (quiet[row] < j->quiet_j[c]) active[nn++] = row;
            }
            if (n_j > 4 * (j->lmax[c] + 2)) break;
            na = nn;
            two_j += 2;
        }
        j->n_j[c] = n_j;
        double fmax = 0.0;
        for (int i = 0; i < n_e; i++) if (frac[i] > fmax) fmax = frac[i];
        j->last_frac[c] = fmax;

        /* the summed blocks in mb (`_coupled_result`): sigma_abs | sigma_tot | sigma_shape_el |
         * sigma_direct | T_lj, the layout `cc_ref` and `cc_install` both speak */
        size_t nd = (size_t)n_e * (3 + n_lev + lt), o = 0;
        double *mine = xmalloc(nd * sizeof(double));
        for (int i = 0; i < n_e; i++) mine[o++] = j->fac[c][i] * reac[i];
        for (int i = 0; i < n_e; i++) mine[o++] = j->fac[c][i] * tot[i];
        for (int i = 0; i < n_e; i++) mine[o++] = j->fac[c][i] * el[i];
        for (int i = 0; i < n_e; i++)
            for (int k = 0; k < n_lev; k++) mine[o++] = j->fac[c][i] * dir[(size_t)i * n_lev + k];
        for (size_t i = 0; i < (size_t)n_e * lt; i++) mine[o++] = tjl[i];
        if (g_cc_feed) {                 /* hand the rows to this worker's `incident._SOLVED` */
            char *b64 = b64enc((const unsigned char *)mine, nd * sizeof(double));
            size_t cap = strlen(b64) + 256;
            char *line = xmalloc(cap + 2);
            int n = snprintf(line, cap, "{\"kind\":\"cc_install\",\"h\":%d,\"ctx\":%d,"
                                        "\"n_j\":%d,\"frac\":%.17g,\"b64\":\"%s\"}",
                             w->cc_h, c, n_j, fmax, b64);
            const char *rep = (n > 0 && (size_t)n < cap) ? worker_send(w, line, (size_t)n) : NULL;
            if (!rep || !jbool(rep, "ok", 0) || jnum(rep, "installed", 0) <= 0) j->ok = 0;
            else j->installed += (int)jnum(rep, "installed", 0);
            free(line);
            free(b64);
        }
        /* against `sum_blocks` itself, on the same context, packed the same way */
        const char *rep = worker_call(w, "{\"kind\":\"cc_ref\",\"h\":%d,\"ctx\":%d}", w->cc_h, c);
        size_t len = 0;
        char *b64r = (rep && jbool(rep, "ok", 0)) ? jstr(rep, "b64", &len) : NULL;
        double *ref = xmalloc(nd * sizeof(double));
        long got = b64r ? b64dec(b64r, len, (unsigned char *)ref, nd * sizeof(double)) : -1;
        free(b64r);
        if (got == (long)(nd * sizeof(double))) {
            for (size_t i = 0; i < nd; i++) {
                j->cells++;
                if (mine[i] == ref[i]) { j->bitwise++; continue; }
                double d = fabs(mine[i] - ref[i]);
                double r = d / (fabs(ref[i]) > 0.0 ? fabs(ref[i]) : 1.0);
                if (d > j->worst_abs) j->worst_abs = d;
                if (r > j->worst_rel) j->worst_rel = r;
            }
        } else {
            j->ok = 0;
        }
        free(ref);
        free(mine);
        free(reac); free(tot); free(el); free(dir); free(tjl);
        free(bmax); free(frac); free(quiet); free(active);
    }
    j->cc_wall_s = now_s() - t0;
    char path[1024];
    snprintf(path, sizeof path, "%s/cc/%03d_%03d.json", g_out, j->n->Z, j->n->A);
    FILE *f = fopen(path, "w");
    if (f) {
        fprintf(f, "{\"Z\":%d,\"A\":%d,\"colltype\":\"%s\",\"cls\":\"%s\",\"ok\":%s,\"nctx\":%d,"
                   "\"tasks\":%d,\"installed\":%d,\"cc_wall_s\":%.6f,\"open_cpu_s\":%.6f,\"cells\":%ld,"
                   "\"bitwise\":%ld,\"worst_abs\":%.17g,\"worst_rel\":%.17g,\"ctx\":[",
                j->n->Z, j->n->A, j->n->colltype, j->n->cls, j->ok ? "true" : "false", j->nctx,
                j->tasks_run, j->installed, j->cc_wall_s, j->open_cpu_s, j->cells, j->bitwise, j->worst_abs,
                j->worst_rel);
        for (int c = 0; c < j->nctx; c++)
            fprintf(f, "%s{\"i\":%d,\"n_e\":%d,\"n_lev\":%d,\"lmax\":%d,\"n_j\":%d,"
                       "\"last_j_fraction\":%.17g}", c ? "," : "", c, j->n_e[c], j->n_lev[c],
                    j->lmax[c], j->n_j[c], j->last_frac[c]);
        fprintf(f, "]}\n");
        fclose(f);
    }
    pthread_mutex_lock(&g_mu);
    fprintf(stderr, "[ cc %5.1fs t%02d] %d-%d %s %d ctx %d tasks %.2fs bitwise %ld/%ld "
                    "worst_rel %.2e%s\n", now_s() - g_t0, w->idx, j->n->Z, j->n->A,
            j->n->colltype, j->nctx, j->tasks_run, j->cc_wall_s, j->bitwise, j->cells,
            j->worst_rel, j->ok ? "" : "  FAIL");
    pthread_mutex_unlock(&g_mu);
}

/* ------------------------------------------------------------------------------- the pthreads */

static void *thread_main(void *arg) {
    Worker *w = arg;
    worker_start(w);
    ssize_t got = getline(&w->line, &w->cap, w->rd);
    if (got <= 0 || !jbool(w->line, "ready", 0)) die("worker %d never became ready", w->idx);
    w->hello_cpu_s = jnum(w->line, "warm_cpu_s", 0.0);
    for (;;) {
        pthread_mutex_lock(&g_mu);
        for (;;) {
            CCJob *p = pending_cc();
            if (p) {                                            /* a CC block task is waiting */
                int slot = p->qh++;
                pthread_mutex_unlock(&g_mu);
                cc_exec(w, p, slot);
                pthread_mutex_lock(&g_mu);
                p->remaining--;
                p->tasks_run++;
                pthread_cond_broadcast(&g_cv);
                continue;
            }
            if (g_cc_active < g_cc_max && g_next_cc < g_ncc) {  /* become a CC leader */
                CCJob *j = &g_cc[g_next_cc++];
                j->live = 1;
                g_cc_active++;
                pthread_mutex_unlock(&g_mu);
                cc_job(w, j);
                pthread_mutex_lock(&g_mu);
                j->live = 0;
                g_cc_active--;
                pthread_mutex_unlock(&g_mu);
                if (g_cc_feed) run_nuclide(w, j->n);   /* same worker: `_SOLVED` holds its rows */
                pthread_mutex_lock(&g_mu);
                pthread_cond_broadcast(&g_cv);
                continue;
            }
            while (g_next_nuc < g_nnuc && g_nuc[g_next_nuc].skip) g_next_nuc++;
            if (g_next_nuc < g_nnuc) {                          /* otherwise a whole nuclide */
                Nuc *n = &g_nuc[g_next_nuc++];
                pthread_mutex_unlock(&g_mu);
                run_nuclide(w, n);
                pthread_mutex_lock(&g_mu);
                continue;
            }
            /* nothing left anywhere; a thread stays while a CC job is live, so the tail's
             * (block, energy) rounds still find helpers */
            if (!g_cc_active && g_next_cc >= g_ncc) break;
            pthread_cond_wait(&g_cv, &g_mu);
        }
        pthread_mutex_unlock(&g_mu);
        break;
    }
    if (w->cc_h) worker_call(w, "{\"kind\":\"cc_close\",\"h\":%d}", w->cc_h);
    worker_stop(w);
    return NULL;
}

/* ------------------------------------------------------------------------- the record and input */

/* CREC's chart index: which nuclides the record can seed. */
static int record_has(const char *idx, int Z, int A) {
    char pat[32];
    snprintf(pat, sizeof pat, "\"%d-%d\":", Z, A);
    return strstr(idx, pat) != NULL;
}

static char *slurp(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *s = xmalloc((size_t)n + 1);
    if (fread(s, 1, (size_t)n, f) != (size_t)n) { fclose(f); free(s); return NULL; }
    s[n] = 0;
    fclose(f);
    return s;
}

static void mkdirs(const char *out) {
    char p[1024];
    const char *sub[] = {"", "/cchart", "/cc", "/logs"};
    for (size_t i = 0; i < sizeof sub / sizeof *sub; i++) {
        snprintf(p, sizeof p, "%s%s", out, sub[i]);
        if (mkdir(p, 0755) && errno != EEXIST) die("mkdir %s: %s", p, strerror(errno));
    }
}

int main(int argc, char **argv) {
    const char *tasks = NULL, *record = NULL;
    int threads = 16, resume = 0, cc_only = 0, no_cc = 0;
    g_repo = (char *)".";
    g_python = (char *)".venv/bin/python";
    g_out = (char *)"chartdrv_out";
    for (int i = 1; i < argc; i++) {
        const char *a = argv[i];
        int last = i + 1 >= argc;
#define ARG(name, var) if (!strcmp(a, name) && !last) { var = argv[++i]; continue; }
        ARG("--repo", g_repo)
        ARG("--python", g_python)
        ARG("--out", g_out)
        ARG("--tasks", tasks)
        ARG("--record", record)
#undef ARG
        if (!strcmp(a, "--threads") && !last) { threads = atoi(argv[++i]); continue; }
        if (!strcmp(a, "--resume")) { resume = 1; continue; }
        if (!strcmp(a, "--cc-only")) { cc_only = 1; continue; }
        if (!strcmp(a, "--no-cc")) { no_cc = 1; continue; }
        if (!strcmp(a, "--cc-feed")) { g_cc_feed = 1; continue; }
        if (!strcmp(a, "--cc-jobs") && !last) { g_cc_max = atoi(argv[++i]); continue; }
        if (!strcmp(a, "--cc-rows") && !last) { g_cc_rows = atoi(argv[++i]); continue; }
        if (!strcmp(a, "--rss-cap-mb") && !last) { g_rss_cap = atof(argv[++i]); continue; }
        die("usage: chart_main --tasks FILE --out DIR [--repo D] [--python P] [--record ROOT]\n"
            "                   [--threads N] [--resume] [--cc-only] [--no-cc] [--cc-feed] [--cc-jobs K] [--cc-rows R] [--rss-cap-mb M]\n"
            "                   (bad arg %s)", a);
    }
    if (!tasks) die("--tasks is required");
    if (threads < 1 || threads > 256) die("--threads out of range");
    if (g_cc_max < 1 || g_cc_max > 64) die("--cc-jobs out of range");
    char rp[1024], op[1024], sp[2048];
    if (!realpath(g_repo, rp)) die("--repo %s: %s", g_repo, strerror(errno));
    g_repo = rp;
    snprintf(sp, sizeof sp, "%s/scripts/hf_route100_chart.py", g_repo);
    g_script = sp;
    if (g_python[0] != '/') {
        static char pp[1024];
        snprintf(pp, sizeof pp, "%s/%s", g_repo, g_python);
        g_python = pp;
    }
    mkdirs(g_out);
    if (!realpath(g_out, op)) die("--out %s: %s", g_out, strerror(errno));
    g_out = op;

    char *idx = NULL;
    if (record) {
        char ip[1024];
        snprintf(ip, sizeof ip, "%s/index.json", record);
        idx = slurp(ip);
        if (!idx) die("--record %s: no index.json", record);
        setenv("CHARTDRV_RECORD", record, 1);
    }
    char *txt = slurp(tasks);
    if (!txt) die("--tasks %s: %s", tasks, strerror(errno));
    int cap = 1024;
    g_nuc = xmalloc((size_t)cap * sizeof(Nuc));
    for (char *line = strtok(txt, "\n"); line; line = strtok(NULL, "\n")) {
        Nuc n;
        memset(&n, 0, sizeof n);
        if (sscanf(line, "%d %d %3s %23s %lf", &n.Z, &n.A, n.colltype, n.cls, &n.prior) < 4)
            continue;
        n.cc = (!strcmp(n.colltype, "R") || !strcmp(n.colltype, "V"));
        n.in_record = idx ? record_has(idx, n.Z, n.A) : 0;
        if (resume) {
            char p[1024];
            snprintf(p, sizeof p, "%s/cchart/%03d_%03d.json", g_out, n.Z, n.A);
            if (!access(p, R_OK)) continue;
        }
        if (g_nnuc == cap) { cap *= 2; g_nuc = realloc(g_nuc, (size_t)cap * sizeof(Nuc)); }
        g_nuc[g_nnuc++] = n;
    }
    g_cc = xmalloc((size_t)(g_nnuc + 1) * sizeof(CCJob));
    memset(g_cc, 0, (size_t)(g_nnuc + 1) * sizeof(CCJob));
    if (!no_cc)
        for (int i = 0; i < g_nnuc; i++)
            if (g_nuc[i].cc) {
                g_cc[g_ncc++].n = &g_nuc[i];
                g_nuc[i].skip = g_cc_feed;
            }
    if (cc_only) g_next_nuc = g_nnuc;
    g_total = cc_only ? 0 : g_nnuc;
    int in_rec = 0;
    for (int i = 0; i < g_nnuc; i++) in_rec += g_nuc[i].in_record;
    fprintf(stderr, "chart_main: %d nuclides (%d in the record), %d coupled-channels targets, "
                    "%d threads, %d CC job(s) at a time%s\n", g_nnuc, in_rec, g_ncc, threads, g_cc_max,
            g_cc_feed ? ", CC fed back into the nuclide" : "");
    if (threads > g_nnuc + g_ncc && threads > 1) threads = g_nnuc + g_ncc ? threads : 1;

    g_t0 = now_s();
    Worker *ws = xmalloc((size_t)threads * sizeof(Worker));
    memset(ws, 0, (size_t)threads * sizeof(Worker));
    pthread_t *th = xmalloc((size_t)threads * sizeof(pthread_t));
    for (int i = 0; i < threads; i++) {
        ws[i].idx = i;
        if (pthread_create(&th[i], NULL, thread_main, &ws[i])) die("pthread_create");
    }
    for (int i = 0; i < threads; i++) pthread_join(th[i], NULL);
    double wall = now_s() - g_t0;
    struct rusage ru, ch;
    getrusage(RUSAGE_SELF, &ru);
    getrusage(RUSAGE_CHILDREN, &ch);
    double self_cpu = ru.ru_utime.tv_sec + 1e-6 * ru.ru_utime.tv_usec + ru.ru_stime.tv_sec
                      + 1e-6 * ru.ru_stime.tv_usec;
    double kid_cpu = ch.ru_utime.tv_sec + 1e-6 * ch.ru_utime.tv_usec + ch.ru_stime.tv_sec
                     + 1e-6 * ch.ru_stime.tv_usec;
    long cells = 0, bit = 0, cctasks = 0;
    double worst_rel = 0.0, cc_wall = 0.0;
    int cc_ok = 0;
    for (int i = 0; i < g_ncc; i++) {
        cells += g_cc[i].cells;
        bit += g_cc[i].bitwise;
        cctasks += g_cc[i].tasks_run;
        cc_wall += g_cc[i].cc_wall_s;
        cc_ok += g_cc[i].ok;
        if (g_cc[i].worst_rel > worst_rel) worst_rel = g_cc[i].worst_rel;
    }
    char p[1024];
    snprintf(p, sizeof p, "%s/chart_main.json", g_out);
    FILE *f = fopen(p, "w");
    if (f) {
        fprintf(f, "{\"threads\":%d,\"cc_jobs\":%d,\"cc_rows\":%d,\"cc_feed\":%s,\"nuclides\":%d,\"in_record\":%d,\"nuclide_ok\":%ld,"
                   "\"nuclide_err\":%ld,\"nuclide_cpu_s\":%.3f,\"cc_targets\":%d,\"cc_ok\":%d,"
                   "\"cc_tasks\":%ld,\"cc_wall_s\":%.3f,\"cc_cells\":%ld,\"cc_bitwise\":%ld,"
                   "\"cc_worst_rel\":%.17g,\"wall_s\":%.3f,\"driver_cpu_s\":%.3f,"
                   "\"worker_cpu_s\":%.3f,\"worker_restarts\":%ld,\"record\":%s}\n",
                threads, g_cc_max, g_cc_rows, g_cc_feed ? "true" : "false", g_nnuc, in_rec, g_nuc_ok, g_nuc_err, g_nuc_cpu, g_ncc, cc_ok, cctasks,
                cc_wall, cells, bit, worst_rel, wall, self_cpu, kid_cpu, g_restarts,
                record ? "true" : "false");
        fclose(f);
    }
    fprintf(stderr, "chart_main: %.1f s wall, %ld ok / %ld err, CC %d/%d ok, %ld tasks, "
                    "bitwise %ld/%ld, worst_rel %.3e, driver cpu %.2f s, workers %.1f s\n",
            wall, g_nuc_ok, g_nuc_err, cc_ok, g_ncc, cctasks, bit, cells, worst_rel, self_cpu,
            kid_cpu);
    return (g_nuc_err || cc_ok != g_ncc) ? 1 : 0;
}
