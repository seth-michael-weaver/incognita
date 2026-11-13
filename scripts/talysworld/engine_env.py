"""Engine switch names: the ONE table between the production engine's names and this repository's.

The calculator and benchmark launchers (engine_job.py, and through it engine_grid.py, warmpool.py, server.py,
check*.py, scripts/perf/bench.py; tests/hf/perfcasc_gate_run.py) set the library v0.2 run environment, and the library's
runner bundle (libv02/inputs/code: pprun, r52pool, engine_pool) sets more of it per job, all under the production
engine's names: build 16606b356d6e (engine-20261022-3) reads NUCLIDO_*. This repository's engine (physics/hf) reads the
same switches as INCOGNITA_*. Without the mirror, a launcher whose TW_ENG is this repository would run a different configuration from
production without any error (no `GGDEADEND`, `DWBAUNIT`, `ISOE2` hold, S-function input, ... ; capture off by up to 45 %).

The launchers keep writing the production names (the bundle cannot be changed: it is the library's frozen runner).
`install(eng)` looks at the engine the job runs (`flavour`) and, for this repository's engine, mirrors every NUCLIDO_*
switch in SWITCHES to its INCOGNITA_* name on every set and delete of os.environ (including the bundle's
os.environ.clear()/update() per item), so the engine sees the production configuration under its own names. For the
production engine nothing changes.

The HF_* numerics switches have the same names in both engines; unprefixed variables (TALYS_DIR, CJ_FLOAT, RL_*,
ENGAUDIT_PATH, ...) are not engine switches of either engine. tests/test_engine_switch_names.py checks that every name
on the right of SWITCHES is read by physics/hf and that every NUCLIDO_* name a launcher of this repository mentions is in
SWITCHES."""
import os
import sys

PROD_PREFIX, REPO_PREFIX = "NUCLIDO_", "INCOGNITA_"

#: production engine switch -> this repository's engine switch.  Who sets it in the calculator / benchmark runs:
#:   J = engine_job.py (libv02/libv022 run.sh environment), P = bundle pprun.py (R83 fixes, FENV, --fewres/--pewindow),
#:   R = bundle r52pool.py (collective-E2 hold rule, item env), E = bundle engine_pool.py (worker set-up),
#:   F = the engine's own fitlib.ENV_LINES_FILE (already the engine's name; listed for completeness), D = docs only.
SWITCHES = {
    "NUCLIDO_GGDEADEND": "INCOGNITA_GGDEADEND",              # J
    "NUCLIDO_NGNEXCL": "INCOGNITA_NGNEXCL",                  # J (also read by native/engine_decay.c)
    "NUCLIDO_DWBAUNIT": "INCOGNITA_DWBAUNIT",                # J, R (OFF twins unset it per item)
    "NUCLIDO_LEVCOMPLETE": "INCOGNITA_LEVCOMPLETE",          # J
    "NUCLIDO_BANDCHECK": "INCOGNITA_BANDCHECK",              # J
    "NUCLIDO_TRAPFIX": "INCOGNITA_TRAPFIX",                  # J (also read by native/nativex.c)
    "NUCLIDO_WFCNORM": "INCOGNITA_WFCNORM",                  # J
    "NUCLIDO_CC_CACHE": "INCOGNITA_CC_CACHE",                # J (row cache; see install(skip=...))
    "NUCLIDO_TALYS_FIT": "INCOGNITA_TALYS_FIT",              # J, E
    "NUCLIDO_ENGPHYS": "INCOGNITA_ENGPHYS",                  # J, E
    "NUCLIDO_SPECOUT_DA": "INCOGNITA_SPECOUT_DA",            # J, P
    "NUCLIDO_GRIDTOP": "INCOGNITA_GRIDTOP",                  # D (not in 16606b356d6e; default on in later engines)
    "NUCLIDO_TRITFID": "INCOGNITA_TRITFID",                  # P (R83)
    "NUCLIDO_RESISO": "INCOGNITA_RESISO",                    # P
    "NUCLIDO_CCSOCB": "INCOGNITA_CCSOCB",                    # P
    "NUCLIDO_MPEFIX": "INCOGNITA_MPEFIX",                    # P
    "NUCLIDO_CPINC2": "INCOGNITA_CPINC2",                    # P
    "NUCLIDO_SPECOUT": "INCOGNITA_SPECOUT",                  # P
    "NUCLIDO_LEVJ": "INCOGNITA_LEVJ",                        # P
    "NUCLIDO_C6FIX": "INCOGNITA_C6FIX",                      # P
    "NUCLIDO_TLOGIT": "INCOGNITA_TLOGIT",                    # P
    "NUCLIDO_SFUNC": "INCOGNITA_SFUNC",                      # P (FENV)
    "NUCLIDO_SFUNC_TABLE": "INCOGNITA_SFUNC_TABLE",          # P
    "NUCLIDO_SFUNC_SCOPE": "INCOGNITA_SFUNC_SCOPE",          # P
    "NUCLIDO_FEWRES": "INCOGNITA_FEWRES",                    # P (--fewres)
    "NUCLIDO_PEWINDOW": "INCOGNITA_PEWINDOW",                # P (--pewindow)
    "NUCLIDO_ISOE2": "INCOGNITA_ISOE2",                      # R
    "NUCLIDO_ISOE2_K": "INCOGNITA_ISOE2_K",                  # R
    "NUCLIDO_ISOHOLD": "INCOGNITA_ISOHOLD",                  # R
    "NUCLIDO_SPINQUENCH": "INCOGNITA_SPINQUENCH",            # R
    "NUCLIDO_M1SHARE": "INCOGNITA_M1SHARE",                  # R
    "NUCLIDO_TALYS_FIT_LINES": "INCOGNITA_TALYS_FIT_LINES",  # R, E
    "NUCLIDO_TALYS_FIT_LINES_FILE": "INCOGNITA_TALYS_FIT_LINES_FILE",  # F
    "NUCLIDO_DIRCAP": "INCOGNITA_DIRCAP",                    # E (ENGPHYS dircap)
    "NUCLIDO_SOUKHO_EFCLAMP": "INCOGNITA_SOUKHO_EFCLAMP",    # E (ENGPHYS efermi)
    "NUCLIDO_DEF_EVENEVEN": "INCOGNITA_DEF_EVENEVEN",        # E (ENGPHYS oddodd)
    "NUCLIDO_PESPIN_NORM": "INCOGNITA_PESPIN_NORM",          # E (ENGPHYS pespin)
}
#: this repository's name -> production name (for checks; the launchers write production names)
REVERSE = {v: k for k, v in SWITCHES.items()}

