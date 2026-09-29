"""Stage B parameter space for the TALYS capture sweep (BLUEPRINT §5.3, option 2).

Every parameter below maps onto TALYS-2.25 input keywords that were verified
against the source tree (``$TALYS_DIR/source/input_*.f90`` and
``getvalues.f90``; see :func:`keyword_exists_in_source` and
``tests/test_sweep_params.py``) **and** empirically checked to change the
197Au(n,γ) cross section (or to be inert by design, as noted).

Parameter vector (index, name, prior, TALYS keywords emitted)
-------------------------------------------------------------
Categorical parameters are sampled uniformly over their ``choices``; continuous
ones are uniform in the *coded* variable ``x`` given below.  ``log2`` priors
mean the physical factor is ``2**x`` with ``x ~ U[log2(lo), log2(hi)]``, i.e.
log-uniform on ``[lo, hi]`` as prescribed for multiplicative adjust factors.

=====  ==================  ===========================  =====================================
idx    name                prior (coded x)              TALYS keyword(s)
=====  ==================  ===========================  =====================================
0      ldmodel             cat {1,2,3,4,5,6}            ``ldmodel <k>`` (+``legacy y`` if k=3,4,6)
1      ld_a_factor         log2, factor in [0.5, 2]     ``aadjust Z A f`` for CN and target
2      ld_pshift_mev       uniform [-1, 1] MeV          ``pshiftadjust Z A s`` (ldmodel<=3)
                                                        ``ptableadjust Z A s`` (ldmodel>=4)
3      ld_spincut_factor   log2, factor in [0.5, 2]     ``rspincut f`` (global)
4      strength            cat {1,2,8,9}                ``strength <k>`` (+ ``legacy y`` if k<=7)
5      gsf_norm            log2, factor in [0.5, 2]     ``sgradjust Z A f E1`` (strength 1-2)
                                                        ``ftable   Z A f E1`` (strength>=3)
6      gsf_eshift_mev      uniform [-1, 1] MeV          ``egradjust Z A (1+s/E_GDR) E1`` (1-2)
                                                        ``etable   Z A s E1`` (strength>=3)
7      gsf_width_factor    log2, factor in [0.5, 2]     ``ggradjust Z A f E1`` (1-2)
                                                        ``wtable   Z A f E1`` (strength>=3)
8      omp_rv_factor       log2, factor in [0.95,1.05]  ``rvadjust n f``
9      omp_av_factor       log2, factor in [0.8, 1.25]  ``avadjust n f``
10     omp_w1_factor       log2, factor in [0.5, 2]     ``w1adjust n f``
11     omp_v1_factor       log2, factor in [0.95,1.05]  ``v1adjust n f``
=====  ==================  ===========================  =====================================

``Z A`` above is the compound nucleus (Z, A+1) for the gamma-strength keywords
(the nucleus that emits the capture gammas) and both the compound nucleus and
the target for the level-density keywords (the target level density drives
the inelastic continuum).  ``Sn`` of the compound nucleus is *not* a TALYS
input (TALYS takes it from its own mass table) but is stored alongside every
run, from ``staging/nuclides.parquet`` (AME2020), as a surrogate feature.

Design notes / traps found in TALYS-2.25
----------------------------------------
* ``deltaadjust`` does not exist; the pairing-shift knob is ``pshift``
  (absolute) / ``pshiftadjust`` (additive correction, MeV).  For the
  tabulated microscopic level densities (``ldmodel`` 4-6) the equivalent
  shift is ``ptable`` / ``ptableadjust``; ``aadjust`` is inert there.
* ``gadjust`` is the *pre-equilibrium* single-particle level-density ``g``
  factor (``input_preeqpar.f90``), not a gamma knob.
* ``gamgamadjust Z A f`` is parsed (``input_gammapar.f90``) and applied in
  ``resonancepar.f90:113``, but the only consumer of Γγ is the ``gnorm y``
  normalisation loop in ``radwidtheory.f90:253``; with the default
  ``gnorm n`` it changes nothing, and in our tests it changed nothing under
  ``gnorm y`` either (197Au, factors 0.5 and 2) -- GNORMFIX (2026-09-17): because
  stock TALYS normalises to the .res keV number read as eV, the loop never
  converges (C/E Gamma_gamma 277-555) and stops at the same ftable whatever the
  factor.  ``runner.write_input`` now adds ``gamgam Z A <eV>`` under ``gnorm y``,
  after which ``gamgamadjust`` acts as documented.  ``gnorm y`` also costs up
  to 10x runtime.  We therefore expose the Γγ knob as ``gsf_norm``: TALYS's
  own normalisation to Γγ is implemented as a rescaling of ``ftable``
  (``radwidtheory.f90:255``), so scaling the E1 strength *is* scaling Γγ.
  Direct ``gamgam Z A <eV>`` + ``gnorm y`` is still available through
  :func:`gamgam_keywords` for calibration runs, but is not part of the sweep.
* GDR-parameter keywords are "class 5" in ``getvalues.f90`` and need the
  multipole token: ``sgradjust 79 198 2.0 E1``.  Without it TALYS aborts with
  "Error in sgradjust / End of file".
* Under the default ``strength 9`` (SMLO) and every other tabulated model
  (3, 4, 6-13), ``sgradjust/egradjust/ggradjust`` are inert; the tabulated
  strength is adjusted with ``ftable`` (multiplicative), ``etable`` (energy
  shift, MeV) and ``wtable`` (width factor) — see ``gammapar.f90:259-566``.
  Analytic models 1 (Kopecky-Uhl) and 2 (Brink-Axel) use the ``*gradjust``
  family and require ``legacy y`` (``checkvalue.f90:804``), as do
  ``ldmodel`` 3, 4 and 6 (``checkvalue.f90:953``); ``legacy`` is only used
  in ``checkvalue.f90``, so it has no other physics side effect.
* ``rvadjust n 1.1`` produced a pathological capture value (1e-7 mb at 1
  MeV on 197Au) while 0.95-1.05 behaved smoothly, hence the narrow prior on
  the OMP radius and real-depth factors.
* Value ranges enforced by ``checkvalue.f90``: ``aadjust`` 0.1-10,
  ``rvadjust/avadjust/w1adjust`` 0.1-10, ``Rspincut`` 0-10, ``sgradjust``
  and friends 0.05-20, ``ldmodel`` 1-7 (7 = BSkG3, new in 2.2x and not
  swept), ``strength`` 1-13.
"""

