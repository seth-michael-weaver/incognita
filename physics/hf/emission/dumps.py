"""Loaders for the T10 instrumented-TALYS dumps (`talys_instrument/chdump.f90`).

The dumps are not TALYS output files; they are the injection channel required by CONTRACT.md §5,
carrying exactly the module globals `binary.f90`, `channels.f90`, `totalxs.f90` and `residual.f90`
read, so the ports of those routines can be scored before the upstream ports are chained in.

Task: T10 (physics/hf/CONTRACT.md §7). Acceptance test: A-mult (§6).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.emission.binary import NUMJ, BinaryInputs, ResidualGrid


def _f(x: str) -> float:
    return float(x)


def load_binary_dump(path: str | Path) -> list[BinaryInputs]:
    """Parse `bin_inputs.txt` into one `BinaryInputs` per incident energy.

    TALYS: binary.f90:1 (binary) -- the module globals it reads on entry
    Test: A-mult
    """
    cases: list[BinaryInputs] = []
    cur: dict | None = None

    def finish():
        if cur is None:
            return
        grids, xspop, xspopex, dd, ppx, sfacs = {}, {}, {}, {}, {}, {}
        for t, m in cur["types"].items():
            n = m["maxex"] + 1
            ex = torch.zeros(n, dtype=DTYPE)
            de = torch.zeros(n, dtype=DTYPE)
            mj = torch.zeros(n, dtype=torch.int64)
            ald = torch.zeros(n, dtype=DTYPE)
            sc = torch.ones(n, dtype=DTYPE)
            pex = torch.zeros(n, dtype=DTYPE)
            pp = torch.zeros(n, dtype=DTYPE)
            par = torch.zeros(n, dtype=torch.int64)
            jd = torch.zeros(n, dtype=DTYPE)
            ddv = torch.zeros(n, dtype=DTYPE)
            for nex, maxj, e, d, px, pq, a, s in m["nex"]:
                ex[nex], de[nex], mj[nex], pex[nex], pp[nex] = e, d, maxj, px, pq
                ald[nex] = a
                if s > 0:
                    sc[nex] = s
            for nex, p, j, x in m["lev"]:
                par[nex], jd[nex], ddv[nex] = p, j, x
            grids[t] = ResidualGrid(
                type=t, zix=m["zix"], nix=m["nix"], maxex=m["maxex"], nlast=m["nl"],
                ex_mev=ex, dex_mev=de, maxj=mj, parlev=par, jdis=jd, ald=ald, spincut=sc,
            )
            pop = torch.zeros((n, NUMJ + 1, 2), dtype=DTYPE)
            for nex, J, P, v in m["pop"]:
                pop[nex, J, 0 if P == -1 else 1] = v
            xspop[t], xspopex[t], dd[t], ppx[t] = pop, pex, ddv, pp
            sfacs[t] = m
        cases.append(BinaryInputs(
            e_inc_mev=cur["einc"], k0=cur["k0"], ltarget=cur["ltarget"],
            targetspin2=cur["targetspin2"], target_parity=cur["targetP"],
            pespinmodel=cur["pespinmodel"], maxjph=cur["maxjph"], numj=cur["numj"],
            popeps_mb=cur["popeps"], xseps_mb=cur["xseps"], xsreacinc_mb=cur["xsreacinc"],
            xselasinc_mb=cur["xselasinc"], xsdirdiscsum_mb=cur["xsdirdiscsum"],
            xspreeqsum_mb=cur["xspreeqsum"], xsgrsum_mb=cur["xsgrsum"],
            xsracape_mb=cur["xsracape"], flagpreeq=cur["flagpreeq"], grids=grids,
            xspop_mb=xspop, xspopex_mb=xspopex,
            xspopnuc_mb={t: m["xspopnuc"] for t, m in cur["types"].items()},
            xsdirdisc_mb=dd, preeqpopex_mb=ppx,
            xsdirdisctot_mb={t: m["ddtot"] for t, m in cur["types"].items()},
            xspreeqtot_mb={t: m["petot"] for t, m in cur["types"].items()},
            xsgrtot_mb={t: m["grtot"] for t, m in cur["types"].items()},
            xscompcont_mb={t: m["compcont"] for t, m in cur["types"].items()},
            xsbinary_mb=torch.tensor(cur["xsbinary"], dtype=DTYPE),
        ))

    with open(path) as fh:
        for line in fh:
            tag, rest = line[:5].strip(), line[5:].split()
            if tag == "EINC":
                finish()
                cur = {"einc": _f(rest[1]), "types": {}, "xsbinary": [0.0] * 8}
            elif tag == "INTS":
                v = list(map(int, rest))
                (cur["k0"], cur["ltarget"], cur["targetspin2"], cur["targetP"],
                 cur["pespinmodel"], cur["maxjph"], cur["numj"], _nlow) = v
            elif tag == "FLAG":
                cur["flagpreeq"] = rest[0] == "T"
            elif tag == "SCAL":
                (cur["popeps"], cur["xseps"], cur["xsreacinc"], cur["xselasinc"],
                 cur["xsdirdiscsum"], cur["xspreeqsum"], cur["xsgrsum"], cur["xsracape"],
                 _pardis) = map(_f, rest)
            elif tag == "XSBI":
                cur["xsbinary"] = list(map(_f, rest))
            elif tag == "TYPE":
                t = int(rest[0])
                cur["types"][t] = dict(
                    zix=int(rest[1]), nix=int(rest[2]), maxex=int(rest[3]), nl=int(rest[4]),
                    ddtot=_f(rest[5]), petot=_f(rest[6]), grtot=_f(rest[7]),
                    compcont=_f(rest[8]), xspopnuc=_f(rest[9]), nex=[], lev=[], pop=[])
            elif tag == "NEX":
                t = int(rest[0])
                cur["types"][t]["nex"].append(
                    (int(rest[1]), int(rest[2]), _f(rest[3]), _f(rest[4]), _f(rest[5]),
                     _f(rest[6]), _f(rest[7]), _f(rest[8])))
            elif tag == "LEV":
                t = int(rest[0])
                cur["types"][t]["lev"].append((int(rest[1]), int(rest[2]), _f(rest[3]), _f(rest[4])))
            elif tag == "POP":
                t = int(rest[0])
                cur["types"][t]["pop"].append((int(rest[1]), int(rest[2]), int(rest[3]), _f(rest[4])))
    finish()
    return cases


# ------------------------------------------------------------------------------------------------
# channels.f90 / totalxs.f90 / residual.f90 inputs
# ------------------------------------------------------------------------------------------------


@dataclass
class NucleusState:
    """One residual nucleus as channels.f90 sees it, after multiple.f90 has decayed everything."""

    zcomp: int
    ncomp: int
    Z: int
    N: int
    A: int
    maxex: int
    nlast: int
    xspopnuc_mb: float
    qres_mev: float
    xsgamdistot_mb: float
    skipcn: float
    edis_mev: dict[int, float] = field(default_factory=dict)
    tau_s: dict[int, float] = field(default_factory=dict)
    sep_mev: dict[int, float] = field(default_factory=dict)  # type -> S(Zcomp, Ncomp, type)
    index: dict[int, tuple[int, int]] = field(default_factory=dict)  # type -> (Zix, Nix)
    popexcl_mb: dict[int, float] = field(default_factory=dict)  # nex -> popexcl
    fisfeedex_mb: dict[int, float] = field(default_factory=dict)
    xspopex_mb: dict[int, float] = field(default_factory=dict)
    xsfeed_mb: dict[int, float] = field(default_factory=dict)  # type -1..6
    feedexcl_mb: dict[int, dict[tuple[int, int], float]] = field(default_factory=dict)


@dataclass
class ChannelInputs:
    """Everything channels.f90 / totalxs.f90 / residual.f90 read, for one incident energy."""

    nin: int
    e_inc_mev: float
    k0: int
    ltarget: int
    maxz: int
    maxn: int
    zinit: int
    ninit: int
    maxchannel: int
    ninclow: int
    xseps_mb: float
    targete_mev: float
    specmass: float
    xsreacinc_mb: float
    xsnonel_mb: float
    flagfission: bool
    flaginitpop: bool
    flagchannels: bool
    parinclude: list[bool]  # index 0 == type -1
    parskip: list[bool]  # index 0 == type 0
    xsbinary_mb: list[float]  # types -1..6
    chanopen: set[tuple[int, int, int, int, int, int]] = field(default_factory=set)
    idnumfull: bool = False
    nuclei: dict[tuple[int, int], NucleusState] = field(default_factory=dict)


def load_channel_dump(path: str | Path) -> list[ChannelInputs]:
    """Parse `ch_inputs.txt` into one `ChannelInputs` per incident energy.

    TALYS: channels.f90:1 (channels) -- the module globals it reads on entry
    Test: A-mult
    """
    cases: list[ChannelInputs] = []
    cur: ChannelInputs | None = None
    with open(path) as fh:
        for line in fh:
            tag, rest = line[:5].strip(), line[5:].split()
            if tag == "EINC":
                cur = ChannelInputs(
                    nin=int(rest[0]), e_inc_mev=_f(rest[1]), k0=1, ltarget=0, maxz=0, maxn=0,
                    zinit=0, ninit=0, maxchannel=4, ninclow=0, xseps_mb=0.0, targete_mev=0.0,
                    specmass=1.0, xsreacinc_mb=0.0, xsnonel_mb=0.0, flagfission=False,
                    flaginitpop=False, flagchannels=True, parinclude=[], parskip=[],
                    xsbinary_mb=[0.0] * 8)
                cases.append(cur)
            elif tag == "GLOB":
                (cur.k0, cur.ltarget, cur.maxz, cur.maxn, cur.zinit, cur.ninit, cur.maxchannel,
                 cur.ninclow) = map(int, rest[:8])
                (cur.xseps_mb, cur.targete_mev, cur.specmass, cur.xsreacinc_mb,
                 cur.xsnonel_mb) = map(_f, rest[8:13])
            elif tag == "FLAG":
                cur.flagfission, cur.flaginitpop, cur.flagchannels = [x == "T" for x in rest]
            elif tag == "PINC":
                cur.parinclude = [x == "T" for x in rest]
            elif tag == "PSKP":
                cur.parskip = [x == "T" for x in rest]
            elif tag == "BIN":
                cur.xsbinary_mb = list(map(_f, rest))
            elif tag == "COPN":
                cur.chanopen.add(tuple(map(int, rest)))
            elif tag == "FULL":
                cur.idnumfull = True
            elif tag == "NUC":
                zc, nc = int(rest[0]), int(rest[1])
                cur.nuclei[(zc, nc)] = NucleusState(
                    zcomp=zc, ncomp=nc, Z=int(rest[2]), N=int(rest[3]), A=int(rest[4]),
                    maxex=int(rest[5]), nlast=int(rest[6]), xspopnuc_mb=_f(rest[7]),
                    qres_mev=_f(rest[8]), xsgamdistot_mb=_f(rest[9]), skipcn=_f(rest[10]))
            elif tag == "LEV":
                n = cur.nuclei[(int(rest[0]), int(rest[1]))]
                n.edis_mev[int(rest[2])] = _f(rest[3])
                n.tau_s[int(rest[2])] = _f(rest[4])
            elif tag == "XFD":
                cur.nuclei[(int(rest[0]), int(rest[1]))].xsfeed_mb[int(rest[2])] = _f(rest[3])
            elif tag == "SEP":
                n = cur.nuclei[(int(rest[0]), int(rest[1]))]
                n.sep_mev[int(rest[2])] = _f(rest[5])
                n.index[int(rest[2])] = (int(rest[3]), int(rest[4]))
            elif tag == "PEX":
                n = cur.nuclei[(int(rest[0]), int(rest[1]))]
                n.popexcl_mb[int(rest[2])] = _f(rest[3])
                n.fisfeedex_mb[int(rest[2])] = _f(rest[4])
            elif tag == "PXE":
                cur.nuclei[(int(rest[0]), int(rest[1]))].xspopex_mb[int(rest[2])] = _f(rest[3])
            elif tag == "FEED":
                n = cur.nuclei[(int(rest[0]), int(rest[1]))]
                n.feedexcl_mb.setdefault(int(rest[2]), {})[(int(rest[3]), int(rest[4]))] = _f(rest[5])
    return cases
