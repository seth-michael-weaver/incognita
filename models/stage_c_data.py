"""Build the Stage C training bundle from the repository's own curated data (WP-15).

Stage B cross sections come from the TALYS surrogate, the targets from the WP-12 curated
EXFOR consensus with trust weights, the teacher from an evaluated library, and the time
split from the publication year of the datasets behind each bin. Nothing here trains: it
only assembles tensors, so the trainer stays testable on synthetic data.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np
import torch

from models.train_stage_c import StageCBundle
from validation.differential import core as C

ROOT = Path(__file__).resolve().parent.parent
MAIN = Path(os.environ.get("INCOGNITA_MAIN", Path(__file__).resolve().parents[1]))   # data directory; default: the repository root

# which surrogate Stage C sits on; set INCOGNITA_SURROGATE to compare them

def _env(name: str, default: str = "") -> str:
    """Read the environment variable INCOGNITA_<name>."""
    return os.environ.get(f"INCOGNITA_{name}", default)


def inelastic_threshold_default() -> bool:
    """The shipped default for the `inelastic_threshold` block, read at call time."""
    return _env("INELASTIC_THRESHOLD", "1").strip().lower() not in ("0", "false", "off", "no", "")

SURROGATE_TAG = _env("SURROGATE", "v3")   # v7 covers 872 nuclides but scores
# worse on the measured benchmark: its extra coverage is in the unmeasured, neutron-rich region
# that the benchmark cannot see, and it bought that coverage with fewer parameter draws


def _data(rel: str) -> Path:
    """Data lives in the main checkout; a worktree only carries code."""
    here = ROOT / rel
    return here if here.exists() else MAIN / rel


def _ckpt(rel: str) -> Path:
    """Prefer this checkout's file, fall back to the main one (a worktree has no data)."""
    here = ROOT / rel
    return here if here.exists() else MAIN / rel


def check_engine_coverage(ids: list[str], engine_b: dict, epath: str) -> list[str]:
    """Refuse a Stage B engine table that does not cover every nuclide of the final bundle.

    An engine table is a recipe, not a hint: a bundle nuclide it does not carry (absent, or a row
    dropped as non-finite) would silently get the surrogate Stage B instead -- on a chart-wide
    run that ships an unvalidated recipe above 5 MeV with no error. Called on the FINAL nuclide
    list, so a table covering only the nuclides with data still passes a require_measurements
    bundle. INCOGNITA_STAGE_B_ALLOW_FALLBACK=1 restores the old behaviour; returns the uncovered.
    """
    uncovered = [nid for nid in ids if nid not in engine_b]
    if uncovered and _env("STAGE_B_ALLOW_FALLBACK", "") != "1":
        raise ValueError(
            f"INCOGNITA_STAGE_B_ENGINE={epath} does not cover {len(uncovered)} of {len(ids)} "
            f"bundle nuclides: {uncovered[:20]}{' ...' if len(uncovered) > 20 else ''}. "
            "Extend the table, or set INCOGNITA_STAGE_B_ALLOW_FALLBACK=1 to give them the "
            "surrogate Stage B on purpose.")
    if uncovered:
        print(f"[stage-c] INCOGNITA_STAGE_B_ALLOW_FALLBACK=1: {len(uncovered)} bundle nuclides "
              "on the surrogate path", flush=True)
    return uncovered


def _grid(e_min_ev: float, e_max_ev: float, n: int) -> np.ndarray:
    """A log-spaced energy grid; Stage C works on a coarser grid than the libraries."""
    return np.logspace(np.log10(e_min_ev), np.log10(e_max_ev), n)