from __future__ import annotations

import functools
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Parameter definitions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Param:
    name: str
    kind: str  # "cat" | "log2" | "uniform"
    lo: float = 0.0  # coded lower bound (for log2: log2 of the physical lower bound)
    hi: float = 1.0
    choices: tuple[int, ...] = ()
    doc: str = ""

    @property
    def coded_bounds(self) -> tuple[float, float]:
        if self.kind == "cat":
            return (0.0, float(len(self.choices)))
        return (self.lo, self.hi)

    def decode(self, x: float):
        """Coded value -> physical value (int for categorical)."""
        if self.kind == "cat":
            i = int(min(len(self.choices) - 1, max(0, int(np.floor(x)))))
            return int(self.choices[i])
        if self.kind == "log2":
            return float(2.0**x)
        return float(x)

    def encode(self, v) -> float:
        """Physical value -> coded value (categoricals map to their bin centre)."""
        if self.kind == "cat":
            return float(self.choices.index(int(v))) + 0.5
        if self.kind == "log2":
            return float(np.log2(v))
        return float(v)

    def default_coded(self) -> float:
        """Coded value of the TALYS default (factor 1, shift 0, default model)."""
        if self.kind == "cat":
            return self.encode(TALYS_DEFAULTS[self.name])
        if self.kind == "log2":
            return 0.0
        return 0.0


# TALYS-2.25 defaults (input_densitymodel.f90: ldmodelall = 1, strength = 9).
TALYS_DEFAULTS: dict[str, int] = {"ldmodel": 1, "strength": 9}

LD_MODELS = (1, 2, 3, 4, 5, 6)
# checkvalue.f90:953-966 - ldmodel 3, 4, 6 abort unless ``legacy y`` (as do strength <= 7).
LEGACY_LD_MODELS = (3, 4, 6)
STRENGTH_MODELS = (1, 2, 8, 9)  # KU, BA (legacy analytic), Gogny D1M, SMLO (default)

