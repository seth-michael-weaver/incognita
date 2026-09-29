"""Differential validation harness (WP-16; blueprint §6.1, §6.3, §4.4, §12).

Scores any prediction of σ(E) — a WP-15 checkpoint, a TALYS run, the surrogate, or an
evaluated library treated *as if* it were a prediction — against

(a) each evaluated library on the common log-energy grid, with the resolved-resonance
    region excluded by the library's own RRR upper bound (a smooth model cannot and should
    not reproduce a resonance ladder), reported separately for the URR and the fast/smooth
    region;
(b) the WP-12 EXFOR consensus bins (trust-weighted and unweighted), or the per-dataset
    cells behind them when a publication-year cutoff is requested (time-split
    retrodiction: only measurements published *after* the cutoff are scored);
(c) Maxwellian-averaged cross sections MACS(kT) folded from σ(E), against KADoNiS v1.0.

Metrics per (nuclide, MT[, region]): log10 RMS, median |log10 ratio|, median relative
error, log10 bias, χ² per degree of freedom (with the MF33 relative covariance of the
reference library where a block exists, diagonal otherwise), and 1σ / 2σ coverage of the
prediction's stated uncertainty. Everything aggregates by mass region and by the WP-05
region-holdout manifests.

The prediction contract (`Prediction`, `PredictionSet.from_parquet`) is what WP-15's
``predict.py`` must write: one row per (nuclide_id, mt) with ``energy_ev``, ``sigma_b`` and
optionally ``sigma_unc_b`` list columns, or ``grid_id`` = the common grid and ``sigma_b``
of length 3000.
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import polars as pl

from physics.grid import ENERGY_GRID_EV, GRID_ID
from validation import cache as C

REPO = C.REPO
CACHE = C.CACHE
LIBRARIES = C.LIBRARIES
KADONIS_MACS = REPO / "raw" / "kadonis" / "kadonis1.0_macs.tsv"
MANIFEST_DIR = REPO / "data" / "splits" / "manifests"
SWEEP_DIR = REPO / "features" / "talys_sweep" / "shards"
SURROGATE_CKPT = REPO / "models" / "surrogate" / "checkpoints" / "talys-surrogate-v0.pt"

_NUC_RE = re.compile(r"^Z(\d{3})N(\d{3})M(\d)$")
LOG10E = math.log10(math.e)
MASS_REGIONS: tuple[str, ...] = ("light", "Fe-Sn", "Sn-Pb", "actinide")
REGIONS: tuple[str, ...] = ("above_rrr", "urr", "fast")
EXFOR_KINDS: tuple[str, ...] = ("sig", "av")

# Every filter in the harness records what it dropped. A silent filter is indistinguishable
# from a correct one (docs/failure-modes.md, "What actually catches these", item 4), and both
# selections below can quietly remove a fifth of the scoring set: the EXFOR selection drops
# whole quantity kinds, and ``compare_to_exfor`` drops every bin the prediction does not
# reach. The tallies go to stderr (stdout is where the scripts put their tables) and the last
# one of each is kept here so a caller or a test can assert on it instead of parsing text.
VERBOSE_DROPS: bool = True
LAST_EXFOR_LOAD_DROPS: dict[str, int | float | str] = {}
LAST_EXFOR_SCORE_DROPS: dict[str, int | float | str] = {}


def _tally(msg: str) -> None:
    if VERBOSE_DROPS:
        print(msg, file=sys.stderr)


# ----------------------------------------------------------------------------- nuclide helpers


def parse_nuclide_id(nuclide_id: str) -> tuple[int, int, int]:
    m = _NUC_RE.match(nuclide_id)
    if m is None:
        raise ValueError(f"not a canonical nuclide id: {nuclide_id!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def nuclide_id(Z: int, N: int, iso: int = 0) -> str:
    return f"Z{Z:03d}N{N:03d}M{iso}"


def mass_region(Z: int, A: int) -> str:
    """Blueprint §6.1 breakdown: light (Z < 26), Fe–Sn (26–50), Sn–Pb (51–82), actinide (> 82).

    Bi/Po/At/Rn/Fr/Ra (Z 83–88) are lumped with the actinides: they share the
    above-N=126 systematics, and the capture subset has no separate bin for them.
    """
    if Z < 26:
        return "light"
    if Z <= 50:
        return "Fe-Sn"
    if Z <= 82:
        return "Sn-Pb"
    return "actinide"


def region_holdouts(manifest_dir: Path = MANIFEST_DIR) -> dict[str, frozenset[str]]:
    """Test members of every ``region`` manifest of WP-05, keyed by split name."""
    index_path = manifest_dir / "manifests_index.json"
    if not index_path.is_file():
        return {}
    index = json.loads(index_path.read_text())["manifests"]
    out: dict[str, frozenset[str]] = {}
    for name, entry in index.items():
        if entry.get("kind") != "region" or entry.get("role") != "test":
            continue
        row = pl.read_parquet(manifest_dir / entry["file"]).row(0, named=True)
        split = name.removesuffix("_test")
        out[split] = frozenset(row["members"])
    return out


# ----------------------------------------------------------------------------- Prediction


def _loglog_interp(x_new: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """log-log interpolation, NaN outside [x.min, x.max] and where y <= 0 on both sides."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y) & (x > 0)
    x, y = x[ok], y[ok]
    out = np.full(len(x_new), np.nan)
    if x.size == 0:
        return out
    order = np.argsort(x)
    x, y = x[order], y[order]
    lx = np.log(x)
    lxn = np.log(np.asarray(x_new, float))
    inside = (lxn >= lx[0]) & (lxn <= lx[-1])
    pos = y > 0
    if pos.all():
        out[inside] = np.exp(np.interp(lxn[inside], lx, np.log(y)))
    else:
        out[inside] = np.interp(lxn[inside], lx, y)
    return out


@dataclass
class Prediction:
    """σ(E) of one (nuclide, MT): energies in eV (ascending), cross sections in barns.

    ``sigma_unc_b`` is the absolute 1σ uncertainty (None if the source has none).
    ``rrr_upper_ev`` / ``urr_upper_ev`` are the prediction's *own* resonance bounds when it
    comes from an evaluated library (0 otherwise); the comparators exclude the union of the
    prediction's and the reference's resolved ranges.
    """

    nuclide_id: str
    mt: int
    energy_ev: np.ndarray
    sigma_b: np.ndarray
    sigma_unc_b: np.ndarray | None = None
    rrr_upper_ev: float = 0.0
    urr_upper_ev: float = 0.0
    source: str = ""

    def __post_init__(self) -> None:
        self.energy_ev = np.asarray(self.energy_ev, dtype=np.float64)
        self.sigma_b = np.asarray(self.sigma_b, dtype=np.float64)
        if self.energy_ev.shape != self.sigma_b.shape or self.energy_ev.ndim != 1:
            raise ValueError("energy_ev and sigma_b must be 1-D and the same length")
        if self.sigma_unc_b is not None:
            self.sigma_unc_b = np.asarray(self.sigma_unc_b, dtype=np.float64)
            if self.sigma_unc_b.shape != self.sigma_b.shape:
                raise ValueError("sigma_unc_b must match sigma_b")
        if np.any(np.diff(self.energy_ev) < 0):
            order = np.argsort(self.energy_ev)
            self.energy_ev = self.energy_ev[order]
            self.sigma_b = self.sigma_b[order]
            if self.sigma_unc_b is not None:
                self.sigma_unc_b = self.sigma_unc_b[order]
        self.rrr_upper_ev = float(self.rrr_upper_ev or 0.0)
        self.urr_upper_ev = float(self.urr_upper_ev or 0.0)
        if not np.isfinite(self.rrr_upper_ev):
            self.rrr_upper_ev = 0.0
        if not np.isfinite(self.urr_upper_ev):
            self.urr_upper_ev = 0.0

    @property
    def ZNI(self) -> tuple[int, int, int]:
        return parse_nuclide_id(self.nuclide_id)

    @property
    def A(self) -> int:
        Z, N, _ = self.ZNI
        return Z + N

    @property
    def e_min_ev(self) -> float:
        ok = np.isfinite(self.sigma_b)
        return float(self.energy_ev[ok].min()) if ok.any() else math.nan

    @property
    def e_max_ev(self) -> float:
        ok = np.isfinite(self.sigma_b)
        return float(self.energy_ev[ok].max()) if ok.any() else math.nan

    def on_grid(self, grid: np.ndarray = ENERGY_GRID_EV) -> tuple[np.ndarray, np.ndarray | None]:
        """(σ, σ_unc) on ``grid`` (NaN outside the prediction's own range).

        Exact when the prediction already lives on the grid; log-log interpolation otherwise.
        """
        if self.energy_ev.shape == grid.shape and np.allclose(self.energy_ev, grid, rtol=1e-9):
            return self.sigma_b, self.sigma_unc_b
        s = _loglog_interp(grid, self.energy_ev, self.sigma_b)
        u = None
        if self.sigma_unc_b is not None:
            u = _loglog_interp(grid, self.energy_ev, self.sigma_unc_b)
        return s, u


