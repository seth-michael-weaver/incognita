"""TENDL-2025 residual production for proton and alpha beams, read from the ENDF-6 files.

TENDL's charged-particle sublibraries are on the IAEA-NDS mirror (tendl.web.psi.ch has not
resolved in DNS since 2026-09-08, see raw/MANIFEST.json ``unreachable``). They carry no
ready-made residual-production table, so production of a nuclide in a state is assembled from
three places, and each one is a way to get it wrong:

1. **Exclusive channels, MF3.** MT 4, 16, 17, 22, 28, ... each make exactly one residual,
   fixed by the emitted particles: for an incident proton MT 4 is (p,n) and makes Z+1, MT 16
   is (p,2n). The partial-level MTs (50-91, 600-849) are *components* of those sums and are
   skipped, or every (p,n) would be counted twice.
2. **Isomer split, MF10.** Where the evaluation resolves final states, MF10 gives the
   production cross section per final state directly (IZAP, LFS). A product whose
   contributing channels are not all resolved has an unknown isomer split, and is returned
   with ``state_complete=False`` rather than as a ground state that silently lacks a channel.
3. **The lumped channel MT 5, MF6.** Everything not given exclusively sits in MT 5, as
   sigma_5(E) times a product yield y_i(E) per (ZAP, LIP) in MF6; LIP is the isomer index.

Residuals whose ZA equals the target (elastic, inelastic) are dropped.

    uv run python -m physics.charged.tendl fetch   # needed targets only -> raw/endf/tendl2025/{p,he4}
"""
from __future__ import annotations

import io
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "raw" / "endf" / "tendl2025"
BASE = "https://www-nds.iaea.org/public/download-endf/TENDL-2025/"
SUBLIB = {"p": "p", "a": "he4", "d": "d"}
PROJ_ZA = {"p": (1, 1), "a": (2, 4), "d": (1, 2)}

_SYM = (
    "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn "
    "Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce "
    "Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn "
    "Fr Ra Ac Th Pa U"
).split()