PARAMS: tuple[Param, ...] = (
    Param("ldmodel", "cat", choices=LD_MODELS, doc="level-density model"),
    Param("ld_a_factor", "log2", -1.0, 1.0, doc="aadjust factor on a (CN + target)"),
    Param("ld_pshift_mev", "uniform", -1.0, 1.0, doc="pairing-shift correction, MeV"),
    Param("ld_spincut_factor", "log2", -1.0, 1.0, doc="rspincut global spin-cutoff factor"),
    Param("strength", "cat", choices=STRENGTH_MODELS, doc="E1 gamma-strength model"),
    Param("gsf_norm", "log2", -1.0, 1.0, doc="E1 strength normalisation (Γγ-equivalent)"),
    Param("gsf_eshift_mev", "uniform", -1.0, 1.0, doc="E1 strength energy shift, MeV"),
    Param("gsf_width_factor", "log2", -1.0, 1.0, doc="E1 strength width factor"),
    Param("omp_rv_factor", "log2", np.log2(0.95), np.log2(1.05), doc="rvadjust n"),
    Param("omp_av_factor", "log2", np.log2(0.8), np.log2(1.25), doc="avadjust n"),
    Param("omp_w1_factor", "log2", -1.0, 1.0, doc="w1adjust n"),
    Param("omp_v1_factor", "log2", np.log2(0.95), np.log2(1.05), doc="v1adjust n"),
)
PARAM_NAMES: tuple[str, ...] = tuple(p.name for p in PARAMS)
N_PARAMS = len(PARAMS)
PARAM_INDEX: dict[str, int] = {p.name: i for i, p in enumerate(PARAMS)}

CONTINUOUS_NAMES = tuple(p.name for p in PARAMS if p.kind != "cat")
CATEGORICAL_NAMES = tuple(p.name for p in PARAMS if p.kind == "cat")


def coded_bounds() -> tuple[np.ndarray, np.ndarray]:
    lo = np.array([p.coded_bounds[0] for p in PARAMS])
    hi = np.array([p.coded_bounds[1] for p in PARAMS])
    return lo, hi


def default_coded_vector() -> np.ndarray:
    """Coded vector reproducing a plain TALYS default run (sample_id 0)."""
    return np.array([p.default_coded() for p in PARAMS], dtype=float)


def decode(x: np.ndarray) -> dict[str, float | int]:
    """Coded vector (len N_PARAMS) -> {name: physical value}."""
    x = np.asarray(x, dtype=float)
    if x.shape != (N_PARAMS,):
        raise ValueError(f"expected coded vector of length {N_PARAMS}, got {x.shape}")
    return {p.name: p.decode(v) for p, v in zip(PARAMS, x, strict=True)}


def encode(values: dict[str, float | int]) -> np.ndarray:
    """{name: physical value} -> coded vector; missing names take the TALYS default."""
    out = default_coded_vector()
    for k, v in values.items():
        out[PARAM_INDEX[k]] = PARAMS[PARAM_INDEX[k]].encode(v)
    return out


# ---------------------------------------------------------------------------
# Keyword generation
# ---------------------------------------------------------------------------


def gdr_energy_systematics(A: int) -> float:
    """E1 GDR centroid systematics used by TALYS/RIPL, MeV: 31.2 A^-1/3 + 20.6 A^-1/6."""
    return 31.2 * A ** (-1.0 / 3.0) + 20.6 * A ** (-1.0 / 6.0)


def _f(v: float) -> str:
    return f"{v:.6g}"