class PredictionSet(Mapping[tuple[str, int], Prediction]):
    """A labelled collection of :class:`Prediction` keyed by (nuclide_id, mt)."""

    def __init__(
        self,
        preds: Iterable[Prediction] = (),
        *,
        label: str = "prediction",
        meta: dict | None = None,
    ):
        self._d: dict[tuple[str, int], Prediction] = {}
        for p in preds:
            self._d[(p.nuclide_id, p.mt)] = p
        self.label = label
        self.meta = dict(meta or {})

    def __getitem__(self, key: tuple[str, int]) -> Prediction:
        return self._d[key]

    def __iter__(self) -> Iterator[tuple[str, int]]:
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def add(self, p: Prediction) -> None:
        self._d[(p.nuclide_id, p.mt)] = p

    @property
    def nuclides(self) -> list[str]:
        return sorted({k[0] for k in self._d})

    @property
    def mts(self) -> list[int]:
        return sorted({k[1] for k in self._d})

    def subset(self, nuclides: Iterable[str] | None = None, mts: Iterable[int] | None = None):
        nset = None if nuclides is None else set(nuclides)
        mset = None if mts is None else set(mts)
        keep = [
            p
            for (n, mt), p in self._d.items()
            if (nset is None or n in nset) and (mset is None or mt in mset)
        ]
        return PredictionSet(keep, label=self.label, meta=self.meta)

    # ------------------------------------------------------------------ constructors

    @classmethod
    def from_parquet(cls, path: str | Path, *, label: str | None = None, mts=None):
        """The WP-15 contract.

        Columns: ``nuclide_id`` (str), ``mt`` (int), ``sigma_b`` (list[f64]); and either
        ``energy_ev`` (list[f64]) or ``grid_id == physics.grid.GRID_ID`` (values on the common
        grid). Optional: ``sigma_unc_b`` (list[f64], absolute 1σ), ``resolved_upper_ev``,
        ``unresolved_upper_ev``, ``source``. ``values_b`` is accepted as an alias of
        ``sigma_b`` so a WP-11 library slice is a valid prediction file.
        """
        path = Path(path)
        lf = pl.scan_parquet(path)
        cols = lf.collect_schema().names()
        if mts is not None:
            lf = lf.filter(pl.col("mt").is_in(list(mts)))
        df = lf.collect()
        val_col = "sigma_b" if "sigma_b" in cols else "values_b"
        if val_col not in cols:
            raise ValueError(f"{path}: needs a sigma_b (or values_b) column")
        has_e = "energy_ev" in cols
        if not has_e and "grid_id" not in cols:
            raise ValueError(f"{path}: needs energy_ev or grid_id")
        preds = []
        for r in df.iter_rows(named=True):
            if has_e:
                e = np.asarray(r["energy_ev"], float)
            else:
                if r["grid_id"] != GRID_ID:
                    raise ValueError(f"{path}: grid_id {r['grid_id']!r} is not {GRID_ID!r}")
                e = ENERGY_GRID_EV
            unc = r.get("sigma_unc_b")
            preds.append(
                Prediction(
                    nuclide_id=r["nuclide_id"],
                    mt=int(r["mt"]),
                    energy_ev=e,
                    sigma_b=np.asarray(r[val_col], float),
                    sigma_unc_b=None if unc is None else np.asarray(unc, float),
                    rrr_upper_ev=r.get("resolved_upper_ev") or 0.0,
                    urr_upper_ev=r.get("unresolved_upper_ev") or 0.0,
                    source=r.get("source") or path.name,
                )
            )
        return cls(preds, label=label or path.stem, meta={"path": str(path)})

    def to_parquet(self, path: str | Path) -> Path:
        """Write in the WP-15 contract layout (explicit energies; lossless round trip)."""
        rows = []
        for p in self._d.values():
            rows.append(
                {
                    "nuclide_id": p.nuclide_id,
                    "mt": p.mt,
                    "energy_ev": p.energy_ev.tolist(),
                    "sigma_b": p.sigma_b.tolist(),
                    "sigma_unc_b": None if p.sigma_unc_b is None else p.sigma_unc_b.tolist(),
                    "resolved_upper_ev": p.rrr_upper_ev,
                    "unresolved_upper_ev": p.urr_upper_ev,
                    "source": p.source or self.label,
                }
            )
        schema = {
            "nuclide_id": pl.Utf8,
            "mt": pl.Int16,
            "energy_ev": pl.List(pl.Float64),
            "sigma_b": pl.List(pl.Float64),
            "sigma_unc_b": pl.List(pl.Float64),
            "resolved_upper_ev": pl.Float64,
            "unresolved_upper_ev": pl.Float64,
            "source": pl.Utf8,
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        pl.DataFrame(rows, schema=schema).write_parquet(path)
        return path

    @classmethod
    def from_library(
        cls,
        key: str,
        *,
        mts: Iterable[int] = (102,),
        nuclides: Iterable[str] | None = None,
        with_uncertainty: bool = True,
    ):
        """An evaluated library as a prediction (RRR/URR bounds kept; MF33 diagonal as 1σ)."""
        lib = Library(key, mts=mts)
        preds = []
        nset = None if nuclides is None else set(nuclides)
        for mt in lib.mts:
            for nid in lib.nuclides(mt):
                if nset is not None and nid not in nset:
                    continue
                s, r_up, u_up = lib.curve(nid, mt)
                unc = None
                if with_uncertainty:
                    rel = lib.rel_unc_on_grid(nid, mt)
                    unc = None if rel is None else rel * s
                preds.append(
                    Prediction(nid, mt, ENERGY_GRID_EV, s, unc, r_up, u_up, source=lib.name)
                )
        return cls(preds, label=lib.name, meta={"library": key, "version": lib.version})

    @classmethod
    def from_callable(
        cls,
        fn: Callable[[str, int, np.ndarray], np.ndarray | tuple[np.ndarray, np.ndarray]],
        nuclides: Iterable[str],
        *,
        mts: Iterable[int] = (102,),
        grid: np.ndarray = ENERGY_GRID_EV,
        label: str = "callable",
    ):
        """``fn(nuclide_id, mt, energy_ev) -> sigma_b`` or ``(sigma_b, sigma_unc_b)``."""
        preds = []
        for nid in nuclides:
            for mt in mts:
                out = fn(nid, mt, grid)
                if isinstance(out, tuple):
                    s, u = out
                else:
                    s, u = out, None
                preds.append(Prediction(nid, mt, grid, s, u, source=label))
        return cls(preds, label=label)

    @classmethod
    def from_talys_default(cls, sweep_dir: Path = SWEEP_DIR, *, channel: str = "capture"):
        """sample_id == 0 rows of the WP-13 sweep: TALYS with all defaults (log10 mb → b)."""
        mt = {
            "capture": 102,
            "total": 1,
            "elastic": 2,
            "inelastic": 4,
            "n2n": 16,
            "np": 103,
            "na": 107,
        }[channel]
        shards = sorted(Path(sweep_dir).glob("*.parquet"))
        if not shards:
            raise FileNotFoundError(f"no sweep shards under {sweep_dir}")
        df = (
            pl.scan_parquet(shards)
            .filter((pl.col("sample_id") == 0) & (pl.col("status") == "ok"))
            .select("Z", "A", "E_mev", f"log10_xs_{channel}")
            .collect()
        )
        preds = []
        for r in df.iter_rows(named=True):
            e = np.asarray(r["E_mev"], float) * 1e6
            s = 10.0 ** np.asarray(r[f"log10_xs_{channel}"], float) * 1e-3
            preds.append(
                Prediction(
                    nuclide_id(r["Z"], r["A"] - r["Z"]),
                    mt,
                    e,
                    s,
                    source="TALYS default (sweep sample 0)",
                )
            )
        return cls(preds, label="TALYS-default", meta={"sweep_dir": str(sweep_dir)})

    @classmethod
    def from_surrogate(
        cls,
        checkpoint: Path = SURROGATE_CKPT,
        *,
        nuclides: Iterable[tuple[int, int, float]] | None = None,
        channel: str = "capture",
        e_min_ev: float = 1e3,
        e_max_ev: float = 20e6,
        grid: np.ndarray = ENERGY_GRID_EV,
        device: str = "cpu",
        gsf_norm: float | dict[str, float] | None = None,
    ):
        """The WP-13 surrogate at the TALYS-default parameter vector.

        ``gsf_norm`` moves the prior off the TALYS default for the photon strength function --
        a scalar, or a dict keyed by nuclide id for a per-nuclide value. The default (None)
        leaves the coded vector alone, which is gsf_norm = 1.0.

        This exists because the default is measurably wrong.
        ``docs/results/psf-normalisation.md`` infers 1.347 (95% CI [1.120, 1.484]) from the
        measured-to-default capture ratio over 191 nuclides, validated against measured
        Gamma_gamma. TALYS's photon strength function is the ingredient only capture uses, and
        capture and (n,2n) prior biases are uncorrelated (r = -0.021), so a shared ingredient is
        not where the remaining error is.

        ``nuclides`` = (Z, N, Sn_of_compound_keV); default = the 40 sweep nuclides
        (Sn taken from the sweep rows). Energies outside [e_min, e_max] are NaN: the
        surrogate was trained on 1 keV–20 MeV only.
        """
        from models.surrogate.mlp import CHANNELS, SurrogateBundle
        from physics.talys import params as P

        if nuclides is None:
            shards = sorted(SWEEP_DIR.glob("*.parquet"))
            df = (
                pl.scan_parquet(shards)
                .filter(pl.col("sample_id") == 0)
                .select("Z", "N", "sn_cn_kev")
                .unique()
                .collect()
            )
            nuclides = [(int(z), int(n), float(s)) for z, n, s in df.iter_rows()]
        nuclides = list(nuclides)
        bundle = SurrogateBundle.load(checkpoint, device=device)
        mask = (grid >= e_min_ev) & (grid <= e_max_ev)
        log10_e_mev = np.log10(grid[mask] * 1e-6)
        Z = np.array([n[0] for n in nuclides])
        N = np.array([n[1] for n in nuclides])
        sn = np.array([n[2] for n in nuclides])
        coded = np.repeat(P.default_coded_vector()[None, :], len(Z), axis=0)
        if gsf_norm is not None:
            # coded is log2(physical) for this parameter: decode(0)=1, decode(1)=2
            j = P.PARAM_INDEX["gsf_norm"]
            lo, hi = P.PARAMS[j].coded_bounds
            if isinstance(gsf_norm, dict):
                vals = np.array([gsf_norm.get(f"Z{z:03d}N{n:03d}M0", 1.0)
                                 for z, n in zip(Z, N, strict=True)], float)
            else:
                vals = np.full(len(Z), float(gsf_norm))
            coded[:, j] = np.clip(np.log2(np.clip(vals, 1e-6, None)), lo, hi)
        out = bundle.predict_curves(Z, N, sn, coded, log10_e_mev)  # (n, nE, channels)
        ch = CHANNELS.index(channel)
        mt = {
            "capture": 102,
            "total": 1,
            "elastic": 2,
            "inelastic": 4,
            "n2n": 16,
            "np": 103,
            "na": 107,
        }[channel]
        preds = []
        for i in range(len(Z)):
            s = np.full(len(grid), np.nan)
            s[mask] = 10.0 ** out[i, :, ch] * 1e-3
            preds.append(
                Prediction(
                    nuclide_id(int(Z[i]), int(N[i])),
                    mt,
                    grid,
                    s,
                    source=f"surrogate {Path(checkpoint).name} @ TALYS default",
                )
            )
        return cls(
            preds, label=f"surrogate:{Path(checkpoint).stem}", meta={"checkpoint": str(checkpoint)}
        )


# ----------------------------------------------------------------------------- Library


class Library:
    """One evaluated library's cached grid values, bounds and MF33 blocks for a set of MTs."""

    def __init__(self, key: str, *, mts: Iterable[int] = (102,)):
        if key not in LIBRARIES:
            raise KeyError(f"unknown library {key!r}; known: {sorted(LIBRARIES)}")
        self.key = key
        self.name = LIBRARIES[key]
        self.mts = sorted(set(int(m) for m in mts))
        self._xs: dict[int, pl.DataFrame] = {}
        self._cov: dict[int, dict[str, tuple[np.ndarray, np.ndarray]]] = {}
        self.version = ""
        for mt in self.mts:
            path = C.cache_library_xs(key, mt)
            df = pl.read_parquet(path)
            self._xs[mt] = df
            if df.height and not self.version:
                self.version = str(df["library_version"][0])
        self._index: dict[tuple[str, int], int] = {}
        for mt, df in self._xs.items():
            for i, nid in enumerate(df["nuclide_id"].to_list()):
                self._index[(nid, mt)] = i

    def nuclides(self, mt: int = 102) -> list[str]:
        return self._xs[mt]["nuclide_id"].to_list()

    def has(self, nid: str, mt: int) -> bool:
        return (nid, mt) in self._index

    def curve(self, nid: str, mt: int) -> tuple[np.ndarray, float, float]:
        """(σ on the common grid, resolved_upper_ev, unresolved_upper_ev)."""
        i = self._index[(nid, mt)]
        row = self._xs[mt].row(i, named=True)
        r = row["resolved_upper_ev"] or 0.0
        u = row["unresolved_upper_ev"] or 0.0
        return np.asarray(row["values_b"], float), float(r), float(u)

    def bounds(self, nid: str, mt: int) -> tuple[float, float]:
        i = self._index[(nid, mt)]
        row = self._xs[mt].row(i, named=True)
        return float(row["resolved_upper_ev"] or 0.0), float(row["unresolved_upper_ev"] or 0.0)

    def _load_cov(self, mt: int) -> dict[str, tuple[np.ndarray, np.ndarray]]:
        if mt not in self._cov:
            out: dict[str, tuple[np.ndarray, np.ndarray]] = {}
            path = C.cache_library_cov(self.key, mt)
            for r in pl.read_parquet(path).iter_rows(named=True):
                n = int(r["n_bins"])
                cov = np.asarray(r["rel_cov"], float).reshape(n, n)
                out[r["nuclide_id"]] = (np.asarray(r["energy_bounds_ev"], float), cov)
            self._cov[mt] = out
        return self._cov[mt]

    def covariance(self, nid: str, mt: int) -> tuple[np.ndarray, np.ndarray] | None:
        """(bin bounds in eV (n+1), relative covariance (n, n)) or None."""
        return self._load_cov(mt).get(nid)

    def rel_unc_on_grid(self, nid: str, mt: int, grid: np.ndarray = ENERGY_GRID_EV):
        blk = self.covariance(nid, mt)
        if blk is None:
            return None
        bounds, cov = blk
        d = np.sqrt(np.clip(np.diag(cov), 0.0, None))
        idx = np.searchsorted(bounds, grid, side="right") - 1
        rel = np.full(len(grid), np.nan)
        ok = (idx >= 0) & (idx < len(d))
        rel[ok] = d[idx[ok]]
        return rel


# ----------------------------------------------------------------------------- metrics


def _wmedian(x: np.ndarray, w: np.ndarray | None) -> float:
    if x.size == 0:
        return math.nan
    if w is None:
        return float(np.median(x))
    o = np.argsort(x)
    cw = np.cumsum(w[o])
    if cw[-1] <= 0:
        return float(np.median(x))
    return float(x[o][np.searchsorted(cw, 0.5 * cw[-1])])


def point_metrics(
    pred: np.ndarray,
    ref: np.ndarray,
    *,
    pred_unc: np.ndarray | None = None,
    ref_unc: np.ndarray | None = None,
    weights: np.ndarray | None = None,
) -> dict[str, float]:
    """Log-space error metrics of ``pred`` against ``ref`` (both positive, same shape).

    Uncertainties are absolute 1σ in the same units (NaN = unknown). Coverage counts the
    points whose |pred − ref| lies within k·sqrt(pred_unc² + ref_unc²) — with only one of
    the two given that is the usual "is the stated error bar honest" question; with
    neither it is NaN. χ²/ndf uses the same combined variance. Weighted variants use
    ``weights`` (trust); the unweighted ones are always reported too (plan trap 2).
    """
    pred = np.asarray(pred, float)
    ref = np.asarray(ref, float)
    ok = np.isfinite(pred) & np.isfinite(ref) & (pred > 0) & (ref > 0)
    out: dict[str, float] = {"n": int(ok.sum())}
    if not ok.any():
        out["n_unc"] = 0
        return out | {
            k: math.nan
            for k in (
                "rms_log10",
                "median_abs_log10",
                "median_rel_err",
                "bias_log10",
                "rms_log10_w",
                "bias_log10_w",
                "chi2_ndf",
                "cov_1s",
                "cov_2s",
            )
        }
    p, r = pred[ok], ref[ok]
    lr = np.log10(p / r)
    w = None if weights is None else np.asarray(weights, float)[ok]
    out["rms_log10"] = float(np.sqrt(np.mean(lr**2)))
    out["median_abs_log10"] = float(np.median(np.abs(lr)))
    out["median_rel_err"] = float(np.median(p / r - 1.0))
    out["bias_log10"] = float(np.mean(lr))
    if w is not None and np.isfinite(w).any() and np.nansum(w) > 0:
        w = np.where(np.isfinite(w), w, 0.0)
        out["rms_log10_w"] = float(np.sqrt(np.sum(w * lr**2) / np.sum(w)))
        out["bias_log10_w"] = float(np.sum(w * lr) / np.sum(w))
    else:
        out["rms_log10_w"] = out["rms_log10"]
        out["bias_log10_w"] = out["bias_log10"]
    var = np.zeros(p.size)
    have = np.zeros(p.size, dtype=bool)
    for u in (pred_unc, ref_unc):
        if u is None:
            continue
        uu = np.asarray(u, float)[ok]
        good = np.isfinite(uu) & (uu >= 0)
        var = np.where(good, var + uu**2, var)
        have |= good
    have &= var > 0
    out["n_unc"] = int(have.sum())
    if have.any():
        z = np.abs(p[have] - r[have]) / np.sqrt(var[have])
        out["chi2_ndf"] = float(np.mean(z**2))
        out["cov_1s"] = float(np.mean(z <= 1.0))
        out["cov_2s"] = float(np.mean(z <= 2.0))
    else:
        out["chi2_ndf"] = out["cov_1s"] = out["cov_2s"] = math.nan
    return out


def chi2_with_covariance(
    d_rel: np.ndarray, rel_cov: np.ndarray, extra_var: np.ndarray | None = None, rcond: float = 1e-4
) -> tuple[float, int]:
    """(χ², rank) of relative residuals ``d_rel`` under ``rel_cov`` (+ diagonal ``extra_var``).

    The MF33 blocks are usually rank-deficient (LB=5 with fully correlated sub-blocks:
    TENDL's 9-bin capture blocks have effective rank ≈ 2), so the pseudo-inverse with
    eigenvalues below ``rcond``·max dropped is used and the rank is the effective number of
    degrees of freedom. ``rcond = 1e-4`` sits well above the round-off floor (≈ 1e-8, where
    keeping the noise modes inflates χ² by 10⁵; at 1e-6 a marginal third mode still turns a
    0.06 into 22 for 76Se) and the result is flat from 1e-4 to 1e-2 on every case checked.
    """
    cov = np.asarray(rel_cov, float).copy()
    if extra_var is not None:
        cov[np.diag_indices_from(cov)] += np.asarray(extra_var, float)
    ok = np.isfinite(d_rel) & np.isfinite(np.diag(cov)) & (np.diag(cov) > 0)
    if ok.sum() == 0:
        return math.nan, 0
    d = d_rel[ok]
    cov = cov[np.ix_(ok, ok)]
    wv, vec = np.linalg.eigh(0.5 * (cov + cov.T))
    keep = wv > rcond * wv.max()
    if not keep.any():
        return math.nan, 0
    proj = vec[:, keep].T @ d
    return float(np.sum(proj**2 / wv[keep])), int(keep.sum())


# ----------------------------------------------------------------------------- (a) vs libraries


def _region_masks(grid: np.ndarray, rrr_ev: float, urr_ev: float) -> dict[str, np.ndarray]:
    urr_top = max(rrr_ev, urr_ev)
    above = grid > rrr_ev
    return {
        "above_rrr": above,
        "urr": above & (grid <= urr_top),
        "fast": grid > urr_top,
    }


def _bin_average(grid: np.ndarray, values: np.ndarray, bounds: np.ndarray) -> np.ndarray:
    """Mean of ``values`` over the grid points inside each [bounds[i], bounds[i+1]) bin.

    The grid is log-uniform, so this is a log-uniform (per-lethargy) average, which is the
    weighting MF33 bins are usually meant for. Bins with no grid point get NaN.
    """
    idx = np.searchsorted(bounds, grid, side="right") - 1
    n = len(bounds) - 1
    out = np.full(n, np.nan)
    ok = (idx >= 0) & (idx < n) & np.isfinite(values)
    if not ok.any():
        return out
    s = np.bincount(idx[ok], values[ok], minlength=n)
    c = np.bincount(idx[ok], minlength=n)
    nz = c > 0
    out[nz] = s[nz] / c[nz]
    return out


def compare_to_library(
    pred: PredictionSet,
    ref: Library | str,
    *,
    grid: np.ndarray = ENERGY_GRID_EV,
    e_min_ev: float | None = None,
    e_max_ev: float | None = None,
    regions: Iterable[str] = REGIONS,
) -> pl.DataFrame:
    """One row per (nuclide, mt, region) with the point metrics of ``pred`` vs ``ref``.

    The resolved-resonance region is excluded up to max(prediction's, reference's) RRR
    upper bound; ``urr`` is the reference's unresolved range above that; ``fast`` is above
    the URR; ``above_rrr`` is their union. ``chi2_cov_ndf`` is the χ²/ndf with the
    reference's MF33 block (bins fully inside the region), NaN where no block exists.

    Two columns here are named in a way a reader can misread, so they are spelled out:

    * ``rms_log10_w`` / ``bias_log10_w`` are **not** weighted on this path. There is no trust
      weight to apply to an evaluated library's grid, so ``point_metrics`` falls back to the
      unweighted value and the two columns are identical by construction. Only the EXFOR
      tables (``summarize_exfor``) carry a real trust weight.
    * ``chi2_ndf`` / ``cov_1s`` / ``cov_2s`` here are computed on the **linear** residual
      (p − r)/σ, while the identically-named columns of ``summarize_exfor`` are computed on
      the **log10** residual. The two are not comparable across report sections, and
      ``chi2_ndf`` here counts every grid point as a degree of freedom even though a smooth
      σ(E) on a 3000-point log grid has far fewer.
    """
    lib = Library(ref, mts=pred.mts) if isinstance(ref, str) else ref
    rows = []
    e_lo = e_min_ev if e_min_ev is not None else -math.inf
    e_hi = e_max_ev if e_max_ev is not None else math.inf
    window = (grid >= e_lo) & (grid <= e_hi)
    for (nid, mt), p in pred.items():
        if not lib.has(nid, mt):
            continue
        r, r_rrr, r_urr = lib.curve(nid, mt)
        s, u = p.on_grid(grid)
        rrr_ev = max(p.rrr_upper_ev, r_rrr)
        urr_ev = max(p.urr_upper_ev, r_urr)
        r_unc = lib.rel_unc_on_grid(nid, mt, grid)
        r_unc_abs = None if r_unc is None else r_unc * r
        blk = lib.covariance(nid, mt)
        masks = _region_masks(grid, rrr_ev, urr_ev)
        urr_top = max(rrr_ev, urr_ev)
        region_bounds = {
            "above_rrr": (rrr_ev, math.inf),
            "urr": (rrr_ev, urr_top),
            "fast": (urr_top, math.inf),
        }
        Z, N, iso = parse_nuclide_id(nid)
        for region in regions:
            m = masks[region] & window & np.isfinite(s) & np.isfinite(r)
            met = point_metrics(np.where(m, s, np.nan), r, pred_unc=u, ref_unc=r_unc_abs)
            chi2c, ndf = math.nan, 0
            if blk is not None and met["n"] > 0:
                bounds, cov = blk
                lo, hi = region_bounds[region]
                lo, hi = max(lo, e_lo), min(hi, e_hi)
                # MF33 bins fully inside the region window
                inside = (bounds[:-1] >= lo * (1 - 1e-9)) & (bounds[1:] <= hi * (1 + 1e-9))
                if inside.sum() >= 1:
                    sb = _bin_average(grid, np.where(m, s, np.nan), bounds)
                    rb = _bin_average(grid, np.where(m, r, np.nan), bounds)
                    with np.errstate(divide="ignore", invalid="ignore"):
                        d = np.where(inside & (rb > 0), sb / rb - 1.0, np.nan)
                    extra = None
                    if u is not None:
                        ub = _bin_average(
                            grid, np.where(m, u / np.where(s > 0, s, np.nan), np.nan), bounds
                        )
                        extra = np.where(np.isfinite(ub), ub**2, 0.0)
                    chi2, ndf = chi2_with_covariance(d, cov, extra)
                    chi2c = chi2 / ndf if ndf else math.nan
            rows.append(
                {
                    "nuclide_id": nid,
                    "Z": Z,
                    "N": N,
                    "A": Z + N,
                    "iso": iso,
                    "mt": mt,
                    "mass_region": mass_region(Z, Z + N),
                    "region": region,
                    "rrr_upper_ev": rrr_ev,
                    "urr_upper_ev": urr_ev,
                    "e_lo_ev": float(grid[m].min()) if m.any() else math.nan,
                    "e_hi_ev": float(grid[m].max()) if m.any() else math.nan,
                    **met,
                    "chi2_cov_ndf": chi2c,
                    "cov_ndf": ndf,
                    "has_cov": blk is not None,
                    "reference": lib.name,
                }
            )
    return (
        pl.DataFrame(rows, schema=_LIB_ROW_SCHEMA) if rows else pl.DataFrame(schema=_LIB_ROW_SCHEMA)
    )


_LIB_ROW_SCHEMA = {
    "nuclide_id": pl.Utf8,
    "Z": pl.Int16,
    "N": pl.Int16,
    "A": pl.Int16,
    "iso": pl.Int8,
    "mt": pl.Int16,
    "mass_region": pl.Utf8,
    "region": pl.Utf8,
    "rrr_upper_ev": pl.Float64,
    "urr_upper_ev": pl.Float64,
    "e_lo_ev": pl.Float64,
    "e_hi_ev": pl.Float64,
    "n": pl.Int64,
    "rms_log10": pl.Float64,
    "median_abs_log10": pl.Float64,
    "median_rel_err": pl.Float64,
    "bias_log10": pl.Float64,
    "rms_log10_w": pl.Float64,
    "bias_log10_w": pl.Float64,
    "chi2_ndf": pl.Float64,
    "cov_1s": pl.Float64,
    "cov_2s": pl.Float64,
    "n_unc": pl.Int64,
    "chi2_cov_ndf": pl.Float64,
    "cov_ndf": pl.Int64,
    "has_cov": pl.Boolean,
    "reference": pl.Utf8,
}


# ----------------------------------------------------------------------------- (b) vs EXFOR


@dataclass
class ExforPoints:
    """Measurement bins ready to be scored: one row per (nuclide, mt, bin[, dataset])."""

    frame: pl.DataFrame
    mode: str
    year_cutoff: int | None = None
    kinds: tuple[str, ...] = EXFOR_KINDS


def load_exfor_points(
    *,
    mode: str = "consensus",
    year_cutoff: int | None = None,
    kinds: Iterable[str] = EXFOR_KINDS,
    state: str = "",
    branch: str = "",
    mts: Iterable[int] = (102,),
    min_trust: float = 0.0,
    consensus_path: Path | None = None,
    channel: str = "capture",
) -> ExforPoints:
    """WP-12 measurements as scoring targets.

    ``mode="consensus"``: one row per (nuclide, mt, bin) from the consensus table, with
    ``weight`` = Σ trust of the datasets contributing to that bin (unweighted metrics count
    every bin once) and ``sigma_log10`` from the fitted consensus uncertainty.

    ``mode="datasets"`` (forced when ``year_cutoff`` is given): one row per (dataset, bin)
    cell — the measurement itself, trust as weight, reported σ × WP-12 inflation as the
    uncertainty, and only datasets with ``year > year_cutoff`` when a cutoff is given
    (retrodiction, blueprint §4.4 item 3 / §6.1).

    Every selection below is counted and the tally written to stderr (and to
    ``LAST_EXFOR_LOAD_DROPS``): ``kind``/``state``/``branch`` are the WP-12 *comparable
    quantity* key — ``sig`` and ``av`` are different quantities, and a partial to an isomer
    is not the total — so the selection is the defence against failure-mode §5 and has to
    say how much of the table it removed.
    """
    kinds = tuple(kinds)
    mts = [int(m) for m in mts]
    # WP-19: a channel selects which curated tables to read. Defaulting to capture keeps every
    # existing call site scoring exactly what it scored before.
    if consensus_path is None:
        consensus_path = C.channel_consensus(channel)
    all_cells = pl.read_parquet(C.cache_exfor_cells(channel=channel))
    quantity = all_cells.filter(
        pl.col("kind").is_in(kinds)
        & (pl.col("state") == state)
        & (pl.col("branch") == branch)
        & pl.col("mt").is_in(mts)
    )
    curated = quantity.filter(pl.col("usable") & (pl.col("decision") != "exclude"))
    cells = curated.filter(pl.col("trust") >= min_trust)
    drops: dict[str, int | float | str] = {
        "channel": channel,
        "cells_total": all_cells.height,
        "cells_after_quantity": quantity.height,
        "cells_after_curation": curated.height,
        "cells_after_trust": cells.height,
        "dropped_quantity": all_cells.height - quantity.height,
        "dropped_curation": quantity.height - curated.height,
        "dropped_trust": curated.height - cells.height,
        "min_trust": float(min_trust),
    }
    if year_cutoff is not None:
        mode = "datasets"
    if mode == "consensus":
        all_cons = pl.read_parquet(consensus_path)
        cons = all_cons.filter(
            pl.col("kind").is_in(kinds)
            & (pl.col("state") == state)
            & (pl.col("branch") == branch)
            & pl.col("mt").is_in(mts)
        )
        drops["consensus_total"] = all_cons.height
        drops["consensus_after_quantity"] = cons.height
        drops["dropped_consensus_quantity"] = all_cons.height - cons.height
        wt = cells.group_by("group_key", "bin").agg(
            weight=pl.col("trust").sum(),
            year_max=pl.col("year").max(),
            year_min=pl.col("year").min(),
            n_datasets_usable=pl.len(),
        )
        joined = cons.join(wt, on=["group_key", "bin"], how="left")
        # A null weight is a consensus bin with no surviving dataset behind it. Filling it
        # with 1.0 makes the *least* trustworthy bins heavier than the median real weight
        # (0.88 on the capture set) -- failure-mode §2, a sentinel that reads as a value, and
        # §4 with the sign flipped: raising ``min_trust`` would then promote exactly the bins
        # it was asked to demote. There are none at min_trust = 0 (verified on capture and
        # n2n), so the published numbers do not move; above 0 the bin is dropped, because its
        # consensus value is made of the datasets that were just excluded.
        n_orphan = int(joined["weight"].is_null().sum())
        drops["consensus_bins_without_cells"] = n_orphan
        if n_orphan and min_trust > 0:
            joined = joined.filter(pl.col("weight").is_not_null())
            drops["dropped_consensus_no_surviving_dataset"] = n_orphan
        elif n_orphan:
            _tally(
                f"[exfor] WARNING {n_orphan} consensus bins have no usable cell behind them; "
                "their trust weight falls back to 1.0 (above the median real weight)"
            )
        df = (
            joined.with_columns(
                weight=pl.col("weight").fill_null(1.0),
                meas_b=pl.col("consensus_b"),
                sigma_log10=pl.col("sigma_log") * LOG10E,
                dataset_key=pl.lit(None, dtype=pl.Utf8),
                year=pl.col("year_max"),
                trust=pl.lit(None, dtype=pl.Float64),
            )
            .select(
                "nuclide",
                "mt",
                "kind",
                "bin",
                "e_lo_ev",
                "e_hi_ev",
                "e_mid_ev",
                "meas_b",
                "sigma_log10",
                "weight",
                "n_datasets",
                "n_points",
                "dataset_key",
                "year",
                "trust",
            )
        )
    elif mode == "datasets":
        if year_cutoff is not None:
            n_before = cells.height
            cells = cells.filter(pl.col("year") > year_cutoff)
            drops["year_cutoff"] = int(year_cutoff)
            drops["dropped_year_cutoff"] = n_before - cells.height
        rel = (
            pl.when(pl.col("stat_rel").is_finite() | pl.col("sys_rel").is_finite())
            .then(
                (
                    pl.col("stat_rel").fill_nan(0.0).fill_null(0.0) ** 2
                    + pl.col("sys_rel").fill_nan(0.0).fill_null(0.0) ** 2
                ).sqrt()
            )
            .otherwise(pl.col("sem_rel"))
        )
        rel = pl.when(rel.is_finite() & (rel > 0)).then(rel).otherwise(0.10)  # no σ: assume 10 %
        df = cells.with_columns(
            meas_b=pl.col("mean_b"),
            sigma_log10=(rel * pl.col("inflation")).clip(1e-3, 3.0) * LOG10E,
            weight=pl.col("trust"),
            e_mid_ev=(pl.col("e_lo_ev") * pl.col("e_hi_ev")).sqrt(),
            n_datasets=pl.lit(1, dtype=pl.Int32),
            n_points=pl.col("n_pts").cast(pl.Int64),
        ).select(
            "nuclide",
            "mt",
            "kind",
            "bin",
            "e_lo_ev",
            "e_hi_ev",
            "e_mid_ev",
            "meas_b",
            "sigma_log10",
            "weight",
            "n_datasets",
            "n_points",
            "dataset_key",
            "year",
            "trust",
        )
    else:
        raise ValueError(f"mode must be 'consensus' or 'datasets', not {mode!r}")
    n_pre_positive = df.height
    df = df.filter(pl.col("meas_b") > 0).rename({"nuclide": "nuclide_id"})
    drops["dropped_non_positive_meas"] = n_pre_positive - df.height
    drops["rows"] = df.height
    drops["mode"] = mode
    LAST_EXFOR_LOAD_DROPS.clear()
    LAST_EXFOR_LOAD_DROPS.update(drops)
    _tally(
        f"[exfor] {channel} {mode}: {all_cells.height} cells -> {quantity.height} "
        f"(kinds {','.join(kinds)} / state {state!r} / branch {branch!r} / "
        f"MT {','.join(map(str, mts))}; -{drops['dropped_quantity']}) -> {curated.height} "
        f"(usable & not excluded; -{drops['dropped_curation']}) -> "
        f"{drops['cells_after_trust']} (trust >= {min_trust}; -{drops['dropped_trust']})"
        + (
            f" -> year > {year_cutoff} (-{drops.get('dropped_year_cutoff', 0)})"
            if year_cutoff is not None
            else ""
        )
        + f"; {df.height} scoring rows"
        + (
            f" (-{drops['dropped_non_positive_meas']} with meas_b <= 0)"
            if drops["dropped_non_positive_meas"]
            else ""
        )
    )
    return ExforPoints(df, mode=mode, year_cutoff=year_cutoff, kinds=kinds)


def rrr_bounds(
    libraries: Iterable[str] = ("endfb81", "jeff33", "jendl5", "cendl32", "tendl2025"),
    mt: int = 102,
) -> dict[str, float]:
    """max resolved-region upper bound over the given libraries, per nuclide (0 if none)."""
    out: dict[str, float] = {}
    for key in libraries:
        try:
            lib = Library(key, mts=(mt,))
        except FileNotFoundError:
            continue
        for nid in lib.nuclides(mt):
            r, _ = lib.bounds(nid, mt)
            out[nid] = max(out.get(nid, 0.0), r)
    return out


def bin_prediction(
    p: Prediction, e_lo: np.ndarray, e_hi: np.ndarray, grid: np.ndarray = ENERGY_GRID_EV
) -> tuple[np.ndarray, np.ndarray]:
    """Prediction averaged over each [e_lo, e_hi] (log-uniform), or interpolated at the
    geometric midpoint when no grid point falls inside. Returns (σ, σ_unc), NaN outside."""
    s, u = p.on_grid(grid)
    n = len(e_lo)
    out = np.full(n, np.nan)
    out_u = np.full(n, np.nan)
    lo = np.searchsorted(grid, e_lo, side="left")
    hi = np.searchsorted(grid, e_hi, side="right")
    mid = np.sqrt(e_lo * e_hi)
    s_mid = _loglog_interp(mid, grid, s)
    u_mid = _loglog_interp(mid, grid, u) if u is not None else None
    for i in range(n):
        seg = s[lo[i] : hi[i]]
        seg = seg[np.isfinite(seg)]
        if seg.size:
            out[i] = seg.mean()
            if u is not None:
                us = u[lo[i] : hi[i]]
                us = us[np.isfinite(us)]
                out_u[i] = us.mean() if us.size else np.nan
        else:
            out[i] = s_mid[i]
            if u_mid is not None:
                out_u[i] = u_mid[i]
    return out, out_u


def compare_to_exfor(
    pred: PredictionSet,
    points: ExforPoints | None = None,
    *,
    rrr: Mapping[str, float] | None = None,
    grid: np.ndarray = ENERGY_GRID_EV,
    **load_kwargs,
) -> pl.DataFrame:
    """Score ``pred`` on every EXFOR bin it covers; one row per bin (or dataset cell).

    Columns add ``pred_b``, ``pred_unc_b``, ``log10_ratio`` (pred/meas), ``z`` (in units of
    the combined log uncertainty), ``above_rrr`` (bin lower edge above the nuclide's RRR
    bound from ``rrr``, default = max over the five libraries) and the mass region.

    Three filters here remove scoring rows and all three are counted into
    ``LAST_EXFOR_SCORE_DROPS`` and written to stderr: bins on (nuclide, MT) pairs the
    prediction does not carry, bins where the prediction interpolates to nothing (outside
    its own energy range — on a real run this is a quarter of the set), and bins whose
    nuclide has **no** entry in ``rrr``. That last one is the dangerous one: ``rrr.get(nid,
    0.0)`` reads a missing bound as "resolved region ends at 0 eV", so *every* bin of such a
    nuclide, thermal resonances included, is flagged ``above_rrr`` and scored. That is
    failure-mode §2 exactly (a sentinel that reads as a value), so the count is reported
    rather than left to look like a clean run.
    """
    pts = points if points is not None else load_exfor_points(mts=pred.mts, **load_kwargs)
    rrr = rrr if rrr is not None else rrr_bounds(mt=pred.mts[0] if pred.mts else 102)
    n_in = pts.frame.height
    df = pts.frame.filter(pl.col("mt").is_in(pred.mts))
    parts = []
    no_bound: dict[str, int] = {}
    for (nid, mt), p in pred.items():
        sub = df.filter((pl.col("nuclide_id") == nid) & (pl.col("mt") == mt))
        if sub.height == 0:
            continue
        e_lo = sub["e_lo_ev"].to_numpy()
        e_hi = sub["e_hi_ev"].to_numpy()
        pb, pu = bin_prediction(p, e_lo, e_hi, grid)
        Z, N, _ = parse_nuclide_id(nid)
        if nid not in rrr:
            no_bound[nid] = no_bound.get(nid, 0) + sub.height
        bound = float(rrr.get(nid, 0.0))
        parts.append(
            sub.with_columns(
                pred_b=pl.Series(pb),
                pred_unc_b=pl.Series(pu),
                rrr_upper_ev=pl.lit(bound),
                above_rrr=pl.Series(e_lo > bound),
                Z=pl.lit(Z, dtype=pl.Int16),
                N=pl.lit(N, dtype=pl.Int16),
                A=pl.lit(Z + N, dtype=pl.Int16),
                mass_region=pl.lit(mass_region(Z, Z + N)),
            )
        )
    drops: dict[str, int | float | str] = {
        "label": pred.label,
        "rows_in": n_in,
        "dropped_other_mt": n_in - df.height,
        "nuclides_without_rrr_bound": len(no_bound),
        "rows_without_rrr_bound": sum(no_bound.values()),
    }
    if not parts:
        drops |= {"rows_on_prediction": 0, "dropped_pred_not_finite": 0, "rows_scored": 0}
        LAST_EXFOR_SCORE_DROPS.clear()
        LAST_EXFOR_SCORE_DROPS.update(drops)
        _tally(f"[exfor] {pred.label}: {n_in} rows in, 0 scored (no overlapping nuclide/MT)")
        return pl.DataFrame()
    out = pl.concat(parts, how="vertical")
    n_on_pred = out.height
    out = out.filter(pl.col("pred_b").is_finite() & (pl.col("pred_b") > 0))
    drops |= {
        "rows_on_prediction": n_on_pred,
        "dropped_no_prediction_nuclide": df.height - n_on_pred,
        "dropped_pred_not_finite": n_on_pred - out.height,
        "rows_scored": out.height,
        "rows_above_rrr": int(out["above_rrr"].sum()),
    }
    LAST_EXFOR_SCORE_DROPS.clear()
    LAST_EXFOR_SCORE_DROPS.update(drops)
    _tally(
        f"[exfor] {pred.label}: {n_in} rows -> {df.height} (MT of the prediction; "
        f"-{drops['dropped_other_mt']}) -> {n_on_pred} (nuclides the prediction covers; "
        f"-{drops['dropped_no_prediction_nuclide']}) -> {out.height} (prediction finite and "
        f"positive in the bin; -{drops['dropped_pred_not_finite']}); "
        f"{drops['rows_above_rrr']} above the RRR"
    )
    if no_bound:
        _tally(
            f"[exfor] WARNING {len(no_bound)} nuclide(s) have no RRR bound in the map "
            f"({sum(no_bound.values())} rows scored as if the resolved region ended at 0 eV): "
            + ", ".join(sorted(no_bound)[:8])
            + (" ..." if len(no_bound) > 8 else "")
        )
    pred_rel = (pl.col("pred_unc_b") / pl.col("pred_b")).fill_nan(0.0).fill_null(0.0) * LOG10E
    return out.with_columns(
        log10_ratio=(pl.col("pred_b") / pl.col("meas_b")).log10(),
    ).with_columns(
        z=pl.col("log10_ratio").abs() / (pl.col("sigma_log10") ** 2 + pred_rel**2).sqrt(),
    )


def summarize_exfor(
    scored: pl.DataFrame, by: Iterable[str] = (), *, above_rrr_only: bool = True
) -> pl.DataFrame:
    """Aggregate an exfor-scored frame: unweighted and trust-weighted log10 RMS, medians,
    χ²/ndf and coverage of the *combined* (measurement + prediction) uncertainty."""
    by = list(by)
    df = scored.filter(pl.col("above_rrr")) if above_rrr_only else scored
    if df.height == 0:
        return pl.DataFrame()
    w = pl.col("weight").fill_null(1.0)
    aggs = [
        pl.len().alias("n"),
        pl.col("nuclide_id").n_unique().alias("n_nuclides"),
        (pl.col("log10_ratio") ** 2).mean().sqrt().alias("rms_log10"),
        pl.col("log10_ratio").abs().median().alias("median_abs_log10"),
        (pl.col("pred_b") / pl.col("meas_b") - 1.0).median().alias("median_rel_err"),
        pl.col("log10_ratio").mean().alias("bias_log10"),
        ((w * pl.col("log10_ratio") ** 2).sum() / w.sum()).sqrt().alias("rms_log10_w"),
        ((w * pl.col("log10_ratio")).sum() / w.sum()).alias("bias_log10_w"),
        (pl.col("z") ** 2).filter(pl.col("z").is_finite()).mean().alias("chi2_ndf"),
        (pl.col("z") <= 1.0).filter(pl.col("z").is_finite()).mean().alias("cov_1s"),
        (pl.col("z") <= 2.0).filter(pl.col("z").is_finite()).mean().alias("cov_2s"),
    ]
    if by:
        return df.group_by(by).agg(aggs).sort(by)
    return df.select(aggs)


# ----------------------------------------------------------------------------- (c) MACS


def maxwellian_average(
    energy_ev: np.ndarray,
    sigma_b: np.ndarray,
    kT_ev: float,
    *,
    A: float | None = None,
    extrapolate_1v: bool = True,
) -> tuple[float, float]:
    """MACS(kT) = 2/√π · (kT)⁻² ∫ σ(E) E e^{−E/kT} dE = 2/√π · ∫ σ x² e^{−x} d ln x, x = E/kT.

    Trapezoids in ln x. A constant σ therefore gives 2σ/√π and a 1/v cross section gives
    σ(E = kT), the two analytic checks in the tests. ``energy_ev`` is the *laboratory*
    neutron energy of the tabulation; when ``A`` (target mass number) is given the
    integral runs over the centre-of-mass energy the Maxwellian and KADoNiS refer to
    (E_cm = E_lab · A/(A+1)). NaN values below the first finite point are filled by a 1/v
    extrapolation when ``extrapolate_1v`` (the s-wave low-energy limit); NaN above the
    last finite point count as zero. Returns (MACS in barns, fraction of the Maxwellian
    weight covered by finite σ before any filling).
    """
    e = np.asarray(energy_ev, float)
    s = np.asarray(sigma_b, float).copy()
    if A is not None:
        e = e * (A / (A + 1.0))
    fin = np.isfinite(s)
    if not fin.any() or e.size < 2:
        return math.nan, 0.0
    x = e / kT_ev
    lnx = np.log(x)
    kernel = x * x * np.exp(-x)

    def integ(f: np.ndarray) -> float:
        g = np.where(np.isfinite(f), f, 0.0) * kernel
        return float(np.sum(0.5 * (g[1:] + g[:-1]) * np.diff(lnx)))

    grid_norm = integ(np.ones_like(s))  # → ∫ x e^{-x} dx = 1 on a complete, fine grid
    if grid_norm <= 0:
        return math.nan, 0.0
    covered = integ(fin.astype(float)) / grid_norm
    first = int(np.flatnonzero(fin)[0])
    if extrapolate_1v and first > 0 and s[first] > 0:
        s[:first] = s[first] * np.sqrt(e[first] / e[:first])
    macs = (2.0 / math.sqrt(math.pi)) * integ(s) / grid_norm
    return macs, covered


def macs_table(
    pred: PredictionSet,
    kT_keV: Iterable[float] = (30.0,),
    *,
    cm_correction: bool = True,
    grid: np.ndarray = ENERGY_GRID_EV,
) -> pl.DataFrame:
    """MACS of every (nuclide, mt) of ``pred`` at each kT, in mb, folded on the common grid
    (coarse native grids such as the 20-point TALYS sweep are log-log interpolated first);
    the uncertainty is folded the same way (fully-correlated assumption)."""
    rows = []
    for (nid, mt), p in pred.items():
        Z, N, iso = parse_nuclide_id(nid)
        A = Z + N
        s, u = p.on_grid(grid)
        for kt in kT_keV:
            m, cov = maxwellian_average(grid, s, kt * 1e3, A=A if cm_correction else None)
            mu = math.nan
            if u is not None:
                mu, _ = maxwellian_average(grid, u, kt * 1e3, A=A if cm_correction else None)
            rows.append(
                {
                    "nuclide_id": nid,
                    "Z": Z,
                    "N": N,
                    "A": A,
                    "iso": iso,
                    "mt": mt,
                    "kT_keV": float(kt),
                    "macs_mb": m * 1e3,
                    "macs_unc_mb": mu * 1e3,
                    "weight_coverage": cov,
                    "mass_region": mass_region(Z, A),
                }
            )
    schema = {
        "nuclide_id": pl.Utf8,
        "Z": pl.Int16,
        "N": pl.Int16,
        "A": pl.Int16,
        "iso": pl.Int8,
        "mt": pl.Int16,
        "kT_keV": pl.Float64,
        "macs_mb": pl.Float64,
        "macs_unc_mb": pl.Float64,
        "weight_coverage": pl.Float64,
        "mass_region": pl.Utf8,
    }
    return pl.DataFrame(rows, schema=schema)


def load_kadonis(path: Path = KADONIS_MACS) -> pl.DataFrame:
    """KADoNiS v1.0 ground-state MACS, long format: nuclide_id, kT_keV, kadonis_mb, kadonis_err_mb
    (the table only quotes an uncertainty at 30 keV; other kT get a NaN error)."""
    from data.ingest.kadonis import KT_KEV, read_macs

    df = read_macs(path).filter(pl.col("isomer") != "m")
    parts = []
    for kt in KT_KEV:
        parts.append(
            df.select(
                nuclide_id=pl.format(
                    "Z{}N{}M0",
                    pl.col("Z").cast(pl.Utf8).str.zfill(3),
                    pl.col("N").cast(pl.Utf8).str.zfill(3),
                ),
                kT_keV=pl.lit(float(kt)),
                kadonis_mb=pl.col(f"macs_{kt}_mb"),
                kadonis_err_mb=pl.col("macs_30_err_mb")
                if kt == 30
                else pl.lit(None, dtype=pl.Float64),
            )
        )
    return pl.concat(parts).filter(pl.col("kadonis_mb").is_not_null())


def compare_to_kadonis(
    pred: PredictionSet,
    kT_keV: Iterable[float] = (30.0,),
    *,
    kadonis: pl.DataFrame | None = None,
    min_coverage: float = 0.98,
) -> pl.DataFrame:
    """Per-(nuclide, kT) rows: predicted MACS vs KADoNiS, log10 ratio and z with KADoNiS'
    30 keV error (plus the prediction's folded uncertainty where present)."""
    kad = kadonis if kadonis is not None else load_kadonis()
    all_tab = macs_table(pred, kT_keV)
    tab = all_tab.filter(pl.col("weight_coverage") >= min_coverage)
    df = tab.join(kad, on=["nuclide_id", "kT_keV"], how="inner")
    if all_tab.height != tab.height or tab.height != df.height:
        _tally(
            f"[macs] {pred.label}: {all_tab.height} (nuclide, kT) folds -> {tab.height} "
            f"(Maxwellian weight covered >= {min_coverage}; "
            f"-{all_tab.height - tab.height}) -> {df.height} (in KADoNiS; "
            f"-{tab.height - df.height})"
        )
    pu = pl.col("macs_unc_mb").fill_nan(0.0).fill_null(0.0)
    ke = pl.col("kadonis_err_mb").fill_null(0.0)
    return df.with_columns(
        log10_ratio=(pl.col("macs_mb") / pl.col("kadonis_mb")).log10(),
        rel_err=pl.col("macs_mb") / pl.col("kadonis_mb") - 1.0,
        z=pl.when((pu**2 + ke**2) > 0)
        .then((pl.col("macs_mb") - pl.col("kadonis_mb")).abs() / (pu**2 + ke**2).sqrt())
        .otherwise(None),
    )


def summarize_macs(scored: pl.DataFrame, by: Iterable[str] = ()) -> pl.DataFrame:
    by = list(by)
    if scored.height == 0:
        return pl.DataFrame()
    aggs = [
        pl.len().alias("n"),
        (pl.col("log10_ratio") ** 2).mean().sqrt().alias("rms_log10"),
        pl.col("log10_ratio").abs().median().alias("median_abs_log10"),
        pl.col("rel_err").median().alias("median_rel_err"),
        pl.col("log10_ratio").mean().alias("bias_log10"),
        (pl.col("z") ** 2).mean().alias("chi2_ndf"),
        (pl.col("z") <= 1.0).mean().alias("cov_1s"),
        (pl.col("z") <= 2.0).mean().alias("cov_2s"),
        (pl.col("rel_err").abs() <= 0.30).mean().alias("within_30pct"),
    ]
    if by:
        return scored.group_by(by).agg(aggs).sort(by)
    return scored.select(aggs)


# ----------------------------------------------------------------------------- aggregation


def _finite_median(col: str) -> pl.Expr:
    c = pl.col(col)
    return c.filter(c.is_finite()).median()


def _pooled_fraction(col: str, ncol: str) -> pl.Expr:
    """Point-weighted mean of a per-nuclide fraction, ignoring rows without points."""
    c = pl.col(col)
    n = pl.col(ncol).cast(pl.Float64)
    ok = c.is_finite() & (n > 0)
    return (
        pl.when(n.filter(ok).sum() > 0)
        .then((n * c).filter(ok).sum() / n.filter(ok).sum())
        .otherwise(None)
    )


def aggregate_library_rows(rows: pl.DataFrame, by: Iterable[str] = ("region",)) -> pl.DataFrame:
    """Pooled (point-weighted) and per-nuclide-median summaries of compare_to_library rows."""
    by = list(by)
    if rows.height == 0:
        return pl.DataFrame()
    nn = pl.col("n").cast(pl.Float64)
    df = rows.filter(pl.col("n") > 0)
    return (
        df.group_by(by)
        .agg(
            pl.col("nuclide_id").n_unique().alias("n_nuclides"),
            pl.col("n").sum().alias("n_points"),
            ((nn * pl.col("rms_log10") ** 2).sum() / nn.sum()).sqrt().alias("rms_log10_pooled"),
            pl.col("rms_log10").median().alias("rms_log10_median"),
            pl.col("median_abs_log10").median().alias("median_abs_log10"),
            pl.col("median_rel_err").median().alias("median_rel_err"),
            ((nn * pl.col("bias_log10")).sum() / nn.sum()).alias("bias_log10"),
            _finite_median("chi2_ndf").alias("chi2_diag_ndf_median"),
            _finite_median("chi2_cov_ndf").alias("chi2_cov_ndf_median"),
            (pl.col("cov_ndf") > 0).sum().alias("n_with_cov"),
            _pooled_fraction("cov_1s", "n_unc").alias("cov_1s"),
            _pooled_fraction("cov_2s", "n_unc").alias("cov_2s"),
        )
        .sort(by)
    )


def add_holdout_flags(
    df: pl.DataFrame, holdouts: Mapping[str, frozenset[str]] | None = None
) -> pl.DataFrame:
    """Boolean column ``holdout_<split>`` per WP-05 region holdout."""
    hs = region_holdouts() if holdouts is None else holdouts
    if df.height == 0:
        return df
    return df.with_columns(
        [
            pl.col("nuclide_id").is_in(list(members)).alias(f"holdout_{name}")
            for name, members in hs.items()
        ]
    )


@dataclass
class HarnessResult:
    label: str
    vs_library: dict[str, pl.DataFrame] = field(default_factory=dict)
    vs_exfor: pl.DataFrame | None = None
    vs_exfor_retro: dict[int, pl.DataFrame] = field(default_factory=dict)
    vs_kadonis: pl.DataFrame | None = None
    macs: pl.DataFrame | None = None


def run_harness(
    pred: PredictionSet,
    *,
    references: Iterable[str] = ("endfb81", "jeff33", "jendl5"),
    year_cutoffs: Iterable[int] = (2003, 2012, 2016),
    kT_keV: Iterable[float] = (5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100),
    exfor: bool = True,
    kadonis: bool = True,
) -> HarnessResult:
    """Everything the report needs, as frames (no printing)."""
    res = HarnessResult(label=pred.label)
    for key in references:
        if pred.meta.get("library") == key:
            continue
        res.vs_library[key] = add_holdout_flags(compare_to_library(pred, key))
    if exfor:
        rrr = rrr_bounds(mt=pred.mts[0] if pred.mts else 102)
        res.vs_exfor = add_holdout_flags(compare_to_exfor(pred, rrr=rrr))
        for y in year_cutoffs:
            pts = load_exfor_points(mode="datasets", year_cutoff=y, mts=pred.mts)
            res.vs_exfor_retro[y] = add_holdout_flags(compare_to_exfor(pred, pts, rrr=rrr))
    if kadonis and KADONIS_MACS.is_file():
        res.macs = macs_table(pred, kT_keV)
        res.vs_kadonis = add_holdout_flags(compare_to_kadonis(pred, kT_keV))
    return res
