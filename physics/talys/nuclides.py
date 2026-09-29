"""Target nuclide sets for the TALYS sweep, plus Sn of the compound nucleus.

The source of truth is ``staging/nuclides.parquet`` (WP-04: AME2020 +
NUBASE2020 joined; one row per (Z, N, iso)).  When it is missing we fall back
to parsing NUBASE2020 directly through ``data.ingest.nubase`` and finally to a
small hard-coded stable-isotope table so the module always imports.

Selection modes (``mode`` argument of :func:`select_nuclides`)
------------------------------------------------------------
``stratified``  one "reference" isotope per Z in ``[z_min, z_max]`` with step
                ``z_step`` (the stable isotope nearest the mean stable mass,
                even A preferred; the longest-lived one for Tc, Pm, Po-Ac, Pa),
                plus ``n_rich`` extra neutron-rich isotopes (A_ref + ``rich_offset``) spread evenly
                over the Z range.  This is the local ~10^3-run design.
``all_ground``  every ground-state nuclide in the Z range with a half-life
                above ``min_half_life_s`` (or stable) — the cloud 10^5+ design.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
STAGING_NUCLIDES = REPO / "staging" / "nuclides.parquet"

# Fallback table: (Z, A) of a stable isotope near the middle of the stable
# band for Z = 26..92, used only when neither staging nor NUBASE is readable.
_FALLBACK_STABLE: tuple[tuple[int, int], ...] = (
    (26, 56),
    (27, 59),
    (28, 58),
    (29, 63),
    (30, 66),
    (31, 69),
    (32, 74),
    (33, 75),
    (34, 80),
    (35, 79),
    (36, 84),
    (37, 85),
    (38, 88),
    (39, 89),
    (40, 90),
    (41, 93),
    (42, 96),
    (43, 99),
    (44, 102),
    (45, 103),
    (46, 106),
    (47, 107),
    (48, 114),
    (49, 115),
    (50, 120),
    (51, 121),
    (52, 130),
    (53, 127),
    (54, 132),
    (55, 133),
    (56, 138),
    (57, 139),
    (58, 140),
    (59, 141),
    (60, 142),
    (61, 145),
    (62, 152),
    (63, 153),
    (64, 158),
    (65, 159),
    (66, 164),
    (67, 165),
    (68, 166),
    (69, 169),
    (70, 174),
    (71, 175),
    (72, 178),
    (73, 181),
    (74, 184),
    (75, 187),
    (76, 192),
    (77, 193),
    (78, 195),
    (79, 197),
    (80, 202),
    (81, 205),
    (82, 208),
    (83, 209),
    (84, 209),
    (85, 210),
    (86, 222),
    (87, 223),
    (88, 226),
    (89, 227),
    (90, 232),
    (91, 231),
    (92, 238),
)


@dataclass(frozen=True)
class Nuclide:
    Z: int
    A: int
    sn_cn_kev: float  # neutron separation energy of the compound nucleus (Z, A+1); NaN if unknown
    is_stable: bool
    log10_half_life_s: float  # NaN for stable / unknown

    @property
    def N(self) -> int:
        return self.A - self.Z

    @property
    def key(self) -> str:
        return f"Z{self.Z:03d}A{self.A:03d}"


def _load_ground_states():
    """Return a polars DataFrame of ground states with columns Z, A, sn_kev, is_stable, log10_t."""
    import polars as pl

    if STAGING_NUCLIDES.is_file():
        df = pl.read_parquet(STAGING_NUCLIDES)
        df = df.filter(pl.col("iso") == 0).select(
            pl.col("Z").cast(pl.Int64),
            pl.col("A").cast(pl.Int64),
            pl.col("sn_kev").struct.field("value").alias("sn_kev"),
            pl.col("is_stable").fill_null(False),
            pl.col("log10_half_life_s").struct.field("value").alias("log10_t"),
        )
        return df
    try:  # pragma: no cover - exercised only when staging is absent
        from data.ingest.nubase import load_nubase

        nb = load_nubase()
        nb = nb[nb["iso"] == 0]
        return pl.DataFrame(
            {
                "Z": nb["Z"].astype(int).to_numpy(),
                "A": nb["A"].astype(int).to_numpy(),
                "sn_kev": np.full(len(nb), np.nan),
                "is_stable": nb["is_stable"].fillna(False).astype(bool).to_numpy(),
                "log10_t": nb["log10_half_life_s"].astype(float).to_numpy(),
            }
        )
    except Exception:  # pragma: no cover
        Z = np.array([z for z, _ in _FALLBACK_STABLE])
        A = np.array([a for _, a in _FALLBACK_STABLE])
        return pl.DataFrame(
            {
                "Z": Z,
                "A": A,
                "sn_kev": np.full(len(Z), np.nan),
                "is_stable": np.ones(len(Z), bool),
                "log10_t": np.full(len(Z), np.nan),
            }
        )


def _sn_lookup(df) -> dict[tuple[int, int], float]:
    out: dict[tuple[int, int], float] = {}
    for z, a, sn in zip(df["Z"].to_list(), df["A"].to_list(), df["sn_kev"].to_list(), strict=True):
        out[(int(z), int(a))] = float("nan") if sn is None else float(sn)
    return out


def _make(df, Z: int, A: int, sn: dict[tuple[int, int], float]) -> Nuclide:
    row = df.filter((df["Z"] == Z) & (df["A"] == A))
    stable = bool(row["is_stable"][0]) if row.height else False
    lt = row["log10_t"][0] if row.height else None
    return Nuclide(
        Z=int(Z),
        A=int(A),
        sn_cn_kev=sn.get((Z, A + 1), float("nan")),
        is_stable=stable,
        log10_half_life_s=float("nan") if lt is None else float(lt),
    )


def select_nuclides(
    mode: str = "stratified",
    z_min: int = 26,
    z_max: int = 92,
    z_step: int = 1,
    n_rich: int = 0,
    rich_offset: int = 4,
    min_half_life_s: float = 3.15e7,
    extra: list[tuple[int, int]] | None = None,
) -> list[Nuclide]:
    """Build the target list (see module docstring for the modes)."""
    df = _load_ground_states()
    sn = _sn_lookup(df)
    zs = list(range(z_min, z_max + 1, z_step))
    if zs[-1] != z_max:
        zs.append(z_max)
    out: list[Nuclide] = []
    seen: set[tuple[int, int]] = set()

    def add(Z: int, A: int) -> None:
        if (Z, A) in seen:
            return
        seen.add((Z, A))
        out.append(_make(df, Z, A, sn))

    if mode == "stratified":
        refs: list[tuple[int, int]] = []
        for Z in zs:
            sub = df.filter(df["Z"] == Z)
            stable = sub.filter(sub["is_stable"])
            if stable.height:
                As = np.array(sorted(stable["A"].to_list()), dtype=float)
                # nearest to the mean stable mass, preferring even A (the
                # abundant even-even workhorses: 56Fe, 90Zr, 208Pb, ...)
                score = np.abs(As - As.mean()) + 1.1 * (As % 2)
                A = int(As[int(np.argmin(score))])
            elif sub.height:
                A = int(sub.sort("log10_t", descending=True, nulls_last=True)["A"][0])
            else:
                A = dict(_FALLBACK_STABLE).get(Z, 2 * Z + Z // 4)
            refs.append((Z, A))
            add(Z, A)
        if n_rich > 0:
            picks = np.linspace(0, len(refs) - 1, n_rich).round().astype(int)
            for i in picks:
                Z, A = refs[int(i)]
                cand = A + rich_offset
                if df.filter((df["Z"] == Z) & (df["A"] == cand)).height:
                    add(Z, cand)
    elif mode == "all_ground":
        sub = df.filter((df["Z"] >= z_min) & (df["Z"] <= z_max))
        sub = sub.filter(sub["is_stable"] | (sub["log10_t"] >= np.log10(min_half_life_s)))
        for Z, A in sorted(zip(sub["Z"].to_list(), sub["A"].to_list(), strict=True)):
            add(int(Z), int(A))
    else:
        raise ValueError(f"unknown nuclide selection mode {mode!r}")

    for Z, A in extra or []:
        add(int(Z), int(A))
    return out