def _bin_index(values: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Nearest grid point for each energy, in log space."""
    return np.abs(np.log10(values)[:, None] - np.log10(grid)[None, :]).argmin(axis=1)


def encoder_embeddings(ids: list[str], dim: int,
                       basis_ids: list[str] | None = None) -> np.ndarray:
    """Frozen WP-06 chart embeddings for the compound and target nuclei, reduced to `dim`.

    For (n,gamma) on target (Z, N) the compound nucleus is (Z, N+1); `gather` returns the
    compound for the (Z, N) it is given and the target one neutron below it, so we pass
    (Z, N+1) and get both halves of the reaction. The 512 features are projected onto their
    leading principal components: 33 nuclides cannot constrain 512 inputs.

    ``basis_ids`` fixes whose principal components those are. The projection — the mean, the
    components and the per-column normalisation — is fitted on the basis set and then applied
    to `ids`, so a nuclide gets the same embedding whichever company it is asked in. Without
    it the basis is refitted on whatever happens to be in the bundle, and running the trained
    residual over the whole chart instead of the 225 it was fitted on silently rotates its
    input: measured 2026-09-11, all 16 encoder columns of a shared nuclide moved by up to 1.9
    in units where the whole column spans [-1, 1], while the 26 physics columns were identical.
    Leave it None to fit on `ids` themselves, which is what training does and must keep doing.
    """
    from models.decoder import embeddings as EMB

    field = EMB.load("production")

    def feature_rows(which: list[str]) -> np.ndarray:
        zn = np.array([[int(nid[1:4]), int(nid[5:8])] for nid in which])
        cn, tg, _has_t, _in_chart = EMB.gather(field["emb"], zn[:, 0], zn[:, 1] + 1,
                                               field["exists"])
        return np.concatenate([cn, tg], axis=1).astype(np.float64)

    basis = list(basis_ids) if basis_ids else list(ids)
    xb = feature_rows(basis)
    mean = xb.mean(axis=0, keepdims=True)
    xb = xb - mean
    k = min(dim, len(basis) - 1, xb.shape[1])
    _u, _sv, vt = np.linalg.svd(xb, full_matrices=False)
    norm = np.abs(xb @ vt[:k].T).max(axis=0, keepdims=True).clip(1e-9)
    z = ((feature_rows(ids) - mean) @ vt[:k].T) / norm   # keep the residual net well conditioned
    out = np.zeros((len(ids), dim), np.float32)
    out[:, :k] = z
    return out


def macs_covered(ids: list[str]) -> np.ndarray:
    """Boolean per nuclide: does KADoNiS quote a Maxwellian-averaged cross section for it?

    A MACS is an integral of the capture cross section against a Maxwellian at kT = 5-100 keV,
    so its weight sits at E = 2kT, 10-200 keV -- the decade the model is scored in and the one
    the per-nuclide normalisation error lives in. For a nuclide with no differential data it is
    the only measurement of that normalisation there is.
    """
    from models.macs_constraint import KADONIS_TSV, load_macs

    _macs, weight, _kt = load_macs(list(ids), _data(KADONIS_TSV))
    return (weight.sum(dim=1) > 0).numpy()


def curated_plus_macs(z_min: int = 26, z_max: int = 92,
                      channel: str = "capture") -> list[tuple[int, int, float]]:
    """Every curated nuclide, plus every charted one KADoNiS has measured.

    `curated_nuclides` is the set with differential data, which is what Stage C has always
    trained on. It leaves out 98 nuclides in Z 26-92 whose capture normalisation is measured --
    as a Maxwellian average rather than a curve -- and which are therefore predicted with no
    measurement of their own at all.
    """
    cur = curated_nuclides(z_min, z_max, channel=channel)
    have = {(z, n) for z, n, _ in cur}
    chart = chart_nuclides(z_min, z_max)
    ids = [f"Z{z:03d}N{n:03d}M0" for z, n, _ in chart]
    cov = macs_covered(ids)
    extra = [t for t, c in zip(chart, cov, strict=True)
             if c and (t[0], t[1]) not in have]
    return sorted(cur + extra)


NEUTRON_ME_KEV = 8071.31806


def curated_nuclides(z_min: int = 26, z_max: int = 92,
                     channel: str = "capture") -> list[tuple[int, int, float]]:
    """(Z, N, S_n of the compound) for every nuclide with curated data in ``channel``.

    The surrogate only needs the compound's neutron separation energy, so it can predict a
    nuclide TALYS was never swept over — that is the whole point of having a surrogate. S_n
    comes from the AME mass excesses in the feature table:
    S_n(Z, N+1) = ME(Z, N) + ME(neutron) - ME(Z, N+1).
    """
    import polars as pl

    feats = pl.read_parquet(_data("features/nuclide_features.parquet"),
                            columns=["Z", "N", "target_mass_excess_kev"])
    me = {(int(z), int(n)): float(v) for z, n, v in feats.iter_rows() if v is not None}
    from validation import cache as _vc

    cur = pl.read_parquet(_vc.channel_consensus(channel),
                          columns=["nuclide"])["nuclide"].unique().to_list()
    out = []
    for nid in cur:
        if not (isinstance(nid, str) and nid.startswith("Z") and "N" in nid and "NAT" not in nid):
            continue
        try:
            z, n = int(nid[1:4]), int(nid[5:8])
        except ValueError:
            continue
        if not (z_min <= z <= z_max) or (z, n) not in me or (z, n + 1) not in me:
            continue
        out.append((z, n, me[(z, n)] + NEUTRON_ME_KEV - me[(z, n + 1)]))
    return sorted(out)


def chart_nuclides(z_min: int = 26, z_max: int = 92) -> list[tuple[int, int, float]]:
    """(Z, N, S_n of the compound) for every ground state in the feature table.

    Same contract as :func:`curated_nuclides`, without the requirement that anyone has ever
    measured capture on it — which is the requirement that keeps the model to 225 nuclides out
    of a chart of three and a half thousand, and the one the surrogate exists to lift. Stage B
    needs nothing per nuclide but (Z, N) and the compound's neutron separation energy, and S_n
    comes from the mass table: measured where AME has it, and from the WP-06 mass model's own
    extrapolation where it does not.

    A nuclide is included only when both (Z, N) and (Z, N+1) carry a mass excess; 3,439 of the
    3,558 ground states do. The rest sit at the edges of the table where even the compound's
    mass is unknown, and predicting capture on them would be predicting from nothing.
    """
    import polars as pl

    feats = pl.read_parquet(_data("features/nuclide_features.parquet"),
                            columns=["Z", "N", "target_mass_excess_kev"])
    me = {(int(z), int(n)): float(v) for z, n, v in feats.iter_rows() if v is not None}
    out = []
    for (z, n) in me:
        if not (z_min <= z <= z_max) or (z, n + 1) not in me:
            continue
        out.append((z, n, me[(z, n)] + NEUTRON_ME_KEV - me[(z, n + 1)]))
    return sorted(out)


def compound_id(nid: str) -> str:
    """The compound formed by capturing a neutron on this target: (Z, N) -> (Z, N+1).

    Resonance parameters, level densities at Sn and photon strengths are all properties of
    the compound, not of the target. The two are one neutron apart, so keying on the wrong
    one does not fail loudly -- it returns a plausible number from the neighbouring system.
    """
    try:
        z, n = int(nid[1:4]), int(nid[5:8])
    except (ValueError, IndexError):
        return nid
    return f"Z{z:03d}N{n + 1:03d}{nid[8:]}"


def resonance_features(ids: list[str]) -> np.ndarray:
    """Measured s-wave resonance parameters per nuclide, with availability flags.

    D0 (mean level spacing), Gamma_gamma (average radiative width) and S0 (s-wave strength
    function) come from RIPL-4, i.e. from resolved-resonance analyses of measurements — not
    from a reaction code. RIPL indexes them by the *compound* nucleus, which is the system
    whose levels are being spaced: capture on target (Z, N) forms (Z, N+1), so the lookup
    goes through compound_id. Keying on the target instead — as this did until 2026-09-10 —
    silently reads the neighbouring system's parameters: U-238 got D0 = 3.5 eV instead of
    20.3, Ta-181 got 1.2 instead of 4.2, and Au-197, Fe-56 and every other target whose own
    (Z, N) is absent from the table got nothing at all, flagged as absent. In the unresolved
    region the average capture cross section is set by
    2*pi*Gamma_gamma/D0, so these are not auxiliary features, they are the quantity itself.
    Unlike an evaluated library curve, they carry information the TALYS surrogate does not
    already contain.
    """
    import polars as pl

    f = _data("staging/structure_params.parquet")
    # every measured, near-target quantity the audit found — not the systematics-filled ones.
    # ld_a is the level-density parameter at the separation energy and is one of the three
    # parameters the identifiability analysis says cross sections can actually determine;
    # s1 and d1 are the p-wave counterparts of s0 and d0.
    # ld_a, s1 and d1 were added after the data audit surfaced them, and made things worse
    # (-4.2% overall, -1.8% on the nuclides carrying them): s1 covers 84 nuclides and d1 only
    # 43, so they arrive mostly as absent-flags and cost more in noise than they carry.
    cols = ["d0_ev", "gamma_gamma_mev", "s0"]
    # each parameter is a struct of (value, sigma, source); RIPL marks systematics-derived
    # entries, and only the measured ones are information the surrogate does not already have
    df = pl.read_parquet(f, columns=["nuclide_id", *cols]).select(
        "nuclide_id", *[pl.col(c).struct.field("value").alias(c) for c in cols],
        *[pl.col(c).struct.field("source").alias(c + "_src") for c in cols])
    table = {r["nuclide_id"]: r for r in df.iter_rows(named=True)}
    spec = (("d0_ev", 1.0, 3.0), ("gamma_gamma_mev", 1e3, 2.0), ("s0", 1e4, 0.0))
    out = np.zeros((len(ids), 2 * len(spec)), np.float32)
    for i, nid in enumerate(ids):
        r = table.get(compound_id(nid))
        for j, (col, scale, centre) in enumerate(spec):
            v = None if r is None else r.get(col)
            if r is not None and r.get(col + "_src") not in (None, "measured"):
                v = None
            if v is not None and np.isfinite(v) and v > 0:
                out[i, j] = (np.log10(v * scale) - centre) / 3.0   # keep inputs O(1)
                out[i, len(spec) + j] = 1.0                         # measured, not imputed
    return out


def thermal_features(ids: list[str]) -> np.ndarray:
    """The measured thermal capture cross section, the most precise number in nuclear data.

    At 0.0253 eV capture is measured to about 1%, against the 45% scatter between independent
    experiments in the fast region (docs/results/noise-floor.md). It anchors the absolute
    capture strength — sigma_thermal goes as Gamma_gamma / D — which is precisely what is
    uncertain where resonances are sparse, and sparse resonances are where this model is worst
    (error against measured D0: rho = +0.26, p = 9e-38).

    It is the same reaction on the same nucleus, six orders of magnitude below the grid we
    predict on, so it constrains the magnitude without leaking the answer.
    """
    import polars as pl

    f = _data("staging/exfor_all.parquet")
    lf = pl.scan_parquet(f)
    cols = lf.collect_schema().names()
    idcol = "target_id" if "target_id" in cols else "nuclide_id"
    df = (lf.filter((pl.col("mt") == 102) & (pl.col("projectile") == "n"))
          .select(idcol, "energy_ev", pl.col("renormalized").struct.field("values").alias("v"))
          .filter(pl.col("energy_ev").list.len() == pl.col("v").list.len())
          .explode(["energy_ev", "v"])
          .filter(pl.col("energy_ev").is_between(0.02, 0.03)
                  & pl.col("v").is_not_null() & (pl.col("v") > 1e-6) & (pl.col("v") < 1e6))
          .group_by(idcol).agg(pl.col("v").median().alias("sigma_th"))
          .collect())
    table = {r[idcol]: r["sigma_th"] for r in df.iter_rows(named=True)}
    out = np.zeros((len(ids), 2), np.float32)
    for i, nid in enumerate(ids):
        v = table.get(nid)
        if v is not None and np.isfinite(v) and v > 0:
            out[i, 0] = np.clip((np.log10(v) - 0.5) / 2.0, -2.0, 2.0)
            out[i, 1] = 1.0
    return out


def qrpa_features(ids: list[str]) -> np.ndarray:
    """Microscopic photon strength (D1M+QRPA) and measured giant-dipole parameters.

    Capture needs two things: how many states the compound can decay through, and how readily
    it emits the gamma. The level density is the first and came from BSkG3+combinatorial
    (+5.6%); this is the second. The radiative-width integral is computed from the D1M Gogny
    interaction with QRPA, never fitted to a cross section — the same independence that made
    the level densities work and the evaluated libraries useless.

    Also carried: the *experimentally measured* giant-dipole energy and width, from RIPL's
    recommended photoabsorption compilation. Earlier the GDR parameters did nothing because
    8,845 of 8,980 were systematics; these 174 are measurements.
    """
    from physics.abinitio.qrpa_strength import gamma_strength_at

    sn = {f"Z{z:03d}N{n:03d}M0": s_ * 1e-3 for z, n, s_ in curated_nuclides(1, 120)}
    got = gamma_strength_at([(nid, sn.get(nid, float("nan"))) for nid in ids])

    exp: dict[tuple[int, int], tuple[float, float]] = {}
    f = _data("raw/ripl4/RIPL-4/gamma/gdr_parameters_recommended_exp_slo.dat")
    if f.exists():
        for line in f.read_text(errors="replace").splitlines():
            if line.startswith("#") or len(line) < 40:
                continue
            try:
                z, a = int(line[0:4]), int(line[4:8])
                er, wr = float(line[13:21]), float(line[21:29])
            except ValueError:
                continue
            if np.isfinite(er) and er > 0:
                exp[(z, a)] = (er, wr)

    out = np.zeros((len(ids), 6), np.float32)
    for i, nid in enumerate(ids):
        r = got.get(nid)
        if r:
            out[i, 0] = (r["log10_gamma_integral"] + 4.5) / 2.0     # centred, O(1)
            out[i, 1] = (r["peak_energy_mev"] - 8.0) / 4.0
            out[i, 2] = 1.0
        try:
            z, n = int(nid[1:4]), int(nid[5:8])
        except ValueError:
            continue
        e = exp.get((z, z + n))            # the target's own measured photoabsorption
        if e:
            out[i, 3] = (e[0] - 15.0) / 5.0
            out[i, 4] = (e[1] - 5.0) / 3.0
            out[i, 5] = 1.0
    return out


def fission_features(ids: list[str]) -> np.ndarray:
    """Whether fission competes with capture, and by how much.

    Bi-209 and U-233 carry 76% of the squared error in the actinide region. Bi-209 is the
    closed-shell problem (Z=83, N=126). U-233 is different: it is fissile, so the compound
    nucleus can fission instead of emitting a gamma, and capture is suppressed by Gamma_f in
    the denominator. Nothing in this model knows that fission exists — the surrogate carries
    no fission channel and the residual has no feature for it.

    The physically meaningful quantity is Sn minus the fission barrier: positive means the
    compound is above the barrier the moment it forms, which is what "fissile" means.
    """
    import polars as pl

    sn = {f"Z{z:03d}N{n:03d}M0": s_ * 1e-3 for z, n, s_ in curated_nuclides(1, 120)}
    d = pl.read_parquet(_data("staging/structure_params.parquet")).select(
        "nuclide_id",
        pl.col("fission_barriers").list.first().struct.field("height_mev")
        .struct.field("value").alias("barrier"))
    bar = {r["nuclide_id"]: r["barrier"] for r in d.iter_rows(named=True)}
    out = np.zeros((len(ids), 3), np.float32)
    for i, nid in enumerate(ids):
        b_, s_ = bar.get(nid), sn.get(nid)
        if b_ is None or s_ is None or not np.isfinite(b_) or not np.isfinite(s_):
            continue
        out[i, 0] = np.clip((s_ - b_) / 3.0, -2.0, 2.0)   # above the barrier at zero energy
        out[i, 1] = np.clip((b_ - 6.0) / 3.0, -2.0, 2.0)  # barrier height, centred
        out[i, 2] = 1.0                                    # a barrier is tabulated at all
    return out


def hfb_features(ids: list[str]) -> np.ndarray:
    """Microscopic level density at Sn, and ground-state deformation, from BSkG3+combinatorial.

    Calculated from a Skyrme Hartree-Fock-Bogoliubov single-particle scheme by counting states,
    for 7,677 nuclei — not fitted to any cross section. This is the test that separates two
    readings of what has worked here: measured D0 and Gamma_gamma helped (+2.2%), while the
    evaluated libraries did nothing (+0.4%). If the operative property is *measurement*, this
    should do nothing. If it is *independence from the reaction code*, it should help, because
    it is calculated but independent.
    """
    from physics.abinitio.hfb_levels import level_density_at

    sn = {f"Z{z:03d}N{n:03d}M0": s_ * 1e-3 for z, n, s_ in curated_nuclides(1, 120)}
    got = level_density_at([(nid, sn.get(nid, float("nan"))) for nid in ids])
    out = np.zeros((len(ids), 3), np.float32)
    for i, nid in enumerate(ids):
        r = got.get(nid)
        if not r:
            continue
        out[i, 0] = (r["log10_rho_sn"] - 5.0) / 3.0     # centred, keeps inputs O(1)
        out[i, 1] = np.clip(r["beta2"] / 0.3, -1.5, 1.5)
        out[i, 2] = 1.0                                  # present, not imputed
    return out


MAGIC = (2, 8, 20, 28, 50, 82, 126)


def shell_features(ids: list[str]) -> np.ndarray:
    """Distance to the nearest closed shell, which is not a smooth function of (Z, N).

    The residual conditions on a PCA of the chart embedding, which is smooth by construction,
    so neighbouring nuclides receive nearly the same correction. Nuclear structure is not smooth:
    it has cliffs at the magic numbers and a sawtooth from pairing. Measured, the model is
    smoother than nature in three independent ways - shell-closure dips 1.6x too shallow, the
    odd-even staggering compressed, and second differences along isotopic chains at 0.82 of the
    measured roughness. These features give it somewhere to put a cliff.

    Columns: signed and absolute distance to the nearest magic N, the same for Z, and an
    indicator for sitting within one of a closure in either.
    """
    out = np.zeros((len(ids), 5), np.float32)
    for i, nid in enumerate(ids):
        try:
            z, n = int(nid[1:4]), int(nid[5:8])
        except ValueError:
            continue
        dn = min(MAGIC, key=lambda m: abs(n - m))
        dz = min(MAGIC, key=lambda m: abs(z - m))
        out[i, 0] = np.clip((n - dn) / 8.0, -1.5, 1.5)      # signed: above or below the shell
        out[i, 1] = min(abs(n - dn), 12) / 12.0
        out[i, 2] = np.clip((z - dz) / 8.0, -1.5, 1.5)
        out[i, 3] = min(abs(z - dz), 12) / 12.0
        out[i, 4] = 1.0 if (abs(n - dn) <= 1 or abs(z - dz) <= 1) else 0.0
    return out


def pairing_features(ids: list[str]) -> np.ndarray:
    """Whether the target has an odd neutron, and the compound's separation energy.

    Add a neutron to an odd-N target and the compound gains pairing energy: its separation
    energy is higher, the level density at that energy is higher, and capture is larger. That
    is the odd-even staggering the s-process runs on. Measured on this model, the bias is
    +0.013 in log10 for even-A targets and -0.004 for odd-A (p = 1.6e-10) — it compresses the
    staggering, the same way it underestimates every shell-closure dip by a factor of 1.6. Both
    are an interpolating model smoothing structure it was never told exists.
    """
    sn = {(z, n): s_ for z, n, s_ in curated_nuclides(1, 120)}
    out = np.zeros((len(ids), 3), np.float32)
    for i, nid in enumerate(ids):
        try:
            z, n = int(nid[1:4]), int(nid[5:8])
        except ValueError:
            continue
        out[i, 0] = 1.0 if n % 2 else -1.0          # odd neutron number in the target
        out[i, 1] = 1.0 if z % 2 else -1.0          # odd proton number
        v = sn.get((z, n))
        if v is not None and np.isfinite(v):
            out[i, 2] = (v * 1e-3 - 7.0) / 3.0      # compound Sn in MeV, centred
    return out


def structure_features(ids: list[str]) -> np.ndarray:
    """The two functions Hauser-Feshbach actually needs, measured, for every nuclide.

    A capture cross section is not a fundamental quantity: it is what you get when a level
    density and a gamma-strength function are put through the statistical model. Those two are
    measured far more widely than cross sections are — constant-temperature level-density fits
    to counted discrete levels exist for 3,240 nuclides and giant-dipole parameters for 9,373,
    against 516 nuclides with any capture measurement at all. Conditioning on them is not
    feature engineering; it is giving the model the inputs the physics uses.

    Columns: level-density temperature and E0, the number and energy span of counted discrete
    levels, and the first giant-dipole resonance's energy, width and peak.
    """
    import polars as pl

    d = pl.read_parquet(_data("staging/structure_params.parquet"))
    counts = pl.read_parquet(_data("staging/level_counts.parquet"),
                             columns=["nuclide_id", "n_levels", "e_max_kev"])
    d = d.join(counts, on="nuclide_id", how="left")
    rows = {}
    for r in d.select(
        "nuclide_id",
        pl.col("ct_temperature_mev").struct.field("value").alias("T"),
        pl.col("ct_e0_mev").struct.field("value").alias("E0"),
        "n_levels", "e_max_kev",
    ).iter_rows(named=True):
        rows[r["nuclide_id"]] = r

    # RIPL marks each value measured or systematics. 8,845 of 8,980 giant-dipole entries are
    # systematics — a global formula in (Z, A), which the chart embedding already contains, so
    # including them adds nothing and dilutes what does. Only measured quantities are kept:
    # the constant-temperature fit and the counted levels behind it.
    spec = (("T", 0.7, 0.5), ("E0", 0.0, 2.0), ("n_levels", 40.0, 60.0),
            ("e_max_kev", 3000.0, 3000.0))
    out = np.zeros((len(ids), len(spec)), np.float32)
    for i, nid in enumerate(ids):
        r = rows.get(nid)
        if r is None:
            continue
        for j, (col, centre, scale) in enumerate(spec):
            v = r.get(col)
            if v is not None and np.isfinite(v):
                out[i, j] = (float(v) - centre) / scale     # keep inputs O(1)
    return out


def urr_norm_features(ids: list[str]) -> np.ndarray:
    """2*pi*Gamma_gamma/D0 -- the unresolved-region capture normalisation itself.

    resonance_features hands the model log D0 and log Gamma_gamma as separate columns with
    separate absent-flags, and it is worth +0.0% in the register (20 seeds, t=-0.1). The
    quantity the physics uses is neither column but their ratio: in the unresolved region the
    average capture cross section goes as 2*pi*Gamma_gamma/D0, so the model has been asked to
    learn a difference of two logs -- each separately centred and scaled, each separately
    maskable -- from 225 nuclides, and it has not.

    The diagnosis this answers (docs/results/beat-tendl.json): against TENDL our odd-A error
    is a per-nuclide *normalisation* error, spread 0.1115 against their 0.0665, while our
    shape is better than theirs. Magnitude is exactly what this ratio sets. The column is
    only defined where both parameters are measured, so it carries its own flag and the
    separate columns stay -- this adds the combination, it does not replace the ingredients.
    """
    import polars as pl

    f = _data("staging/structure_params.parquet")
    cols = ["d0_ev", "gamma_gamma_mev"]
    df = pl.read_parquet(f, columns=["nuclide_id", *cols]).select(
        "nuclide_id", *[pl.col(c).struct.field("value").alias(c) for c in cols],
        *[pl.col(c).struct.field("source").alias(c + "_src") for c in cols])
    table = {r["nuclide_id"]: r for r in df.iter_rows(named=True)}
    out = np.zeros((len(ids), 2), np.float32)
    for i, nid in enumerate(ids):
        r = table.get(compound_id(nid))
        if r is None:
            continue
        if any(r.get(c + "_src") not in (None, "measured") for c in cols):
            continue
        d0, gg = r.get("d0_ev"), r.get("gamma_gamma_mev")
        if not (d0 and gg and np.isfinite(d0) and np.isfinite(gg) and d0 > 0 and gg > 0):
            continue
        # Gamma_gamma is in meV, D0 in eV: the ratio is dimensionless once both are in eV.
        ratio = 2.0 * np.pi * (gg * 1e-3) / d0
        out[i, 0] = (np.log10(ratio) + 2.0) / 2.0    # keep inputs O(1)
        out[i, 1] = 1.0                              # both measured, ratio is real
    return out


# Feature blocks appended to the encoder embedding, in a fixed order. Both the measurement
# bundle and the library pre-training bundle assemble their embedding through this, so a
# warm start actually transfers: build them with different flags and the state dict will
# not load.
FEATURE_BLOCKS = ("resonance", "urr_norm", "structure", "pairing", "shells", "hfb",
                  "fission", "qrpa", "thermal", "n2n", "inelastic_threshold", "target_spin",
                  "m1_strength", "noise_control", "noise_control4")



def _psf_scale_arg() -> float | dict[str, float] | None:
    """Read INCOGNITA_PSF_SCALE into the `gsf_norm` argument of the Stage B prior.

    Values: unset (TALYS default, 1.0), a number (global scale), or "per-nuclide" to read the
    inferred per-nuclide table. The per-nuclide values are noisy -- 16-84 percentile 0.63-4.20 --
    so they are clipped to the sweep's own range and anything absent falls back to the global
    median rather than to 1.0, since the global correction is the better-supported claim.
    """
    v = _env("PSF_SCALE", "")
    if not v:
        return None
    if v.strip().lower() not in ("per-nuclide", "per_nuclide"):
        return float(v)
    import polars as pl

    path = _data("curated/psf-normalisation.parquet")
    if not path.exists():
        return None
    d = pl.read_parquet(path)
    med = float(d["psf_scale"].median())
    out: dict[str, float] = {}
    for r in d.iter_rows(named=True):
        z, a_ = int(r["Z"]), int(r["A"])
        out[f"Z{z:03d}N{a_ - z:03d}M0"] = float(min(max(r["psf_scale"], 0.5), 2.0))
    out["__default__"] = med
    return out


def n2n_features(ids: list[str]) -> np.ndarray:
    """What makes (n,2n) a different problem from capture: a threshold and two competitors.

    Every feature Stage C had was built for capture, where the cross section is finite at
    thermal energy and falls smoothly. (n,2n) does not exist below a threshold, rises over a
    few MeV, and is then cut off from above when (n,3n) opens. None of the capture features
    describes any of that, and the first (n,2n) residual was trained without them.

    Four numbers, all from the AME mass excesses already in the feature table:

      0  threshold energy in MeV, centred. Removing a neutron from the target (Z, A) costs
         S_n(Z, A), and in the lab frame that is (A+1)/A times the CM value. This is the
         single most important number for the channel: below it the cross section is zero.
      1  S_2n of the target, which sets where (n,3n) opens and starts taking flux away.
      2  the gap between them, S_2n - S_n: how wide the window is in which (n,2n) is the
         dominant neutron-emission channel.
      3  S_p - S_n of the compound, the proxy for (n,p) competition: a proton-rich compound
         with a low proton separation energy loses flux to charged-particle emission, which
         is why (n,2n) is weak on the proton-rich side of stability.

    A missing mass leaves the row at zero, which is the same convention every other block
    here uses, and is why they are all centred: zero means "no information", not "zero MeV".
    """
    import polars as pl

    feats = pl.read_parquet(_data("features/nuclide_features.parquet"),
                            columns=["Z", "N", "target_mass_excess_kev"])
    me = {(int(z), int(n)): float(v) for z, n, v in feats.iter_rows() if v is not None}
    ME_N = 8071.31806          # neutron mass excess, keV (AME2020)
    ME_H = 7288.97106          # 1H mass excess, keV

    def s_n(z: int, n: int) -> float | None:
        """Neutron separation energy of (Z, N), keV."""
        a, b = me.get((z, n - 1)), me.get((z, n))
        return None if (a is None or b is None) else a + ME_N - b

    def s_2n(z: int, n: int) -> float | None:
        a, b = me.get((z, n - 2)), me.get((z, n))
        return None if (a is None or b is None) else a + 2 * ME_N - b

    def s_p(z: int, n: int) -> float | None:
        a, b = me.get((z - 1, n)), me.get((z, n))
        return None if (a is None or b is None) else a + ME_H - b

    out = np.zeros((len(ids), 4), np.float32)
    for i, nid in enumerate(ids):
        try:
            z, n = int(nid[1:4]), int(nid[5:8])
        except ValueError:
            continue
        a_mass = z + n
        sn_t = s_n(z, n)
        if sn_t is not None and np.isfinite(sn_t) and a_mass > 0:
            e_thr = sn_t * 1e-3 * (a_mass + 1.0) / a_mass       # MeV, lab frame
            out[i, 0] = (e_thr - 9.0) / 3.0                      # typical threshold ~7-12 MeV
        s2 = s_2n(z, n)
        if s2 is not None and np.isfinite(s2):
            out[i, 1] = (s2 * 1e-3 - 15.0) / 4.0
            if sn_t is not None and np.isfinite(sn_t):
                out[i, 2] = ((s2 - sn_t) * 1e-3 - 7.0) / 3.0
        # the compound of n + (Z, N) is (Z, N+1)
        spc, snc = s_p(z, n + 1), s_n(z, n + 1)
        if None not in (spc, snc) and np.isfinite(spc) and np.isfinite(snc):
            out[i, 3] = ((spc - snc) * 1e-3) / 5.0
    return out


def inelastic_features(ids: list[str]) -> np.ndarray:
    """Where inelastic scattering opens and starts taking flux away from capture.

    Above the first excited state of the *target* the (n,n') channel opens and competes with
    capture for the compound nucleus. No block here carries that threshold: `structure` has the
    level density and gamma strength, `resonance` the compound's D0/Gamma_gamma, and
    `n2n_features` the S_n/S_2n thresholds -- all of which are several MeV up. The first level
    is two orders of magnitude lower, and in the deformed rare earths it sits below 150 keV,
    which is exactly the decade where this model loses to TENDL by 41% on Sn-Pb
    (docs/results/best-by-a-lot-audit.md) with a per-nuclide *normalisation* error.

    Two numbers, both of the target, not the compound -- it is the target that gets excited:

      0  log10 E(first excited level) in keV, centred. The threshold itself. Taken at any
         spin, deliberately: E(2+) exists only for even-even nuclei, and the nuclides this
         block is aimed at -- Tb-159, Tm-169, I-127, Pt-195 -- are odd-A, where the first
         level is a rotational or single-particle state at tens of keV. An E(2+) column would
         be exactly zero on every nuclide the block was built for.
      1  R42 = E(4+)/E(2+), the textbook collectivity discriminant: ~2.0 for a vibrational
         nucleus, ~3.33 for a good rotor. It says how fast the band drains flux once the first
         level is open, which the threshold alone does not. Even-even only, hence its own flag.

    Both come from the counted ENSDF levels in staging/levels.parquet, restricted to levels
    with an unambiguous J-pi assignment, so a tentative spin never sets a threshold. Columns
    2-3 are the matching measured-not-imputed flags, on the same convention as
    resonance_features: zero means "no information", not "zero keV".
    """
    import polars as pl

    lv = pl.read_parquet(_data("staging/levels.parquet"),
                         columns=["nuclide_id", "level_index", "energy_kev", "energy_offset",
                                  "j_values", "parities", "j_unique"])
    # level_index 1 is the ground state; an excited level is index > 1 at non-zero energy.
    # A non-null energy_offset (e.g. "SN") means energy_kev is quoted relative to that offset, not
    # to the ground state: Os-190's lowest such row is a 6.7 eV resonance above S_n, which the
    # unfiltered min() took as E(2+) (log10 -4.67 instead of 186.7 keV's -0.23). AUDIT2, 2026-09-13.
    ex = lv.filter((pl.col("level_index") > 1) & (pl.col("energy_kev") > 0)
                   & pl.col("energy_offset").is_null())
    first = {r["nuclide_id"]: r["e"] for r in
             ex.group_by("nuclide_id").agg(e=pl.col("energy_kev").min()).iter_rows(named=True)}

    def lowest(j: float) -> dict[str, float]:
        d = ex.filter(pl.col("j_unique") & pl.col("j_values").list.contains(j)
                      & pl.col("parities").list.contains(1))
        d = d.group_by("nuclide_id").agg(e=pl.col("energy_kev").min())
        return {r["nuclide_id"]: r["e"] for r in d.iter_rows(named=True)}

    e2, e4 = lowest(2.0), lowest(4.0)
    out = np.zeros((len(ids), 4), np.float32)
    for i, nid in enumerate(ids):
        v1 = first.get(nid)
        if v1 is not None and np.isfinite(v1) and v1 > 0:
            out[i, 0] = (np.log10(v1) - 2.5) / 1.0    # 10 keV -> -1.5, 3 MeV -> +1.0
            out[i, 2] = 1.0
        v2, v4 = e2.get(nid), e4.get(nid)
        if None not in (v2, v4) and np.isfinite(v2) and np.isfinite(v4) and v2 > 0:
            out[i, 1] = (v4 / v2 - 2.5) / 0.7         # R42, centred between vib and rot
            out[i, 3] = 1.0
    return out

def target_spin_features(ids: list[str]) -> np.ndarray:
    """The target's ground-state spin and parity, which set the entrance-channel weight.

    A neutron captured on a target of spin I forms the compound at J = I +/- 1/2 for s-wave,
    and the statistical weight of that channel is g = (2J+1)/(2(2I+1)). The (2I+1) is a
    first-order factor in every Hauser-Feshbach capture cross section and no block here carries
    it: `pairing` knows only the *parity* of N and Z, `structure` has the level-density spin
    cutoff (the width of the spin distribution, not the target's own J), and `resonance` has D0,
    which is itself quoted per-J and so presupposes the number this block supplies.

    It is also information the chart encoder cannot interpolate. Ground-state J is the odd
    nucleon's orbital -- 1/2, 3/2, ... 9/2 with no smooth dependence on (Z, N) -- so a 3x3
    convolution over neighbours has nothing to average. It is identically 0 on even-even
    targets, which means the entire information content sits on odd-A, and odd-A is where this
    model's deficit against TENDL is a per-nuclide *normalisation* error (0.1115 against their
    0.0665, see urr_norm_features).

    Three columns, all of the target, not the compound:

      0  log10(2I+1), centred: the entrance-channel statistical weight itself.
      1  ground-state parity, +1 or -1.
      2  the measured-not-imputed flag, on the resonance_features convention.
    """
    import polars as pl

    df = pl.read_parquet(_data("staging/nuclides.parquet"),
                         columns=["nuclide_id", "spin", "parity", "iso"]).filter(pl.col("iso") == 0)
    table = {r["nuclide_id"]: r for r in df.iter_rows(named=True)}
    out = np.zeros((len(ids), 3), np.float32)
    for i, nid in enumerate(ids):
        r = table.get(nid)
        if r is None:
            continue
        j, par = r.get("spin"), r.get("parity")
        if j is None or not np.isfinite(j) or j < 0:
            continue
        out[i, 0] = (np.log10(2.0 * j + 1.0) - 0.5) / 0.5   # I=0 -> -1, I=9/2 -> +1
        out[i, 1] = 1.0 if (par or 0) > 0 else (-1.0 if (par or 0) < 0 else 0.0)
        out[i, 2] = 1.0
    return out


def m1_strength_features(ids: list[str]) -> np.ndarray:
    """Microscopic M1 photon strength (D1M+QRPA): the half of the gamma cascade qrpa omits.

    A radiative width is E1 plus M1. `qrpa_features` carries only the E1 giant dipole, yet the
    same D1M+QRPA archive ships the M1 tables for the same 103 proton chains -- the scissors
    mode and the spin-flip resonance, plus the finite-temperature low-energy upbend -- and
    nothing here reads them. M1 is 10-20% of the integrated strength, and it is the component
    that varies with deformation, so it is not a constant that the E1 column already stands in
    for.

    It is also the kind of feature that has actually worked here. The register splits cleanly:
    every block that helps is a microscopic prediction never fitted to a cross section (qrpa
    +4.4%, hfb +1.7%, fission +1.0%), while every block carrying a measured per-nuclide constant
    is null or worse -- `thermal` -1.9% and `target_spin` -0.6%, both significant. This is on
    the microscopic side of that line: the sweep varies `strength` and the gsf scale factors,
    but nothing in PARAM_NAMES supplies a nuclide-specific M1 shape.

    Three columns:

      0  log10 of the M1 radiative-width integral at S_n, centred.
      1  log10(M1/E1) -- the M1 share of the width, which is the physically meaningful
         combination and is scaled far tighter than either integral alone (sd 0.22 vs 0.43).
      2  the measured-not-imputed flag.
    """
    import polars as pl

    from physics.abinitio.qrpa_strength import gamma_strength_at

    df = pl.read_parquet(_data("staging/nuclides.parquet"),
                         columns=["nuclide_id", "sn_kev", "iso"]).filter(pl.col("iso") == 0)

    def _v(x):
        return x.get("value") if isinstance(x, dict) else x

    sn = {r["nuclide_id"]: (_v(r["sn_kev"]) or 0.0) / 1000.0 for r in df.iter_rows(named=True)}
    req = [(nid, sn.get(nid, float("nan"))) for nid in ids]
    e1 = gamma_strength_at(req, "e1")
    m1 = gamma_strength_at(req, "m1")

    out = np.zeros((len(ids), 3), np.float32)
    for i, nid in enumerate(ids):
        rm, re = m1.get(nid), e1.get(nid)
        if not rm:
            continue
        out[i, 0] = (rm["log10_gamma_integral"] + 4.9) / 0.45
        out[i, 2] = 1.0
        if re:
            out[i, 1] = ((rm["log10_gamma_integral"] - re["log10_gamma_integral"]) + 0.97) / 0.22
    return out


def noise_control_features(ids: list[str]) -> np.ndarray:
    """Three columns of deterministic noise: the control every feature block needed.

    Three physically motivated blocks were added on 2026-09-12 and all three failed --
    `inelastic_threshold` null below 0.85%, `target_spin` -0.59%, `m1_strength` -2.25% at
    t=-7.1. Each failure was read as a statement about its physics. That reading is only valid
    if a column carrying NO information is harmless, and nothing in the register had ever
    checked it.

    This block is the check: same column count as m1_strength, same O(1) scale, same
    100% "measured" flag, and zero information -- the values are a hash of the nuclide id, so
    they are fixed across seeds and arms (a resampled column would measure something else) and
    uncorrelated with anything physical.

    If this costs as much as the physics blocks did, then those results are about Stage C's
    capacity at 225 nuclides and not about level schemes, spins or M1 strength, and the right
    response is to stop adding columns rather than to keep looking for better ones.
    """
    out = np.zeros((len(ids), 3), np.float32)
    for i, nid in enumerate(ids):
        h = hashlib.sha256(nid.encode()).digest()
        # two O(1) values in roughly the same range as a centred physics column, plus the flag
        out[i, 0] = (int.from_bytes(h[0:4], "big") / 2**32 - 0.5) * 2.0
        out[i, 1] = (int.from_bytes(h[4:8], "big") / 2**32 - 0.5) * 2.0
        out[i, 2] = 1.0
    return out


def noise_control4_features(ids: list[str]) -> np.ndarray:
    """A width-matched noise control for `inelastic_threshold`, which is a 4-column block.

    F0 measured the control at THREE columns (`noise_control`, -1.13% over 200 paired seeds)
    and `noise-control-verdict.md` then priced `inelastic_threshold`'s four columns at
    4/3 x that. F1 measured the same physics through the tax-free `lift_sigma` route at -0.67%
    with a 95% interval that EXCLUDES the +2.06% excess that extrapolation implies, so either
    the tax is not linear in column count or the two routes carry different things. The
    extrapolation is the suspect part; this block removes it by measuring the 4-column tax
    instead of predicting it.

    The control is `inelastic_features` itself, with the rows DERANGED across nuclides: sort
    the nuclides by a SHA-256 of the id and give each one the block of the next nuclide in
    that order. Every nuclide gets somebody else's first excited level and R42, wrapped in
    somebody else's coverage flags.

    Why a derangement and not four more columns of uniform hash, which is what F0 used:

    * It matches the block it controls for EXACTLY -- same four columns, same marginal
      distribution in each, same sparsity (223 of 225 rows carry a threshold, the R42 pair only
      the even-even ones), same pairing of value with flag. A moment-matched uniform would not:
      column 1 is R42 and has a heavy tail (a few nuclides with a very low first 2+ read in the
      hundreds), so a uniform with its standard deviation would hand EVERY covered row a value
      the real block gives to three, and the control would lose for being a worse input rather
      than for being uninformative.
    * The information it removes is exactly the information under test -- which nuclide has
      which level scheme. Nothing else about the block changes.

    The derangement is a fixed function of the nuclide ids, so it is identical across seeds and
    arms and does not depend on the order the ids arrive in. `noise_control` (three columns of
    uniform hash) is left exactly as F0 ran it; this is a second block, not a replacement.
    """
    real = inelastic_features(ids)
    n = len(ids)
    if n < 2:
        return real.copy()
    # hash order, then a shift by one in it: deterministic, independent of the input order,
    # and a derangement -- no nuclide keeps its own row
    order = sorted(range(n), key=lambda i: hashlib.sha256(f"noise4:{ids[i]}".encode()).digest())
    out = np.zeros_like(real)
    for k, i in enumerate(order):
        out[i] = real[order[(k + 1) % n]]
    return out


def first_level_ev(ids: list[str]) -> np.ndarray:
    """First excited level of the TARGET in eV, 0 where no level is counted.

    Same source and same cut as `inelastic_features` column 0 -- the lowest ENSDF level above
    the ground state with an unambiguous J-pi -- but returned as a threshold energy rather than
    a centred scalar, because it is consumed as a per-energy channel and not as an embedding
    column. Zero means "not counted"; StageCBundle turns it into a flat channel rather than a
    threshold at 1 eV.
    """
    import polars as pl

    lv = pl.read_parquet(_data("staging/levels.parquet"),
                         columns=["nuclide_id", "level_index", "energy_kev", "j_unique"])
    ex = lv.filter((pl.col("level_index") > 1) & (pl.col("energy_kev") > 0)
                   & pl.col("j_unique"))
    first = {r["nuclide_id"]: r["e"] for r in
             ex.group_by("nuclide_id").agg(e=pl.col("energy_kev").min()).iter_rows(named=True)}
    out = np.zeros(len(ids), np.float64)
    for i, nid in enumerate(ids):
        v = first.get(nid)
        if v is not None and np.isfinite(v) and v > 0:
            out[i] = float(v) * 1e3
    return out


def assemble_embedding(ids: list[str], base: np.ndarray, **flags: bool) -> np.ndarray:
    """Append every enabled physics feature block to `base`, in FEATURE_BLOCKS order."""
    fns = {"resonance": resonance_features, "urr_norm": urr_norm_features,
           "structure": structure_features,
           "pairing": pairing_features, "shells": shell_features, "hfb": hfb_features,
           "fission": fission_features, "qrpa": qrpa_features,
           "thermal": thermal_features, "n2n": n2n_features,
           "inelastic_threshold": inelastic_features,
           "target_spin": target_spin_features,
           "m1_strength": m1_strength_features,
           "noise_control": noise_control_features,
           "noise_control4": noise_control4_features}
    emb = base
    for name in FEATURE_BLOCKS:
        if flags.get(name):
            emb = np.concatenate([emb, fns[name](ids)], axis=1)
    return emb


def build_bundle(
    *,
    surrogate_ckpt: Path | None = None,
    # "" (default) = no teacher library is loaded (INCOGNITA v0.1: no library value in training); name one to opt in
    teacher_key: str = "",
    year_cutoff: int = 2012,
    e_min_ev: float = 1e3,
    e_max_ev: float = 2e7,
    n_energy: int = 64,
    embed_dim: int = 16,
    embeddings: str = "encoder",
    resonance: bool = True,    # measured D0/Gg/S0 help (+2.2% overall, +3.5% where present)
    urr_norm: bool = False,    # 2*pi*Gg/D0, the normalisation itself: under test 2026-09-10
    structure: bool = False,   # measured level density and gamma strength: see structure_features
    pairing: bool = True,      # parity of N and the compound's Sn: see pairing_features
    shells: bool = True,       # distance to the nearest closed shell: see shell_features
    hfb: bool = True,          # microscopic level density at Sn: see hfb_features (+5.6%)
    fission: bool = True,      # does fission compete with capture: see fission_features
    qrpa: bool = True,         # microscopic photon strength + measured GDR: see qrpa_features
    # target E(2+) and R42. ON by default since 2026-09-13: F3 +1.69% vs its width-matched
    # control, F5 +1.21% at members=5 (docs/results/power/). None reads
    # INCOGNITA_INELASTIC_THRESHOLD at CALL time (default 1); the reproduce scripts of models
    # trained before the flip set it to 0 so they rebuild byte-for-byte.
    inelastic_threshold: bool | None = None,
    target_spin: bool = False,          # target ground-state J and parity: HURTS, see docs
    m1_strength: bool = False,          # microscopic D1M+QRPA M1: HURTS -2.25%, see docs
    noise_control: bool = False,        # zero-information control for the blocks above
    noise_control4: bool = False,       # the same control at four columns: see F3
    # Not an embedding block: this one enters as a second per-energy channel. See the comment
    # at the construction site below.
    inelastic_channel: bool = False,
    urr_channel: bool = False,
    # measured 2026-09-10: the thermal anchor is neutral overall and cost Sn-Pb its lead
    # (0.123 -> 0.131). At 44 embedding dimensions on 225 nuclides, features now move error
    # between regions rather than removing it.
    thermal: bool = False,     # measured 2200 m/s cross section: see thermal_features
    # None = on for (n,2n) and off for capture, which is the only sensible default: the block
    # is the threshold and its competitors, and capture has no threshold. Pass True/False to
    # override, which is what an ablation needs.
    n2n: bool | None = None,   # threshold, S_2n, the (n,2n) window, (n,p) competition
    # Restrict the bundle to a slice of the chart. A per-region Stage C is the only way to
    # test whether joint training is what stops a per-region Stage B from paying off: the
    # region split via INCOGNITA_SURROGATE_MAP kept one residual over all three regions, so the
    # correction learned in Sn-Pb still depended on Stage B in Fe-Sn.
    z_min: int = 26,
    z_max: int = 92,
    nuclides: str = "sweep",
    # WP-19: which reaction this bundle is for. `mt` selects the channel out of the Stage B,
    # teacher and surrogate prediction sets (all of them are keyed (nuclide, mt)); `channel`
    # selects which curated measurement tables to score against. They are separate arguments
    # because MT is an ENDF number and the channel is a curation tag, and nothing guarantees
    # a one-to-one map for future channels.
    mt: int = 102,
    # The surrogate names its outputs ("capture", "n2n", ...) and maps them to MT itself, the
    # curation names its tables by the same strings, and the two must agree or Stage B would
    # silently be the capture curve scored against (n,2n) measurements. Asserted below.
    channel: str = "capture",
    # True keeps only nuclides with a differential measurement; "or_macs" also keeps nuclides
    # whose only capture datum is a KADoNiS Maxwellian average; False keeps everything, which
    # is what inference over the whole chart needs.
    require_measurements: bool | str = True,
    embedding_basis: list[str] | None = None,
    # "teacher" = the teacher library's own resolved-resonance bound (what every run before
    # 2026-09-11 used); "canonical" = the maximum over the evaluated libraries. See the comment
    # at the assignment below for why the difference is not cosmetic. None reads INCOGNITA_RRR_POLICY
    # at CALL time -- a default of _env(...) would be evaluated once at import and freeze whatever
    # the environment happened to be when the module was first loaded.
    rrr_policy: str | None = None,
    device: str = "cpu",
) -> StageCBundle:
    """Assemble measurements, Stage B, teacher and the time split onto one grid.

    ``require_measurements`` is what separates training from inference. Training needs a
    target, so a nuclide nobody has measured cannot be in the bundle; inference does not, and
    dropping it there is what confined the model to the 225 nuclides that happen to have EXFOR
    data. Pass False with ``nuclides="chart"`` to build over the whole chart instead. Every
    physics feature already arrives as a (value, was-it-measured) pair, so a nuclide with no
    resonance parameters is handled the same way the trained ones with none were.
    """
    if inelastic_threshold is None:
        inelastic_threshold = inelastic_threshold_default()
    surrogate_ckpt = surrogate_ckpt or _ckpt(
        f"models/surrogate/checkpoints/talys-surrogate-{SURROGATE_TAG}.pt")
    grid = _grid(e_min_ev, e_max_ev, n_energy)

    rrr: dict[str, float] = {}
    _CH_MT = {"capture": 102, "total": 1, "elastic": 2, "inelastic": 4,
              "n2n": 16, "np": 103, "na": 107}
    if channel not in _CH_MT:
        raise ValueError(f"unknown channel {channel!r}; the surrogate knows {sorted(_CH_MT)}")
    if _CH_MT[channel] != mt:
        raise ValueError(
            f"channel {channel!r} is MT {_CH_MT[channel]}, but mt={mt} was requested. "
            "Mismatching them would score one reaction's Stage B against another's "
            "measurements, which reads as a very bad model rather than as an error."
        )
    if n2n is None:
        n2n = channel == "n2n"
    picked = (curated_nuclides(z_min, z_max, channel=channel) if nuclides == "curated"
              else chart_nuclides(z_min, z_max) if nuclides == "chart"
              else curated_plus_macs(z_min, z_max, channel=channel)
              if nuclides == "curated+macs" else None)
    # INCOGNITA_PSF_SCALE moves the Stage B prior's photon strength function off the TALYS
    # default. "1.347" applies the global correction measured in psf-normalisation.md; "per
    # nuclide" reads curated/psf-normalisation.parquet and applies each nuclide's own inferred
    # scale, falling back to the global median where none was inferred. Unset leaves the prior
    # at the TALYS default, which is what every published result used.
    _psf = _psf_scale_arg()
    stage_b = C.PredictionSet.from_surrogate(surrogate_ckpt, grid=grid, e_min_ev=e_min_ev,
                                             e_max_ev=e_max_ev, device=device, nuclides=picked,
                                             channel=channel, gsf_norm=_psf)
    ids = sorted({nid for nid, _mt in stage_b.keys()})

    # Per-region Stage B. Surrogates trained on identical data with different seeds differ by
    # more than any recipe change measured on 2026-09-10 -- Fe-Sn input error ranges 0.181 to
    # 0.295 across four seeds -- and no single one wins everywhere. INCOGNITA_SURROGATE_MAP picks
    # the best per mass region. The choice is made on `input_pre`, the error against
    # measurements published BEFORE the cutoff, so it never sees the retrodiction test; and it
    # is three bits of freedom over 225 nuclides, not a per-nuclide fit, which is what failed
    # in the per-nuclide fine-tune and the parameter fit.
    region_sets: dict[str, object] = {}
    # `region:tag` picks one checkpoint for a region; `region:tagA|tagB|...` gives that region
    # its own ENSEMBLE, log-averaged like the global one. The distinction matters because a
    # single seed carries the seed noise the ensemble exists to cancel -- measured at 0.0032
    # on the gate cells -- so a per-region pick made from single checkpoints cannot be
    # compared against a five-seed global ensemble on equal terms.
    smap = _env("SURROGATE_MAP", "")
    region_ens: dict[str, list] = {}
    if smap:
        for item in smap.split(","):
            reg, tags = item.split(":")
            sets = []
            for tag in tags.split("|"):
                ck = _ckpt(f"models/surrogate/checkpoints/talys-surrogate-{tag.strip()}.pt")
                sets.append(C.PredictionSet.from_surrogate(
                    ck, grid=grid, e_min_ev=e_min_ev, e_max_ev=e_max_ev,
                    device=device, nuclides=picked, channel=channel))
            region_ens[reg.strip()] = sets
            region_sets[reg.strip()] = sets[0]
        print(f"[stage-c] per-region Stage B: {smap}", flush=True)

    # A pre-cutoff evaluated library as the prior, instead of (or blended with) the surrogate.
    # input-ceiling.json says Stage C is close to a pass-through of its input and that a
    # library-quality prior (error 0.090) yields 0.093 -- 1.16x the measurement noise floor,
    # against 1.86x from the TALYS-surrogate prior. That was dismissed as leakage because the
    # teacher was TENDL-2025, which has seen the post-2012 data the test holds out. ENDF/B-VII.1
    # was released in December 2011 and has not. Starting from the previous evaluation and
    # correcting it with newer measurements is what an evaluator does; the time-split stays
    # honest as long as the library predates the cutoff. INCOGNITA_PRIOR_LIB picks it and
    # INCOGNITA_PRIOR_W blends in log10 (1.0 = library only, 0.5 = geometric mean with Stage B).
    prior_libs: list = []
    prior_lib = None
    prior_w = float(_env("PRIOR_W", "1.0"))
    prior_regions = set(r.strip() for r in _env(
        "PRIOR_REGIONS", "Fe-Sn,Sn-Pb,actinide").split(",") if r.strip())
    if _env("PRIOR_LIB", ""):
        # Several pre-cutoff libraries average better than one. They are correlated -- all three
        # fit the same pre-2012 measurements -- but they differ by evaluator judgement, and that
        # is the component an average cancels. ENDF/B-VII.1 (2011), JENDL-4.0 (2010) and
        # ENDF/B-VII.0 (2006) all predate the 2012 cutoff, so none of them leaks.
        for _lib in _env("PRIOR_LIB").split(","):
            prior_libs.append(
                C.PredictionSet.from_library(_lib.strip(), mts=(mt,), nuclides=ids))
        prior_lib = prior_libs[0]
        print(f"[stage-c] Stage B prior blended with {len(prior_libs)} librar(ies) "
              f"{_env('PRIOR_LIB')} at w={prior_w}", flush=True)

    # Averaging beats choosing. The seed spread measured on 2026-09-10 (Fe-Sn input error 0.181
    # to 0.295 over four seeds trained on identical data) is variance, and the standard answer
    # to variance is the mean, not a pick: a per-region pick keeps one draw's noise, while the
    # ensemble mean cancels it. Averaged in log10, which is the space every score is computed in.
    ens_sets: list[object] = []
    ens = _env("SURROGATE_ENSEMBLE", "")
    if ens:
        for tag in ens.split(","):
            ck = _ckpt(f"models/surrogate/checkpoints/talys-surrogate-{tag.strip()}.pt")
            ens_sets.append(C.PredictionSet.from_surrogate(
                ck, grid=grid, e_min_ev=e_min_ev, e_max_ev=e_max_ev,
                device=device, nuclides=picked, channel=channel))
        print(f"[stage-c] Stage B is the log-mean of {len(ens_sets)} surrogates: {ens}", flush=True)

    # An optical-model correction derived from measured TOTAL cross sections. The fit sees no
    # capture data at all, so unlike every capture-fitted correction tried on 2026-09-10 there
    # is nothing in it to overfit: measured 12.7% better than TALYS-default on post-cutoff
    # capture bins while flat on pre-cutoff ones. Additive in log10, so it composes with the
    # surrogate ensemble and the library blend rather than replacing them.
    omp_delta: dict[str, np.ndarray] = {}
    _dpath = _env("OMP_DELTA", "")
    if _dpath:
        import polars as _pl
        _d = _pl.read_parquet(ROOT / _dpath if not os.path.isabs(_dpath) else _dpath)
        _scale = float(_env("OMP_DELTA_W", "1.0"))
        for _r in _d.iter_rows(named=True):
            omp_delta[_r["nuclide_id"]] = np.asarray(_r["delta_log10"], float) * _scale
        print(f"[stage-c] optical-model correction from total cross sections: "
              f"{len(omp_delta)} nuclides at weight {_scale}", flush=True)

    # The photon-strength anchor, applied through the same path. `gnorm` with a measured
    # Gamma_gamma is the only intervention that has ever moved this prior -- the PSF is the one
    # ingredient of the TALYS calculation anchored to no measurement, and (n,2n) rules out the
    # shared ingredients at r = -0.021. Deltas are summed where a nuclide carries both, because
    # the two corrections are to different ingredients of the same calculation.
    _ppath = _env("PSF_DELTA", "")
    if _ppath:
        import polars as _pl
        _pd_ = _pl.read_parquet(ROOT / _ppath if not os.path.isabs(_ppath) else _ppath)
        _pscale = float(_env("PSF_DELTA_W", "1.0"))
        _added = 0
        for _r in _pd_.iter_rows(named=True):
            _d = np.asarray(_r["delta_log10"], float) * _pscale
            _k = _r["nuclide_id"]
            omp_delta[_k] = omp_delta[_k] + _d if _k in omp_delta else _d
            _added += 1
        print(f"[stage-c] photon-strength correction from measured Gamma_gamma: "
              f"{_added} nuclides at weight {_pscale}", flush=True)

    def _region_of(nid: str) -> str:
        z = int(nid[1:4])
        return "Fe-Sn" if z <= 50 else ("Sn-Pb" if z <= 82 else "actinide")
    # RETRO: a retrodiction exam has to hand the bundle a teacher of the right vintage. The
    # teacher never enters the loss in the exam family (teacher_weight = 0) but it sets the
    # teacher RRR bound and the in-bundle comparison column, and TENDL-2025 has seen everything.
    teacher_key = _env("TEACHER_LIB", "") or teacher_key
    teacher = C.PredictionSet.from_library(teacher_key, mts=(mt,), nuclides=ids) if teacher_key else {}

    points = C.load_exfor_points(mode="datasets", year_cutoff=None, mts=(mt,),
                                 channel=channel)
    # RETRO sensitivity arm S6: `year_cutoff` keeps a measurement out of training by its
    # PUBLICATION year, but an evaluator of year Y worked from the EXFOR snapshot of year Y,
    # and 41 % of capture datasets are compiled into EXFOR more than two years after they are
    # published. Setting INCOGNITA_EXFOR_COMPILED_CUTOFF = Y also drops every dataset whose
    # entry was compiled after Y, so the model sees only what TENDL-Y's snapshot held.
    _cc = _env("EXFOR_COMPILED_CUTOFF", "")
    if _cc:
        import polars as _pl
        _dates = _pl.read_parquet(
            Path(os.environ.get("INCOGNITA_INPUTS", Path.home() / "incognita-inputs")) / "shared" / "retro_exfor_entry_dates.parquet"
        ).select("entry", "compiled_year")
        _ent = _pl.read_parquet(
            MAIN / "curated" / "exfor_capture_Z26-92_trust.parquet"
        ).select("dataset_key", "entry").unique(subset="dataset_key")
        _n0 = points.frame.height
        _keep = (points.frame.join(_ent, on="dataset_key", how="left")
                 .join(_dates, on="entry", how="left")
                 .filter(_pl.col("compiled_year").is_null()
                         | (_pl.col("compiled_year") <= int(_cc)))
                 .drop(["entry", "compiled_year"]))
        points.frame = _keep
        print(f"[stage-c] RETRO compiled-date cutoff {_cc}: {_n0} -> {_keep.height} dataset rows",
              flush=True)
    frame = points.frame.to_pandas() if hasattr(points.frame, "to_pandas") else points.frame

    # --- per-dataset normalisation, marginalised instead of fitted -------------------------
    # 38% of the disagreement between independent experiments is a whole-dataset normalisation
    # shift (sigma = 0.079 in log10), not point-to-point scatter -- docs/results/noise-floor.md.
    # Training on the raw values makes the model chase those offsets, which is why every attempt
    # to fit harder generalises worse in time: per-nuclide parameter fitting reaches TENDL-level
    # error on the bins it fits and transfers nothing, because the next decade's experiments do
    # not share this decade's normalisations.
    #
    # So estimate each dataset's shift against the consensus of the others and remove it, with a
    # Gaussian prior of that measured width so a dataset with little overlap is barely moved:
    #     delta_d = sum_i w_i (y_i - consensus_i) / (sum_i w_i + 1/sigma0^2)
    # Iterated a few times, this is the standard hierarchical normalisation an evaluator applies
    # by hand. Only rows at or before the cutoff are touched: the post-cutoff rows are the score
    # and must never be adjusted by anything the model can see.
    if _env("NORM_HARMONISE", "") not in ("", "0"):
        sigma0 = float(_env("NORM_SIGMA", "0.079"))
        n_it = int(_env("NORM_ITERS", "4"))
        import pandas as _pd
        fr = frame if isinstance(frame, _pd.DataFrame) else frame.to_pandas()
        fr = fr.copy()
        pre = (fr["year"].isna()) | (fr["year"] <= year_cutoff)
        val = np.log10(fr["meas_b"].to_numpy(float).clip(1e-30))
        # The weight has to be a precision, not a trust score: the prior contributes 1/sigma0^2
        # = 160 to the denominator, so weights of order 1 leave every shift shrunk to nothing
        # (measured: rms shift 0.0017 against a measured normalisation width of 0.079). Trust
        # divided by the point's own variance is the right scale -- a dataset quoting 0.1 in
        # log10 contributes 100 per point, and ten such points outweigh the prior as they should.
        w = fr["weight"].to_numpy(float) if "weight" in fr else np.ones(len(fr))
        sg = fr["sigma_log10"].to_numpy(float) if "sigma_log10" in fr else np.full(len(fr), 0.1)
        sg = np.where(np.isfinite(sg) & (sg > 1e-3), sg, 0.1)
        w = np.where(np.isfinite(w) & (w > 0), w, 0.0) / sg**2
        w = w * pre.to_numpy()
        cell = (fr["nuclide_id"].astype(str) + "|" + fr["bin"].astype(str)).to_numpy()
        ds = fr["dataset_key"].astype(str).to_numpy()
        cell_ix, cells = _pd.factorize(cell)
        ds_ix, dsk = _pd.factorize(ds)
        adj = val.copy()
        for _ in range(n_it):
            num = np.bincount(cell_ix, weights=w * adj, minlength=len(cells))
            den = np.bincount(cell_ix, weights=w, minlength=len(cells))
            cons = np.divide(num, den, out=np.zeros_like(num), where=den > 0)
            r = adj - cons[cell_ix]
            multi = den[cell_ix] > w            # only cells another dataset also measured
            wm = w * multi
            dn = np.bincount(ds_ix, weights=wm * r, minlength=len(dsk))
            dd = np.bincount(ds_ix, weights=wm, minlength=len(dsk)) + 1.0 / sigma0**2
            delta = dn / dd
            # A shift estimated from one or two overlapping cells is mostly noise, and applying
            # it to every point of that dataset injects the noise everywhere. Require the
            # dataset's overlapping evidence to outweigh the prior by `INCOGNITA_NORM_MINOVL`
            # before moving it at all; the rest keep their published normalisation.
            min_ovl = float(_env("NORM_MINOVL", "0")) / sigma0**2
            if min_ovl > 0:
                delta = np.where(dd - 1.0 / sigma0**2 >= min_ovl, delta, 0.0)
            adj = val - delta[ds_ix] * pre.to_numpy()
        moved = float(np.sqrt(np.mean(delta**2)))
        print(f"[stage-c] normalisation harmonised: {len(dsk)} datasets, rms shift "
              f"{moved:.4f} log10 (prior {sigma0}), {int(pre.sum())} pre-cutoff rows", flush=True)
        fr["meas_b"] = 10.0 ** adj
        frame = fr
    frame = frame[frame["nuclide"].isin(ids) if "nuclide" in frame else
                  frame["nuclide_id"].isin(ids)]
    col_id = "nuclide" if "nuclide" in frame else "nuclide_id"

    n = len(ids)
    stage_b_b = np.full((n, n_energy), np.nan)
    teacher_log = np.zeros((n, n_energy))
    teacher_ok = np.zeros(n, dtype=np.float32)
    target_log = np.zeros((n, n_energy))
    trust = np.zeros((n, n_energy))
    is_test = np.zeros((n, n_energy))
    ds_records: list[dict] = []

    # EXACTFIT: Stage B from the exact engine (scripts/exactfit_engine.py) instead of any
    # surrogate. A parquet of (nuclide_id, capture_b on this grid); a nuclide it does not carry
    # keeps the surrogate path below, and the count is printed so a partial table is visible.
    engine_b: dict[str, np.ndarray] = {}
    _epath = _env("STAGE_B_ENGINE", "")
    if _epath:
        import polars as _pl
        for _r in _pl.read_parquet(_epath).iter_rows(named=True):
            _c = np.asarray(_r["capture_b"], float)
            if _c.shape[0] == n_energy and np.isfinite(_c).all() and (_c > 0).all():
                engine_b[_r["nuclide_id"]] = _c
        print(f"[stage-c] Stage B from the exact engine ({_epath}): {len(engine_b)} of "
              f"{len(ids)} nuclides, the rest on the surrogate path", flush=True)
    # ACTINIDEFIT: nuclides whose engine-table row is already the final Stage B (a pre-cutoff
    # library taken at full weight), so the library blend below must not dilute it again.
    engine_final = set(n.strip() for n in _env("STAGE_B_FINAL", "").split(",") if n.strip())
    if engine_final:
        print(f"[stage-c] Stage B rows taken as final (no library blend): {sorted(engine_final)}",
              flush=True)

    for i, nid in enumerate(ids):
        _sets = region_ens.get(_region_of(nid)) or ens_sets
        if nid in engine_b:
            stage_b_b[i] = engine_b[nid]
        elif _sets:
            curves = []
            for st in _sets:
                q = st.get((nid, mt))
                if q is not None:
                    c, _ = q.on_grid(grid)
                    c = np.asarray(c, float)
                    if np.isfinite(c).any():
                        curves.append(np.log10(np.clip(c, 1e-30, None)))
            if curves:
                stage_b_b[i] = 10.0 ** np.mean(np.stack(curves), axis=0)
            p = _sets[0].get((nid, mt))
        else:
            src = region_sets.get(_region_of(nid), stage_b)
            p = src.get((nid, mt))
            if p is None:
                p = stage_b.get((nid, mt))
            if p is not None:
                s, _ = p.on_grid(grid)
                stage_b_b[i] = s
        # blend the pre-cutoff library in last, over whatever Stage B produced -- but only in
        # the regions where a library carries information rather than fitting. Measured
        # 2026-09-10: blending everywhere improves Fe-Sn at all three cutoffs (-0.010, -0.011,
        # -0.008) and destroys Sn-Pb (+0.019, +0.041, +0.055). docs/results/noise-floor.md said
        # why before the experiment ran: in Sn-Pb the libraries score two to three times BELOW
        # the scatter of the experiments they are scored against, which is what fitting those
        # datasets looks like, while in Fe-Sn and the actinides they sit 2.5x and 5x above the
        # floor with real headroom. Importing an overfitted prior imports the overfitting.
        if prior_lib is not None and _region_of(nid) in prior_regions and not (
                nid in engine_b and nid in engine_final):
            base_l = np.log10(np.clip(stage_b_b[i], 1e-30, None))
            got = []
            for st in prior_libs:
                q = st.get((nid, mt))
                if q is None:
                    continue
                lc = np.asarray(q.on_grid(grid)[0], float)
                ok_l = np.isfinite(lc) & (lc > 0)
                if ok_l.any():
                    got.append(np.where(ok_l, np.log10(np.clip(lc, 1e-30, None)), base_l))
            if got:
                lib_l = np.mean(np.stack(got), axis=0)
                stage_b_b[i] = 10.0 ** ((1.0 - prior_w) * base_l + prior_w * lib_l)
        if nid in omp_delta:
            d_ = omp_delta[nid]
            if d_.shape[0] == stage_b_b.shape[1] and np.isfinite(d_).all():
                stage_b_b[i] = 10.0 ** (np.log10(np.clip(stage_b_b[i], 1e-30, None)) + d_)
        t = teacher.get((nid, mt))
        if t is not None:
            rrr[nid] = float(getattr(t, "rrr_upper_ev", 0.0) or 0.0)
            ts, _ = t.on_grid(grid)
            teacher_log[i] = np.log10(np.where(np.isfinite(ts) & (ts > 0), ts, 1e-12))
            teacher_ok[i] = 1.0
        rows = frame[frame[col_id] == nid]
        if len(rows) == 0:
            continue
        e = rows["e_mid_ev"].to_numpy(float)
        keep = np.isfinite(e) & (e >= e_min_ev) & (e <= e_max_ev)
        idx = _bin_index(e[keep], grid)
        meas = rows["meas_b"].to_numpy(float)[keep] if "meas_b" in rows else \
            10.0 ** rows["consensus_log"].to_numpy(float)[keep]
        w = rows["weight"].to_numpy(float)[keep] if "weight" in rows else np.ones(keep.sum())
        year = rows["year"].to_numpy(float)[keep] if "year" in rows else np.full(keep.sum(), np.nan)
        # C6 (models/norm_latent.py) needs the rows this mean is about to collapse: a
        # normalisation error applies to a whole EXFOR dataset, and once the datasets are
        # averaged into one number per bin there is nothing left to attach the latent to.
        dsk = (rows["dataset_key"].astype(str).to_numpy()[keep] if "dataset_key" in rows
               else np.array([f"{nid}|cell"] * int(keep.sum())))
        sgl = (rows["sigma_log10"].to_numpy(float)[keep] if "sigma_log10" in rows
               else np.full(int(keep.sum()), np.nan))
        for j, m, wt, yr, dk, sg in zip(idx, meas, w, year, dsk, sgl, strict=True):
            if not np.isfinite(m) or m <= 0:
                continue
            ds_records.append({"nuc_ix": i, "bin": int(j), "log10": float(np.log10(m)),
                               "sigma_log10": float(sg), "weight": float(wt),
                               "dataset_key": str(dk),
                               "is_test": float(np.isfinite(yr) and yr > year_cutoff)})
            # trust-weighted running mean in log space, so repeated bins combine
            prev = trust[i, j]
            target_log[i, j] = (target_log[i, j] * prev + np.log10(m) * wt) / max(prev + wt, 1e-9)
            trust[i, j] = prev + wt
            if np.isfinite(yr) and yr > year_cutoff:
                is_test[i, j] = 1.0

    # the surrogate leaves the odd grid edge undefined; carry the nearest finite value across
    # rather than dropping the whole nuclide for one point.
    for i in range(n):
        row = stage_b_b[i]
        good = np.isfinite(row) & (row > 0)
        if good.sum() >= 2:
            stage_b_b[i] = np.interp(np.log10(grid), np.log10(grid[good]), row[good])
    ok = np.isfinite(stage_b_b).all(axis=1) & (stage_b_b > 0).all(axis=1)
    if require_measurements == "or_macs":
        # A nuclide with no differential bin but a KADoNiS MACS is not a nuclide with no data.
        # The cross-validation measures what that one number is worth: held out with its MACS
        # the model reaches 0.1510 log10, held out without it 0.2035, and the difference is
        # almost entirely per-nuclide bias -- 57% of its variance. 98 chart nuclides are in
        # exactly that position and `require_measurements=True` excludes every one of them,
        # so they are predicted by a model that never saw the measurement that pins them.
        ok &= (trust.sum(axis=1) > 0) | macs_covered(ids)
    elif require_measurements:
        ok &= trust.sum(axis=1) > 0
    ids = [nid for nid, k in zip(ids, ok, strict=True) if k]
    sel = np.where(ok)[0]
    if _epath:
        check_engine_coverage(ids, engine_b, _epath)
    if embeddings == "encoder":
        try:
            emb = encoder_embeddings(ids, embed_dim, basis_ids=embedding_basis)
        except Exception as exc:                       # no cached field: fall back, but say so
            print(f"[stage-c] encoder embeddings unavailable ({exc}); using (Z, N)")
            embeddings = "zn"
    if embeddings != "encoder":
        rng = np.random.default_rng(0)
        zn = np.array([[int(nid[1:4]), int(nid[5:8])] for nid in ids], float)
        emb = np.concatenate([zn / 100.0,
                              rng.standard_normal((len(ids), embed_dim - 2)) * 0.01], axis=1)

    emb = assemble_embedding(ids, emb, resonance=resonance, urr_norm=urr_norm,
                             structure=structure, pairing=pairing, shells=shells, hfb=hfb,
                             fission=fission, qrpa=qrpa, thermal=thermal, n2n=n2n,
                             inelastic_threshold=inelastic_threshold,
                             target_spin=target_spin, m1_strength=m1_strength,
                             noise_control=noise_control, noise_control4=noise_control4)
    tt = lambda a: torch.tensor(a[sel], dtype=torch.float32)  # noqa: E731
    # Which resolved-resonance boundary bounds the region Stage C is allowed to speak in.
    #
    # "teacher" is the historical behaviour: the bound the teacher library itself declares.
    # That is one evaluator's choice and usually the lowest of the six -- 559 eV for Hf-176
    # where the maximum over the libraries is 3,000 eV, and 82 of 225 nuclides differ by more
    # than 1.5x. Between the two bounds the measurements are resolved resonances sampled at 64
    # log-spaced points across four decades, which is aliasing, not a cross section. Stage C
    # both TRAINS and is SCORED there, so it is being asked to fit noise and then graded on how
    # well it did. `scripts/residual_structure.py` measured the scoring half: it read Hf-176 at
    # 0.514 log10 instead of 0.119 and made it the worst nuclide on the chart.
    #
    # "canonical" takes the maximum over the evaluated libraries, which is the bound
    # `validation.differential.rrr_bounds` uses and every comparison script in the repository
    # already scores against.
    # "indep" (default since v0.1): the library-free bound of INDEP_FIX2 (RIPL D0 x resonance count with fallbacks,
    # docs/release/indep_fix2/bounds2.py); INCOGNITA_RRR_BOUNDS points at another table with columns nuclide_id, e_rrr_ev.
    # "teacher" and "canonical" read evaluated libraries and are opt-in.
    rrr_policy = rrr_policy or _env("RRR_POLICY", "indep")
    if rrr_policy == "indep":
        import pandas as _pd
        _bp = _env("RRR_BOUNDS", "") or str(Path(__file__).resolve().parents[1] / "docs" / "release" / "indep_fix2" / "indep_bounds2.parquet")
        _b = _pd.read_parquet(_bp).set_index("nuclide_id").e_rrr_ev
        rrr = {nid: (float(_b[nid]) if nid in _b.index and np.isfinite(_b[nid]) else 0.0) for nid in ids}
        print(f"[stage-c] resonance bound: indep ({_bp}); {sum(v > 0 for v in rrr.values())} of {len(ids)} nuclides bounded", flush=True)
    elif rrr_policy == "canonical":
        canon = C.rrr_bounds(mt=mt)
        raised = sum(1 for nid in ids if canon.get(nid, 0.0) > rrr.get(nid, 0.0) * 1.5)
        rrr = {nid: max(rrr.get(nid, 0.0), float(canon.get(nid, 0.0) or 0.0)) for nid in ids}
        print(f"[stage-c] resonance bound: canonical (max over libraries); raised by more than "
              f"1.5x on {raised} of {len(ids)} nuclides", flush=True)
    elif rrr_policy != "teacher":
        raise ValueError(f"rrr_policy must be 'indep', 'teacher' or 'canonical', got {rrr_policy!r}")
    bounds = torch.tensor([rrr.get(nid, 0.0) for nid in ids], dtype=torch.float32)
    # the (n,2n) channel opens near the compound's neutron separation energy, which we already
    # have: it is what the surrogate is conditioned on
    # `threshold_ev` is the energy where (n,2n) opens -- the kink the residual is lifted with
    # (models/residual/fno.py). It was S_n of the *compound*, which is not that energy.
    #
    # n + (Z,A) -> (Z,A+1)*: emitting the first neutron costs S_n(Z,A+1) and returns the
    # compound to (Z,A); emitting the second costs S_n(Z,A). The compound's excitation is
    # E_cm + S_n(Z,A+1), so the channel opens at E_cm = S_n(Z,A) -- the separation energy of
    # the TARGET, times (A+1)/A for the lab frame. S_n(compound) sits 1.4-3.8 MeV below that
    # (Au-197 6.51 against 8.11, Fe-56 7.65 against 11.40), so the model was being shown the
    # kink in the wrong place for every nuclide.
    #
    # Correcting it changes nothing measurable. Five paired ensembles, capture, mean effect on
    # the nine gate cells +0.0009 +- 0.0009 (0.95 se) -- not significant, and the sign is
    # marginally *worse*. So the default stays `compound`: that is what capture-v19 was fitted
    # with, and there is no evidence to justify moving the shipped model. `target` is the
    # physically correct value and is kept switchable, because the null result is about this
    # model's sensitivity, not about which number is right.
    _thr_mode = _env("THRESHOLD", "compound")
    if _thr_mode == "off":
        # The ablation: no threshold information at all. It has to be None, not zeros --
        # StageCBundle turns threshold_ev into log10(E / threshold_ev.clamp_min(1 eV)) clipped
        # to [-2, 1], so a zero threshold becomes +1.0 at every energy, which says "far above
        # the threshold everywhere" rather than "unknown". The same trap catches any nuclide
        # missing from the lookup, which `.get(nid, 0.0)` fills with exactly that zero.
        thresh = None
    elif _thr_mode == "compound":
        sn_lookup = {f"Z{z:03d}N{n:03d}M0": s_ * 1e3 for z, n, s_ in curated_nuclides(1, 120)}
        # a missing nuclide gets a large threshold, i.e. "below it everywhere", rather than 0,
        # which the clamp would turn into "far above it everywhere" -- the opposite claim
        miss = float(grid[-1]) * 10.0
        thresh = torch.tensor([sn_lookup.get(nid) or miss for nid in ids], dtype=torch.float32)
    else:
        tf = n2n_features(ids)                    # column 0 is (e_thr - 9)/3 in MeV
        miss = float(grid[-1]) * 10.0
        thresh = torch.tensor([(float(v) * 3.0 + 9.0) * 1e6 if v != 0.0 else miss
                               for v in tf[:, 0]], dtype=torch.float32)
    # Remap the per-dataset rows onto the surviving nuclides. `sel` is the selection that
    # produced `ids`, so a row whose nuclide was dropped has no home and is dropped with it.
    from models.norm_latent import build_rows
    remap = {int(o): k for k, o in enumerate(sel)}
    ds_rows = build_rows([{**r, "nuc_ix": remap[r["nuc_ix"]]} for r in ds_records
                          if r["nuc_ix"] in remap], ids, int(len(grid)))
    # The (n,n') threshold, as a channel rather than as an embedding column. `lift_embed` is a
    # per-nuclide constant broadcast over the whole grid, so `inelastic_threshold` (the scalar
    # block, null at +0.55%) could only tell the residual *which nuclide* has a low first level,
    # never *where on the grid* the channel opens. Routed here it reaches `lift_sigma` and can
    # put a kink at the threshold, which is what the already-successful (n,2n) channel does.
    inel = None
    if inelastic_channel:
        ev = first_level_ev(ids)
        inel = torch.tensor(ev, dtype=torch.float32)
        print(f"[stage-c] inelastic channel: first level counted for "
              f"{int((ev > 0).sum())}/{len(ids)} targets, median "
              f"{np.median(ev[ev > 0]) / 1e3:.0f} keV", flush=True)
    return StageCBundle(year_cutoff=year_cutoff,
                        nuclides=ids, grid_ev=grid, stage_b_b=tt(stage_b_b),
                        target_log=tt(target_log), trust=tt(trust), teacher_log=tt(teacher_log),
                        teacher_ok=tt(teacher_ok),
                        embeddings=torch.tensor(emb, dtype=torch.float32), is_test=tt(is_test),
                        rrr_upper_ev=bounds, threshold_ev=thresh, inelastic_ev=inel,
                        aux_urr=urr_channel, ds=ds_rows)


def build_library_bundle(
    *,
    library: str = "endfb71",
    year_cutoff: int = 2012,
    e_min_ev: float = 1e3,
    e_max_ev: float = 2e7,
    n_energy: int = 64,
    embed_dim: int = 16,
    max_nuclides: int | None = None,
    # must match the measurement bundle, or the pre-trained state dict will not load onto it
    mt: int = 102,
    channel: str = "capture",
    resonance: bool = True,
    urr_norm: bool = False,
    structure: bool = False,
    pairing: bool = True,
    shells: bool = True,
    hfb: bool = True,
    fission: bool = True,
    qrpa: bool = True,
    inelastic_threshold: bool | None = None,  # see build_bundle
    target_spin: bool = False,
    m1_strength: bool = False,
    noise_control: bool = False,
    noise_control4: bool = False,
    thermal: bool = False,
    device: str = "cpu",
) -> StageCBundle:
    """A pre-training bundle whose targets are an evaluated library, not measurements.

    The gold set is 17,062 curated capture measurements on a few hundred nuclides. An
    evaluated library covers the whole chart, is not ground truth, and encodes decades of
    expert fitting — the same trade an MSA makes for protein structure. Default is
    ENDF/B-VII.1, released December 2011: pre-training on a library that has already seen
    the post-cutoff measurements would leak the test set straight into the prior.
    """
    if inelastic_threshold is None:
        inelastic_threshold = inelastic_threshold_default()
    surrogate_ckpt = _ckpt(f"models/surrogate/checkpoints/talys-surrogate-{SURROGATE_TAG}.pt")
    grid = _grid(e_min_ev, e_max_ev, n_energy)
    lib = C.PredictionSet.from_library(library, mts=(mt,))
    ids = sorted({nid for nid, _mt in lib.keys() if _mt == mt})
    zn_all = {}
    for nid in ids:
        try:
            zn_all[nid] = (int(nid[1:4]), int(nid[5:8]))
        except ValueError:
            continue
    sn = {(z, n): s for z, n, s in curated_nuclides(1, 120)}
    picked = [(zn_all[n][0], zn_all[n][1], sn[zn_all[n]]) for n in ids
              if n in zn_all and zn_all[n] in sn]
    if max_nuclides:
        picked = picked[:max_nuclides]
    if not picked:
        raise RuntimeError(f"no {library} nuclides with a separation energy")

    stage_b = C.PredictionSet.from_surrogate(surrogate_ckpt, grid=grid, e_min_ev=e_min_ev,
                                             e_max_ev=e_max_ev, device=device, nuclides=picked,
                                             channel=channel)
    keep = sorted({nid for nid, _mt in stage_b.keys()})
    n = len(keep)
    stage_b_b = np.full((n, n_energy), np.nan)
    target_log = np.zeros((n, n_energy))
    trust = np.zeros((n, n_energy))
    rrr = np.zeros(n)
    # NOTE: a library-prior blend and a per-region Stage B source were pasted in here by
    # e43b1d0 (2026-09-10) from build_bundle, which defines prior_lib, prior_libs, prior_w,
    # region_sets and _region_of. This function defines none of them, so the loop raised
    # NameError on its first iteration and build_library_bundle could not run at all. Removed
    # rather than wired up, on two grounds: the blend reads stage_b_b[i] as `base_l` twenty
    # lines before that row is assigned, so it would have averaged against NaN; and blending a
    # library prior into a bundle whose TARGET is that same library is circular.
    # docs/results/pretrain-experiment.json predates the breakage (2026-09-10 20:13 against
    # 22:41), so the G4 null result stands -- but it was not re-runnable until now.
    for i, nid in enumerate(keep):
        p = stage_b.get((nid, mt))
        if p is not None:
            s_, _ = p.on_grid(grid)
            good = np.isfinite(s_) & (s_ > 0)
            if good.sum() >= 2:
                stage_b_b[i] = np.interp(np.log10(grid), np.log10(grid[good]), s_[good])
        t = lib.get((nid, mt))
        if t is None:
            continue
        ts, _ = t.on_grid(grid)
        ok = np.isfinite(ts) & (ts > 0)
        target_log[i, ok] = np.log10(ts[ok])
        trust[i, ok] = 1.0                       # a library curve is a weak label, weight 1
        rrr[i] = float(getattr(t, "rrr_upper_ev", 0.0) or 0.0)

    ok = np.isfinite(stage_b_b).all(axis=1) & (stage_b_b > 0).all(axis=1)
    # unconditional here: `require_measurements` is build_bundle's parameter and a nuclide with
    # no library target carries no pre-training signal at all.
    ok &= trust.sum(axis=1) > 0
    keep = [nid for nid, k in zip(keep, ok, strict=True) if k]
    sel = np.where(ok)[0]
    emb = assemble_embedding(keep, encoder_embeddings(keep, embed_dim),
                             resonance=resonance, urr_norm=urr_norm, structure=structure,
                             pairing=pairing, shells=shells, hfb=hfb, fission=fission,
                             qrpa=qrpa, thermal=thermal, inelastic_threshold=inelastic_threshold,
                             target_spin=target_spin, m1_strength=m1_strength,
                             noise_control=noise_control, noise_control4=noise_control4,
                             n2n=(channel == "n2n"))
    tt = lambda a: torch.tensor(a[sel], dtype=torch.float32)  # noqa: E731
    return StageCBundle(nuclides=keep, grid_ev=grid, stage_b_b=tt(stage_b_b),
                        target_log=tt(target_log), trust=tt(trust), teacher_log=tt(target_log),
                        embeddings=torch.tensor(emb, dtype=torch.float32),
                        is_test=torch.zeros_like(tt(trust)),
                        rrr_upper_ev=torch.tensor(rrr[sel], dtype=torch.float32))


if __name__ == "__main__":
    b = build_bundle()
    print(f"[stage-c] {len(b.nuclides)} nuclides, grid {b.n_energy}, "
          f"measured bins {int((b.trust > 0).sum())}, test bins {int(b.is_test.sum())}")