# emitted (n, p, d, t, 3He, alpha) per exclusive MT (ENDF-6 manual, Appendix B)
EJECTILES: dict[int, tuple[int, int, int, int, int, int]] = {
    4: (1, 0, 0, 0, 0, 0), 11: (2, 0, 1, 0, 0, 0), 16: (2, 0, 0, 0, 0, 0),
    17: (3, 0, 0, 0, 0, 0), 22: (1, 0, 0, 0, 0, 1), 23: (1, 0, 0, 0, 0, 3),
    24: (2, 0, 0, 0, 0, 1), 25: (3, 0, 0, 0, 0, 1), 28: (1, 1, 0, 0, 0, 0),
    29: (1, 0, 0, 0, 0, 2), 30: (2, 0, 0, 0, 0, 2), 32: (1, 0, 1, 0, 0, 0),
    33: (1, 0, 0, 1, 0, 0), 34: (1, 0, 0, 0, 1, 0), 35: (1, 0, 1, 0, 0, 2),
    36: (1, 0, 0, 1, 0, 2), 37: (4, 0, 0, 0, 0, 0), 41: (2, 1, 0, 0, 0, 0),
    42: (3, 1, 0, 0, 0, 0), 44: (1, 2, 0, 0, 0, 0), 45: (1, 1, 0, 0, 0, 1),
    102: (0, 0, 0, 0, 0, 0), 103: (0, 1, 0, 0, 0, 0), 104: (0, 0, 1, 0, 0, 0),
    105: (0, 0, 0, 1, 0, 0), 106: (0, 0, 0, 0, 1, 0), 107: (0, 0, 0, 0, 0, 1),
    108: (0, 0, 0, 0, 0, 2), 109: (0, 0, 0, 0, 0, 3), 111: (0, 2, 0, 0, 0, 0),
    112: (0, 1, 0, 0, 0, 1), 113: (0, 0, 0, 1, 0, 2), 114: (0, 0, 1, 0, 0, 2),
    115: (0, 1, 1, 0, 0, 0), 116: (0, 1, 0, 1, 0, 0), 117: (0, 0, 1, 0, 0, 1),
    152: (5, 0, 0, 0, 0, 0), 153: (6, 0, 0, 0, 0, 0), 154: (2, 0, 0, 1, 0, 0),
    155: (0, 0, 0, 1, 0, 1), 156: (4, 1, 0, 0, 0, 0), 157: (3, 0, 1, 0, 0, 0),
    158: (1, 0, 1, 0, 0, 1), 159: (2, 1, 0, 0, 0, 1), 160: (7, 0, 0, 0, 0, 0),
    161: (8, 0, 0, 0, 0, 0), 162: (5, 1, 0, 0, 0, 0), 163: (6, 1, 0, 0, 0, 0),
    164: (7, 1, 0, 0, 0, 0), 165: (4, 0, 0, 0, 0, 1), 166: (5, 0, 0, 0, 0, 1),
    167: (6, 0, 0, 0, 0, 1), 168: (7, 0, 0, 0, 0, 1), 169: (4, 0, 1, 0, 0, 0),
    170: (5, 0, 1, 0, 0, 0), 171: (6, 0, 1, 0, 0, 0), 172: (3, 0, 0, 1, 0, 0),
    173: (4, 0, 0, 1, 0, 0), 174: (5, 0, 0, 1, 0, 0), 175: (6, 0, 0, 1, 0, 0),
    176: (2, 0, 0, 0, 1, 0), 177: (3, 0, 0, 0, 1, 0), 178: (4, 0, 0, 0, 1, 0),
    179: (3, 2, 0, 0, 0, 0), 180: (3, 0, 0, 0, 0, 2), 181: (3, 1, 0, 0, 0, 1),
    182: (0, 0, 1, 1, 0, 0), 183: (1, 1, 1, 0, 0, 0), 184: (1, 1, 0, 1, 0, 0),
    185: (1, 0, 1, 1, 0, 0), 186: (1, 1, 0, 0, 1, 0), 187: (1, 0, 1, 0, 1, 0),
    188: (1, 0, 0, 1, 1, 0), 189: (1, 0, 0, 1, 0, 1), 190: (2, 2, 0, 0, 0, 0),
    191: (0, 1, 0, 0, 1, 0), 192: (0, 0, 1, 0, 1, 0), 193: (0, 0, 0, 0, 1, 1),
    194: (4, 2, 0, 0, 0, 0), 195: (4, 0, 0, 0, 0, 2), 196: (4, 1, 0, 0, 0, 1),
    197: (0, 3, 0, 0, 0, 0), 198: (1, 3, 0, 0, 0, 0), 199: (3, 2, 0, 0, 0, 1),
    200: (5, 2, 0, 0, 0, 0),
}
_EJ_ZA = ((0, 1), (1, 1), (1, 2), (1, 3), (2, 3), (2, 4))


def residual_of(mt: int, Z: int, A: int, projectile: str) -> tuple[int, int] | None:
    ej = EJECTILES.get(mt)
    if ej is None:
        return None
    zp, ap = PROJ_ZA[projectile]
    dz = sum(k * z for k, (z, _) in zip(ej, _EJ_ZA, strict=True))
    da = sum(k * a for k, (_, a) in zip(ej, _EJ_ZA, strict=True))
    return Z + zp - dz, A + ap - da


# --------------------------------------------------------------------------------------------
# ENDF-6 record reader
# --------------------------------------------------------------------------------------------

def _f(s: str) -> float:
    s = s.strip()
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        # 1.234567+5 / 1.234567-5
        for i in range(len(s) - 1, 0, -1):
            if s[i] in "+-" and s[i - 1] not in "eE":
                return float(s[:i] + "e" + s[i:])
        raise


