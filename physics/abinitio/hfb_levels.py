"""Microscopic level densities from the BSkG3 + combinatorial model (WP-28 step 1).

RIPL-4 ships 448 MB of level densities computed from a Skyrme Hartree-Fock-Bogoliubov
single-particle scheme by explicitly counting states, for 7,677 nuclei with 8 <= Z <= 110.
They are not fitted to cross sections, which makes them independent of TALYS in exactly the
way the evaluated libraries are not — and independence, not volume, is what separated this
project's one useful prior (measured D0/Gg, +2.2%) from its three null ones (library
pre-training +0.4%, systematics giant-dipole parameters, measured level counts +0.1%).

The quantity that matters is the total level density at the neutron separation energy: the
compound nucleus lands there, and how many states it finds decides how readily it captures.
Our error correlates with the measured level spacing D0 at rho = +0.26 (p = 9e-38), so this is
the same physics from a Hamiltonian rather than from an experiment.

    from physics.abinitio.hfb_levels import level_density_at
    level_density_at([("Z050N078M0", 6.9)])     # nuclide id, Sn in MeV
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
TABLES = REPO / "raw" / "ripl4" / "RIPL-4" / "densities" / "total" / "bskg3-comb"
HEADER = re.compile(r"Z=\s*(\d+)\s+A=\s*(\d+):\s*(Positive|Negative)-Parity.*?b20=\s*(-?[\d.]+)")


def _parse_chain(path: Path) -> dict[tuple[int, int], dict]:
    """Parse one zXXX.tab file into {(Z, A): {u, rho_pos, rho_neg, beta2}}."""
    out: dict[tuple[int, int], dict] = {}
    key: tuple[int, int] | None = None
    parity = ""
    rows: list[tuple[float, float]] = []

    def flush() -> None:
        if key is None or not rows:
            return
        rec = out.setdefault(key, {})
        arr = np.asarray(rows, float)
        rec[f"u_{parity}"] = arr[:, 0]
        rec[f"rho_{parity}"] = arr[:, 1]

    with path.open() as fh:
        for line in fh:
            m = HEADER.search(line)
            if m:
                flush()
                rows = []
                key = (int(m.group(1)), int(m.group(2)))
                parity = "pos" if m.group(3) == "Positive" else "neg"
                out.setdefault(key, {})["beta2"] = float(m.group(4))
                continue
            parts = line.split()
            if len(parts) >= 5 and parts[0][0].isdigit():
                try:
                    rows.append((float(parts[0]), float(parts[4])))    # U[MeV], RHOTOT
                except ValueError:
                    continue
    flush()
    return out


def level_density_at(requests: list[tuple[str, float]]) -> dict[str, dict]:
    """Total (both parities) HFB level density at each nuclide's separation energy.

    ``requests`` are (nuclide_id of the *target*, Sn of the compound in MeV). The compound is
    (Z, A+1), which is the nucleus the table must be read for.
    """
    want: dict[int, list[tuple[str, int, float]]] = {}
    for nid, sn in requests:
        try:
            z, n = int(nid[1:4]), int(nid[5:8])
        except ValueError:
            continue
        want.setdefault(z, []).append((nid, z + n + 1, float(sn)))    # compound mass number

    out: dict[str, dict] = {}
    for z, items in want.items():
        path = TABLES / f"z{z:03d}.tab"
        if not path.exists():
            continue
        chain = _parse_chain(path)
        for nid, a_cn, sn in items:
            rec = chain.get((z, a_cn))
            if not rec or "u_pos" not in rec:
                continue
            u = rec["u_pos"]
            rho = rec["rho_pos"] + rec.get("rho_neg", rec["rho_pos"] * 0)
            if not np.isfinite(sn) or sn <= 0 or len(u) < 2:
                continue
            val = float(np.interp(sn, u, np.log10(np.clip(rho, 1e-30, None))))
            out[nid] = {"log10_rho_sn": val, "beta2": rec.get("beta2", 0.0),
                        "compound_A": a_cn}
    return out


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(REPO))
    from models.stage_c_data import curated_nuclides

    req = [(f"Z{z:03d}N{n:03d}M0", s * 1e-3) for z, n, s in curated_nuclides(26, 92)][:400]
    got = level_density_at(req)
    print(f"HFB level densities recovered for {len(got)} of {len(req)} nuclides")
    for nid in list(got)[:5]:
        r = got[nid]
        print(f"  {nid}  log10 rho(Sn) = {r['log10_rho_sn']:6.2f}  beta2 = {r['beta2']:+.3f}")
