"""`INCOGNITA_CHANOBS`: the channel observables TALYS writes by default that `Results` does not otherwise carry, OUTPUT ONLY.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Every quantity here is already computed by `emission.channels.exclusive_channels` (channels.f90, totalxs.f90) or
`emission.binary.binary` (binary.f90); this module only names them the way TALYS names its files and columns, so a
comparison with a stock TALYS run is a join on the name. Names (all mb unless the suffix says otherwise):

    <p>prod.tot                 total particle production, p in g n p d t h a      productionout.f90:84, xsparticle
    <p>prod.tot:multiplicity    its yield column (xsparticle / xsnonel)            totalxs.f90:105-110
    binary.tot:<p>              binary non-elastic cross section per ejectile      binary.f90 xsbinary
    <k0><p>.tot:discrete        exclusive (k0,p) to discrete levels (xsdisctot)    discreteout.f90:278
    <k0><p>.tot:continuum       exclusive (k0,p) to the continuum (xsexclcont)     totalxs.f90:90 (xsngn not added)
    xsNNNNNN.tot:gamma          gamma production of an exclusive channel          channelsout.f90:315, xsgamchannel
    xsNNNNNN.LMM                isomeric/ground cross section of the channel      channelsout.f90:354, xschaniso
    xsNNNNNN.LMM:branch         its isomeric ratio (exclbranch)                    channelsout.f90:390
    xsNNNNNN.fis                exclusive fission channel (multi-chance)          channelsout.f90:552, xsfischannel

`MM` is the level's number in the level file (`levnum`, as TALYS and `multiple.isomer_files` write it), not the
index `nex`. Isomer files exist only for a channel whose residual has an isomer.

Switch: `INCOGNITA_CHANOBS` = 1/y/yes/on (default unset: nothing is computed or added, every array of every test is
unchanged). On the C driver it makes each energy take the Python channels (`exclusive_channels` on the C cascade's
`packed.result()`), the documented fallback of `engine_c.cases`, because `ce_channels` returns only the channel
cross sections.

TALYS routines ported here (file:line of the subroutine statement):
    totalxs.f90:1 (totalxs)            xsexclcont, multiplicity -- the parts `channels._channel_result` did not fill
    channelsout.f90:1 (channelsout)    file names and columns
Task: T10 (physics/hf/CONTRACT.md section 7; output only). Acceptance test: KWCOV-B1
(tests/hf/test_chanobs.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import os

ENV = "INCOGNITA_CHANOBS"
PARSYM = "gnpdtha"
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)


def enabled() -> bool:
    """True when `INCOGNITA_CHANOBS` asks for the extra channel observables.

    TALYS: (none -- a port switch)
    Test: tests/hf/test_chanobs.py
    """
    return os.environ.get(ENV, "").strip().lower() in ("1", "y", "yes", "on", "true")


def residual_of(code: int, Zcn: int, Acn: int) -> tuple[int, int]:
    """(Z, A) of the residual an exclusive channel `code` (digits n p d t h a) leaves from the compound (Zcn, Acn).

    TALYS: channels.f90:1 (channels) -- Zix/Nix of a channel
    Test: tests/hf/test_chanobs.py
    """
    d = [int(c) for c in f"{int(code):06d}"]
    dz = sum(n * PARZ[t + 1] for t, n in enumerate(d))
    dn = sum(n * PARN[t + 1] for t, n in enumerate(d))
    return Zcn - dz, Acn - dz - dn


def extras(ch, b, k0: int, Z: int, A: int, levnum=None, binp=None) -> dict[str, float]:
    """The CHANOBS names of one incident energy from a `ChannelResult` `ch` and a `BinaryResult` `b`.

    `levnum(Z, A)` gives {nex: level number} of a residual's isomers (default `multiple.LEVNUM`). `binp` (the
    energy's `BinaryInputs`) completes particle production: unless the triton binary rule already did it, the cascade got only the
    compound part of `xsbinary`, so the direct, pre-equilibrium, giant-resonance and direct-capture emission that
    multiple.f90:950 adds to xsfeed(0,0,type) is added here (xsparticle is a sum over xsfeed, so this is exact).

    TALYS: totalxs.f90:1 (totalxs), channelsout.f90:1, channelsout
    Test: tests/hf/test_chanobs.py
    """
    if levnum is None:
        from physics.hf.emission.multiple import LEVNUM

        def levnum(z, a):
            return LEVNUM.get((int(z), int(a)))

    out: dict[str, float] = {}
    part = {t: float(v) for t, v in ch.xsparticle_mb.items()}
    mult = {t: float(ch.multiplicity.get(t, 0.0)) for t in part}
    if binp is not None:
        from physics.hf.emission.multiple import binary_adds, tritfid_on

        if not tritfid_on():
            for t, add in binary_adds(binp):
                if t in part:
                    part[t] += add
            # totalxs.f90:105-110: multiplicity = xsparticle / xsnonel (the channels' own xsnonel, recovered)
            for t in part:
                x0, m0 = float(ch.xsparticle_mb[t]), mult[t]
                nonel = x0 / m0 if m0 else (float(b.xsnonel_mb) if b is not None else 0.0)
                mult[t] = part[t] / nonel if nonel else 0.0
    for t, v in part.items():
        out[f"{PARSYM[t]}prod.tot"] = v
        out[f"{PARSYM[t]}prod.tot:multiplicity"] = mult[t]
    if b is not None:
        xb = b.xsbinary_mb
        for t in range(7):
            out[f"binary.tot:{PARSYM[t]}"] = float(xb[t + 1])  # xsbinary is indexed -1..6
        for t, v in ch.xsexclusive_mb.items():
            disc = float(b.xsdisctot_mb[t])
            out[f"{PARSYM[k0]}{PARSYM[t]}.tot:discrete"] = disc
            out[f"{PARSYM[k0]}{PARSYM[t]}.tot:continuum"] = max(float(v) - disc, 0.0)  # totalxs.f90:90
    Zcn, Acn = Z + PARZ[k0], A + PARZ[k0] + PARN[k0]
    for code, g in ch.xsgamchannel_mb.items():
        stem = f"xs{int(code):06d}"
        out[f"{stem}.tot:gamma"] = float(g)
        f = ch.xsfischannel_mb.get(code, 0.0)
        if f:
            out[f"{stem}.fis"] = float(f)
        iso = ch.xschaniso_mb.get(code) or {}
        if not any(nex > 0 for nex in iso):
            continue
        num = levnum(*residual_of(code, Zcn, Acn)) or {}
        br = ch.exclbranch.get(code) or {}
        for nex, v in sorted(iso.items()):
            m = 0 if nex == 0 else int(num.get(nex, nex))
            out[f"{stem}.L{m:02d}"] = float(v)
            out[f"{stem}.L{m:02d}:branch"] = float(br.get(nex, 0.0))
    return out