class Section:
    """Sequential reader over one MF/MT section's 66-column payload."""

    def __init__(self, lines: list[str]):
        self.lines = lines
        self.i = 0

    def _fields(self) -> list[str]:
        ln = self.lines[self.i]
        self.i += 1
        return [ln[k:k + 11] for k in range(0, 66, 11)]

    def cont(self) -> tuple[float, float, int, int, int, int]:
        f = self._fields()
        return (_f(f[0]), _f(f[1]), int(_f(f[2])), int(_f(f[3])), int(_f(f[4])), int(_f(f[5])))

    def _values(self, n: int) -> list[float]:
        out: list[float] = []
        while len(out) < n:
            f = self._fields()
            out.extend(_f(x) for x in f[: min(6, n - len(out))])
        return out

    def tab1(self):
        c1, c2, l1, l2, nr, np_ = self.cont()
        self._values(2 * nr)
        xy = np.array(self._values(2 * np_), float).reshape(-1, 2)
        return (c1, c2, l1, l2), xy[:, 0], xy[:, 1]

    def tab2(self):
        c1, c2, l1, l2, nr, nz = self.cont()
        self._values(2 * nr)
        return (c1, c2, l1, l2), nz

    def list_(self):
        c1, c2, l1, l2, npl, n2 = self.cont()
        return (c1, c2, l1, l2, n2), self._values(npl)


def split_sections(text: str) -> dict[tuple[int, int], list[str]]:
    out: dict[tuple[int, int], list[str]] = defaultdict(list)
    for ln in text.splitlines():
        if len(ln) < 75:
            continue
        try:
            mf, mt = int(ln[70:72]), int(ln[72:75])
        except ValueError:
            continue
        if mt == 0 or mf == 0:
            continue
        out[(mf, mt)].append(ln)
    return out


def _skip_law(sec: Section, law: int) -> None:
    if law in (0, 3, 4):
        return
    if law in (1, 2, 5):
        _, ne = sec.tab2()
        for _ in range(ne):
            sec.list_()
        return
    if law == 6:
        sec.cont()
        return
    if law == 7:
        _, ne = sec.tab2()
        for _ in range(ne):
            _, nmu = sec.tab2()
            for _ in range(nmu):
                sec.tab1()
        return
    raise ValueError(f"MF6 LAW={law} not handled")


def residual_production(text: str, Z: int, A: int, projectile: str,
                        grid_mev: np.ndarray | None = None) -> list[dict]:
    """Production cross sections (mb) per (product_z, product_a, state) on ``grid_mev``."""
    secs = split_sections(text)
    if grid_mev is None:
        e = secs.get((3, 5))
        grid_mev = Section(e).tab1()[1] * 1e-6 if e else np.linspace(1, 60, 60)
    grid_ev = np.asarray(grid_mev, float) * 1e6
    tot: dict[tuple[int, int], np.ndarray] = defaultdict(lambda: np.zeros_like(grid_ev))
    st: dict[tuple[int, int, int], np.ndarray] = defaultdict(lambda: np.zeros_like(grid_ev))
    unresolved: set[tuple[int, int]] = set()
    target = (Z, A)

    def on_grid(x, y):
        return np.interp(grid_ev, x, y, left=0.0, right=0.0)

    for (mf, mt), lines in sorted(secs.items()):
        if mf != 3 or mt == 5 or mt not in EJECTILES:
            continue
        res = residual_of(mt, Z, A, projectile)
        if res is None or res == target or res[1] <= 0:
            continue
        sec = Section(lines)
        sec.cont()
        _, x, y = sec.tab1()
        tot[res] += on_grid(x, y) * 1e3
        if (10, mt) in secs:
            s10 = Section(secs[(10, mt)])
            _, _, _, _, ns, _ = s10.cont()
            for _ in range(ns):
                (qm, qi, izap, lfs), x10, y10 = s10.tab1()
                zr, ar = divmod(int(izap), 1000)
                st[(zr, ar, 1000 + int(lfs))] += on_grid(x10, y10) * 1e3
        else:
            unresolved.add(res)

    if (3, 5) in secs and (6, 5) in secs:
        s3 = Section(secs[(3, 5)])
        s3.cont()
        _, x5, y5 = s3.tab1()
        sig5 = on_grid(x5, y5) * 1e3
        s6 = Section(secs[(6, 5)])
        _, _, _, _, nk, _ = s6.cont()
        for _ in range(nk):
            (zap, awp, lip, law), xy_e, yld = s6.tab1()
            _skip_law(s6, law)
            zr, ar = divmod(int(zap), 1000)
            if ar < 5 or (zr, ar) == target:
                continue
            prod = sig5 * on_grid(xy_e, yld)
            tot[(zr, ar)] += prod
            st[(zr, ar, int(lip))] += prod

    # MF10's LFS is the LEVEL NUMBER of the final state (99mTc is LFS=2), while MF6's LIP is
    # the ISOMER INDEX (99mTc is LIP=1). Keying both on the raw number filed 99mTc's
    # exclusive-channel production as "M2" and its MT-5 production as "M" -- two halves of one
    # state under two labels. Positive LFS values are ranked per product to recover the index.
    lfs_rank: dict[tuple[int, int], dict[int, int]] = {}
    for (zr, ar, k) in list(st):
        if k >= 1000:  # MF10 entries are stored offset by 1000 below
            lfs_rank.setdefault((zr, ar), {})[k - 1000] = 0
    for key, levels in lfs_rank.items():
        for i, lev in enumerate(sorted(v for v in levels if v > 0), start=1):
            levels[lev] = i
    merged: dict[tuple[int, int, int], np.ndarray] = defaultdict(lambda: np.zeros_like(grid_ev))
    for (zr, ar, k), xs in st.items():
        iso = lfs_rank[(zr, ar)][k - 1000] if k >= 1000 else k
        merged[(zr, ar, iso)] += xs
    st = merged

    out = []
    for (zr, ar), xs in tot.items():
        out.append({"product_z": zr, "product_a": ar, "state": "", "state_complete": True,
                    "E_mev": grid_ev * 1e-6, "xs_mb": xs})
    for (zr, ar, k), xs in st.items():
        out.append({"product_z": zr, "product_a": ar,
                    "state": "G" if k == 0 else ("M" if k == 1 else f"M{k}"),
                    "state_complete": (zr, ar) not in unresolved,
                    "E_mev": grid_ev * 1e-6, "xs_mb": xs})
    return out