#: files of an engine checkout that read switches; whichever prefix they use is the engine's flavour
_PROBES = ("physics/hf/structure/ggdeadend.py", "physics/hf/ecis/ccdisk.py", "physics/hf/engphys.py")


def flavour(eng):
    """'repo' (INCOGNITA_* switches, this repository's engine) or 'production' (NUCLIDO_*, build 16606b356d6e and its
    nucleus siblings) for the engine checkout `eng`. TW_ENG_FLAVOUR=repo|production overrides. Raises when it cannot tell
    (a launcher must not guess: a wrong guess silently drops every switch)."""
    f = os.environ.get("TW_ENG_FLAVOUR", "").strip().lower()
    if f in ("repo", "production"):
        return f
    n = {"repo": 0, "production": 0}
    for rel in _PROBES:
        try:
            src = open(os.path.join(eng, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        n["repo"] += src.count('"' + REPO_PREFIX)
        n["production"] += src.count('"' + PROD_PREFIX)
    if n["repo"] and not n["production"]:
        return "repo"
    if n["production"] and not n["repo"]:
        return "production"
    raise RuntimeError(f"engine_env.flavour: cannot tell the switch names of engine {eng!r} ({n}); "
                       "set TW_ENG_FLAVOUR=repo|production")


def translate(env, skip=()):
    """{production name: value} -> the same switches under this repository's names (unmapped names dropped)."""
    return {SWITCHES[k]: v for k, v in env.items() if k in SWITCHES and k not in skip}


_warned = set()


def _target(k, skip):
    if not k.startswith(PROD_PREFIX) or k in skip:
        return None
    t = SWITCHES.get(k)
    if t is None and k not in _warned:
        _warned.add(k)
        sys.stderr.write(f"engine_env: {k} has no INCOGNITA_ equivalent in engine_env.SWITCHES; "
                         "this repository's engine ignores it\n")
    return t


def _mirror_class(base, skip):
    class _Mirror(base):
        """os.environ that writes every mapped NUCLIDO_* switch under its INCOGNITA_* name too (set and delete)."""
        _skip = frozenset(skip)

        def __setitem__(self, k, v):
            super().__setitem__(k, v)
            t = _target(k, self._skip)
            if t is not None:
                super().__setitem__(t, v)

        def __delitem__(self, k):
            super().__delitem__(k)
            t = _target(k, self._skip)
            if t is not None:
                try:
                    super().__delitem__(t)
                except KeyError:
                    pass
    return _Mirror


def clear_switches():
    """Remove every engine switch of either flavour from os.environ (a job starts from the run environment only)."""
    for k in [k for k in os.environ if k.startswith((PROD_PREFIX, REPO_PREFIX))]:
        del os.environ[k]


def install(eng, skip=()):
    """Make os.environ carry the production-named switches to engine `eng` under the names it reads. Returns the flavour.
    For 'repo' the existing NUCLIDO_* switches are mirrored now and every later set / delete is mirrored (in this process
    and in its forks; subprocesses inherit the mirrored variables). `skip`: production names NOT to mirror (the launcher
    sets an alternative itself). Idempotent."""
    f = flavour(eng)
    if f != "repo":
        return f
    base = type(os.environ)
    if getattr(base, "_skip", None) is not None:  # already installed
        base = base.__mro__[1]
    os.environ.__class__ = _mirror_class(base, skip)
    for k, v in list(os.environ.items()):
        t = _target(k, frozenset(skip))
        if t is not None:
            os.environ[t] = v
    return f
