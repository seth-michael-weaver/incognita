"""Microscopic photon strength functions from D1M+QRPA (WP-28, the gamma-strength half).

Capture has two ingredients. The level density decides how many states the compound can decay
through — that came from BSkG3+combinatorial and was worth +5.6%. The photon strength function
decides how readily it emits the gamma, and RIPL ships it computed from the D1M Gogny
interaction with QRPA for the whole chart, in `gamma/d1m.zip`. Like the level densities it is
calculated from a nuclear interaction and never fitted to a cross section, which is the
property that has separated this project's useful priors from its useless ones.

The scalar that matters is the radiative width itself. To leading order

    Gamma_gamma  ~  integral over E of  f_E1(E) * E^3

taken from zero to the separation energy, since the primary gamma carries away up to Sn. The
table is a grid over gamma energy and excitation, so the column nearest U = Sn is used.

    from physics.abinitio.qrpa_strength import gamma_strength_at
    gamma_strength_at([("Z050N078M0", 6.9)])
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "raw" / "ripl4" / "RIPL-4" / "gamma" / "d1m.zip"
HEADER = re.compile(r"Z=\s*(\d+)\s+A=\s*(\d+)")


def _parse_chain(zf: zipfile.ZipFile, name: str) -> dict[tuple[int, int], dict]:
    """One zXXX_e1 member -> {(Z, A): {e, cols, u_grid}}."""
    out: dict[tuple[int, int], dict] = {}
    key: tuple[int, int] | None = None
    u_grid: np.ndarray | None = None
    rows: list[list[float]] = []

    def flush() -> None:
        if key is not None and rows and u_grid is not None:
            arr = np.asarray(rows, float)
            out[key] = {"e": arr[:, 0], "f": arr[:, 1:], "u": u_grid}

    with zf.open(name) as fh:
        for raw in fh:
            line = raw.decode(errors="replace").rstrip()
            m = HEADER.search(line)
            if m and "PSF" in line:
                flush()
                rows = []
                key = (int(m.group(1)), int(m.group(2)))
                continue
            if "U=" in line and "E[MeV]" in line:
                u_grid = np.array([float(x) for x in re.findall(r"U=(\d+)MeV", line)], float)
                continue
            # The M1 tables are laid out by temperature ("T=0", "T>0"), not by excitation
            # energy, so without this they never set u_grid, flush() drops every chain, and the
            # member parses to an empty dict with no error. Mark the two columns so the caller
            # can pick one; gamma_strength_at takes the finite-temperature column for M1.
            if "T=" in line and "E[MeV]" in line:
                u_grid = np.array([0.0, 1.0], float)
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0][0].isdigit():
                try:
                    rows.append([float(x) for x in parts])
                except ValueError:
                    continue
    flush()
    return out


def gamma_strength_at(requests: list[tuple[str, float]],
                      multipole: str = "e1") -> dict[str, dict]:
    """log10 of the radiative-width integral, per target nuclide, at its separation energy.

    `multipole` selects the D1M+QRPA table: "e1" is the giant dipole, "m1" the magnetic
    strength (scissors mode plus spin-flip), which the same archive carries for the same 103
    proton chains. The transmission coefficient goes as f_XL * E^(2L+1), and 2L+1 = 3 for both
    E1 and M1, so the integrand is unchanged.
    """
    if not ARCHIVE.exists():
        return {}
    want: dict[int, list[tuple[str, int, float]]] = {}
    for nid, sn in requests:
        try:
            z, n = int(nid[1:4]), int(nid[5:8])
        except ValueError:
            continue
        want.setdefault(z, []).append((nid, z + n + 1, float(sn)))

    out: dict[str, dict] = {}
    with zipfile.ZipFile(ARCHIVE) as zf:
        names = set(zf.namelist())
        for z, items in want.items():
            member = f"d1m/z{z:03d}_{multipole}"
            if member not in names:
                continue
            chain = _parse_chain(zf, member)
            for nid, a_cn, sn in items:
                rec = chain.get((z, a_cn))
                if not rec or not np.isfinite(sn) or sn <= 0:
                    continue
                e, f, u = rec["e"], rec["f"], rec["u"]
                if f.shape[1] == 0:
                    continue
                if multipole == "m1":
                    # last column is T>0, the finite-temperature strength: it carries the
                    # low-energy upbend, which is the part that matters for keV capture
                    col = f.shape[1] - 1
                else:
                    col = int(np.argmin(np.abs(u[: f.shape[1]] - sn))) if len(u) else 0
                m = e <= sn
                if m.sum() < 3:
                    continue
                integral = float(np.trapezoid(f[m, col] * e[m] ** 3, e[m]))
                if integral <= 0:
                    continue
                peak = float(e[m][np.argmax(f[m, col] * e[m] ** 3)])
                out[nid] = {"log10_gamma_integral": float(np.log10(integral)),
                            "peak_energy_mev": peak}
    return out


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(REPO))
    from physics.talys.nuclides import select_nuclides

    ns = select_nuclides(mode="all_ground", z_min=26, z_max=60, min_half_life_s=3.15e7)[:60]
    req = [(f"Z{n.Z:03d}N{n.A - n.Z:03d}M0", n.sn_cn_kev * 1e-3) for n in ns
           if getattr(n, "sn_cn_kev", None)]
    got = gamma_strength_at(req)
    print(f"D1M+QRPA strength recovered for {len(got)} of {len(req)} nuclides")
    for nid in list(got)[:5]:
        r = got[nid]
        print(f"  {nid}  log10 integral {r['log10_gamma_integral']:+.3f}  "
              f"peak {r['peak_energy_mev']:.1f} MeV")