def local_path(Z: int, A: int, projectile: str) -> Path:
    sub = SUBLIB[projectile]
    return RAW / sub / f"{sub}_{Z:03d}-{_SYM[Z - 1]}-{A}.zip"


def read_target(Z: int, A: int, projectile: str, grid_mev=None) -> list[dict]:
    p = local_path(Z, A, projectile)
    zf = zipfile.ZipFile(p)
    text = zf.read(zf.namelist()[0]).decode("latin1")
    return residual_production(text, Z, A, projectile, grid_mev)


def fetch(targets) -> None:
    import re
    from urllib.request import Request, urlopen

    sys.path.insert(0, str(REPO))
    from data.ingest.download import digest, load_manifest, now, save_manifest

    listings: dict[str, list[str]] = {}
    got = []
    for Z, A, proj in targets:
        sub = SUBLIB[proj]
        if sub not in listings:
            with urlopen(Request(BASE + sub + "/", headers={"User-Agent": "Mozilla/5.0"}),
                         timeout=60) as r:
                listings[sub] = re.findall(r'href="([^"]+\.zip)"', r.read().decode())
        pat = f"{sub}_{Z:03d}-{_SYM[Z - 1]}-{A}_"
        names = [n for n in listings[sub] if n.startswith(pat)]
        if not names:
            print(f"[tendl] no {sub} file for Z={Z} A={A}")
            continue
        dest = local_path(Z, A, proj)
        if not dest.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            with urlopen(Request(BASE + sub + "/" + names[0],
                                 headers={"User-Agent": "Mozilla/5.0"}), timeout=120) as r:
                dest.write_bytes(r.read())
        got.append((dest, BASE + sub + "/" + names[0]))
    m = load_manifest()
    for dest, url in got:
        m["files"][str(dest.relative_to(REPO / "raw"))] = {
            "source": "tendl2025_charged", "url": url, "phase": 3, "status": "adopted",
            "license": "TENDL: CC BY 4.0, cite Koning et al. NDS 155 (2019) 1",
            "fetched_at": now(), "bytes": dest.stat().st_size, "sha256": digest(dest),
            "problems": None,
            "notes": "TENDL-2025 charged-particle sublibrary, WP-25 medical targets only",
        }
    save_manifest(m)
    print(f"[tendl] {len(got)} files present")


if __name__ == "__main__":
    from omegaconf import OmegaConf

    cfg = OmegaConf.load(REPO / "configs" / "charged_medical_sweep.yaml")
    fetch([(int(z), int(a), str(p)) for z, a, p in cfg.targets])