def to_keywords(x: np.ndarray, Z: int, A: int, *, projectile: str = "n") -> dict[str, str]:
    """Translate a coded parameter vector into TALYS ``keyword value`` pairs.

    ``Z, A`` are the *target*; gamma-strength adjustments go on the compound
    nucleus (Z, A+1), level-density adjustments on both.  Returns an ordered
    dict suitable for ``runner.run_talys(..., extra_keywords=...)``.  Keys
    that must appear more than once (``aadjust`` for two nuclei) are
    disambiguated with a ``#n`` suffix that :func:`keyword_lines` strips.
    """
    v = decode(x)
    if projectile != "n":
        raise ValueError("parameter space is defined for neutron-induced reactions only")
    Zc, Ac = Z, A + 1
    kw: dict[str, str] = {}

    # --- level density -------------------------------------------------
    ld = int(v["ldmodel"])
    kw["ldmodel"] = str(ld)
    if ld in LEGACY_LD_MODELS:
        kw["legacy"] = "y"
    af = v["ld_a_factor"]
    if abs(af - 1.0) > 1e-9:
        kw["aadjust#cn"] = f"{Zc} {Ac} {_f(af)}"
        kw["aadjust#tg"] = f"{Z} {A} {_f(af)}"
    ps = v["ld_pshift_mev"]
    if abs(ps) > 1e-9:
        key = "pshiftadjust" if ld <= 3 else "ptableadjust"
        kw[f"{key}#cn"] = f"{Zc} {Ac} {_f(ps)}"
        kw[f"{key}#tg"] = f"{Z} {A} {_f(ps)}"
    sc = v["ld_spincut_factor"]
    if abs(sc - 1.0) > 1e-9:
        kw["rspincut"] = _f(sc)

    # --- gamma strength --------------------------------------------------
    st = int(v["strength"])
    kw["strength"] = str(st)
    if st <= 7:
        kw["legacy"] = "y"
    analytic = st in (1, 2)
    gn, ge, gw = v["gsf_norm"], v["gsf_eshift_mev"], v["gsf_width_factor"]
    if abs(gn - 1.0) > 1e-9:
        kw["sgradjust" if analytic else "ftable"] = f"{Zc} {Ac} {_f(gn)} E1"
    if abs(ge) > 1e-9:
        if analytic:
            kw["egradjust"] = f"{Zc} {Ac} {_f(1.0 + ge / gdr_energy_systematics(Ac))} E1"
        else:
            kw["etable"] = f"{Zc} {Ac} {_f(ge)} E1"
    if abs(gw - 1.0) > 1e-9:
        kw["ggradjust" if analytic else "wtable"] = f"{Zc} {Ac} {_f(gw)} E1"

    # --- optical model (neutron channel) ----------------------------------
    for name, key in (
        ("omp_rv_factor", "rvadjust"),
        ("omp_av_factor", "avadjust"),
        ("omp_w1_factor", "w1adjust"),
        ("omp_v1_factor", "v1adjust"),
    ):
        f = v[name]
        if abs(f - 1.0) > 1e-9:
            kw[key] = f"n {_f(f)}"
    return kw


def keyword_lines(kw: dict[str, str]) -> list[str]:
    """``{key[#tag]: value}`` -> ``["key value", ...]`` with the ``#tag`` suffix removed."""
    return [f"{k.split('#', 1)[0]} {v}" for k, v in kw.items()]


def gamgam_keywords(Z: int, A: int, gamgam_ev: float) -> dict[str, str]:
    """Direct Γγ (eV) for the compound nucleus via ``gnorm y`` (calibration use only)."""
    return {"gnorm": "y", "gamgam": f"{Z} {A + 1} {_f(gamgam_ev)}"}


# ---------------------------------------------------------------------------
# Source verification (used by tests and by sweep start-up)
# ---------------------------------------------------------------------------

ALL_KEYWORDS_USED: tuple[str, ...] = (
    "ldmodel",
    "aadjust",
    "pshiftadjust",
    "ptableadjust",
    "rspincut",
    "strength",
    "legacy",
    "sgradjust",
    "egradjust",
    "ggradjust",
    "ftable",
    "etable",
    "wtable",
    "rvadjust",
    "avadjust",
    "w1adjust",
    "v1adjust",
    "gnorm",
    "gamgam",
    # speed / output keywords used by the sweep
    "channels",
    "filechannels",
    "filetotal",
    "fileelastic",
    "outbasic",
    "outdiscrete",
    "outspectra",
    "outgamdis",
    "bins",
    "maxlevelstar",
    "preequilibrium",
    "maxZ",
    "maxN",
)


def talys_source_dir() -> Path | None:
    from physics.talys.runner import talys_dir

    d = talys_dir() / "source"
    return d if d.is_dir() else None


@functools.lru_cache(maxsize=1)
def _source_keyword_index() -> frozenset[str] | None:
    """Set of every ``'keyword'`` literal in the TALYS input parsers + getvalues (cached)."""
    src = talys_source_dir()
    if src is None:
        return None
    pat = re.compile(r"'([a-z0-9]+)'")
    found: set[str] = set()
    for f in list(src.glob("input_*.f90")) + [src / "getvalues.f90"]:
        if f.is_file():
            found.update(pat.findall(f.read_text(errors="replace")))
    return frozenset(found)


def keyword_exists_in_source(keyword: str) -> bool | None:
    """True/False if the TALYS source is available, None if it is not."""
    idx = _source_keyword_index()
    if idx is None:
        return None
    return keyword.lower() in idx


def verify_keywords(keywords=ALL_KEYWORDS_USED) -> list[str]:
    """Return the keywords *not* found in the TALYS source (empty list = all good)."""
    return [k for k in keywords if keyword_exists_in_source(k) is False]
