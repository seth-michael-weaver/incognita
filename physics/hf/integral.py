"""KWCOV B10b: effective cross sections in integral spectra (`integral y`, integral.dat), OUTPUT ONLY.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

integral.f90 folds the run's excitation functions (the xs*.tot / xs*.Lnn files as written: the rows below eninclow are
thermal.f90's, `Results.thermal`) with the group spectra of structure/integral/spectra/<name>.txt:
xseff = 1e-3 sum_g xs(E_g) phi_g / sum_g phi_g barn, E_g = the group's mid energy, xs linear in E between the file's
rows with a (0, 0) point in front, groups above the last row left out. Which (reaction, spectrum, measured value)
triples: structure/integral/sacs/<Nuc><AAA>.sacs (target ground state, no deck triples), else the deck's
`integral <file> <spectrum> <value>` lines.

TALYS-2.25 bug kept (and warned): the deck form never produces a row. input_output.f90:326 stores the deck's file in
xsfluxfile, but integral.f90:111-143 rebuilds xsfluxfile from reacstr, which only the sacs reader fills, so a deck
triple looks for the file '.tot' and is skipped with "cross section file .tot does not exist".

TALYS routines ported here (file:line of the subroutine statement):
    integral.f90:1 (integral)      the sacs triples, the spectra, the fold, integral.dat's rows
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B10b, output only). Acceptance test: KWCOV-B10b
(tests/hf/test_kwcov_b10b.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import bisect
import warnings

import numpy as np

__all__ = ["REAC", "sacs_entries", "spectrum", "effective_b", "excitation", "integral_table", "parse_deck"]

#: integral.f90:114-131: reaction string -> channel file stem
REAC = {"n,g": "xs000000", "n,p": "xs010000", "n,d": "xs001000", "n,t": "xs000100", "n,h": "xs000010",
        "n,a": "xs000001", "n,2n": "xs200000", "n,np": "xs110000", "n,na": "xs100001", "n,2a": "xs000002",
        "n,2na": "xs200001", "n,3n": "xs300000", "n,4n": "xs400000", "n,pa": "xs010001", "n,da": "xs001001",
        "n,nt": "xs100100", "n,n2a": "xs100002", "n,3na": "xs300001"}


def sacs_entries(Z: int, A: int) -> list[dict]:
    """The target's sacs triples: [{"reac", "iso", "flux", "exp_b"}] (empty without a file). Words split on blanks
    (getkeywords), the measured value from columns 41-49 (integral.f90:99).

    TALYS: integral.f90:1 (integral) lines 86-106
    Test: tests/hf/test_kwcov_b10b.py
    """
    from physics.hf.core.constants import nuclide_symbol
    from physics.hf.structure.files import talys_structure_dir

    f = talys_structure_dir() / "integral" / "sacs" / f"{nuclide_symbol(Z).capitalize()}{A:03d}.sacs"
    if not f.is_file():
        return []
    out = []
    for line in f.read_text(errors="replace").splitlines():
        w = line.split()
        if len(w) < 5:
            continue
        out.append(dict(reac=w[2].lower(), iso=w[3].lower(), flux=w[4], exp_b=float(line[40:49])))
    return out


def spectrum(name: str) -> tuple[np.ndarray, np.ndarray] | None:
    """(E_mid in MeV, phi) of structure/integral/spectra/<name>.txt: two header lines, then `group Eup Elow
    lethargy data ...` rows in eV; None without the file.

    TALYS: integral.f90:1 (integral) lines 156-176
    Test: tests/hf/test_kwcov_b10b.py
    """
    from physics.hf.structure.files import talys_structure_dir

    f = talys_structure_dir() / "integral" / "spectra" / f"{name}.txt"
    if not f.is_file():
        return None
    e, s = [], []
    for line in f.read_text(errors="replace").splitlines()[2:]:
        w = line.split()
        try:
            eup, elo, sp = float(w[1]), float(w[2]), float(w[4])
        except (ValueError, IndexError):
            break  # list-directed read stops at the first bad row
        e.append(0.5 * (eup + elo) * 1.0e-6)
        s.append(sp)
    return np.asarray(e), np.asarray(s)


def effective_b(e_mev, xs_mb, e_flux, phi) -> float:
    """1e-3 sum xs(E_g) phi_g / sum phi_g (barn); xs linear between rows with (0, 0) in front, zero above the last row.

    TALYS: integral.f90:1 (integral) lines 210-227 (locate + pol1)
    Test: tests/hf/test_kwcov_b10b.py
    """
    ex = [0.0] + [float(x) for x in e_mev]
    xs = [0.0] + [float(x) for x in xs_mb]
    tot = 0.0
    for efl, sp in zip(e_flux, phi):
        efl = float(efl)
        if ex[0] <= efl <= ex[-1]:
            j = max(min(bisect.bisect_right(ex, efl) - 1, len(ex) - 2), 0)
            e1, e2 = ex[j], ex[j + 1]
            v = xs[j] + (efl - e1) * (xs[j + 1] - xs[j]) / (e2 - e1) if e2 != e1 else xs[j]
            tot += v * float(sp)
    return 1.0e-3 * tot / float(np.sum(phi))


def excitation(res, stem_ext: str) -> tuple[np.ndarray, np.ndarray] | None:
    """(E, xs) of one channel file as TALYS writes it: `Results.thermal`'s rows below eninclow, then the engine's
    rows; None when the run has no such channel (TALYS: the file does not exist). `stem_ext` = "xs000000.tot" or
    "xs000000.L02".

    TALYS: channelsout.f90:1 (channelsout) -- the rows integral.f90 reads back
    Test: tests/hf/test_kwcov_b10b.py
    """
    stem, ext = stem_ext.split(".")
    key = f"channels_mb/{stem}" if ext == "tot" else f"extras/{stem}.{ext}"
    part, name = key.split("/")
    src = getattr(res, part, {})
    if name not in src:
        return None
    e = res.e_inc_mev.detach().cpu().numpy().astype(float)
    v = np.asarray(src[name].detach().cpu().numpy() if hasattr(src[name], "detach") else src[name], dtype=float)
    th = getattr(res, "thermal", {}) or {}
    if th and key in th:
        low = float(th["eninclow"][0])
        keep = np.float32(e) >= np.float32(low)
        e = np.concatenate([np.asarray(th["E"], float), e[keep]])
        v = np.concatenate([np.asarray(th[key], float), v[keep]])
    return e, v


def parse_deck(lines) -> dict | None:
    """The deck's `integral` lines: None without `integral y` / a triple; else {"triples": [(file, spectrum, exp)]}.

    TALYS: input_output.f90:319-332
    Test: tests/hf/test_kwcov_b10b.py
    """
    on, triples = False, []
    for ln in lines:
        w = ln.split()
        if not w or w[0].lower() != "integral":
            continue
        v = w[1].lower() if len(w) > 1 else ""
        if v[:1] == "n" and len(v) == 1:
            on = False
        elif v[:1] == "y" and len(v) == 1:
            on = True
        else:
            if len(w) < 3:
                raise ValueError(f"deck line {ln!r}: expected `integral <xs file> <spectrum> [value]`")
            try:
                ex = float(w[3]) if len(w) > 3 else 0.0
            except ValueError:
                ex = 0.0
            triples.append((w[1], w[2], ex))
            on = True
    return {"triples": triples} if on else None


def integral_table(res, Z: int, A: int, triples=(), ltarget: int = 0) -> dict:
    """integral.dat as {"file", "spectrum": list, "xseff_b", "xsexp_b", "ratio": ndarray}, in integral.f90's order.

    TALYS: integral.f90:1 (integral)
    Test: tests/hf/test_kwcov_b10b.py
    """
    entries = []
    if not triples and ltarget == 0:
        entries = sacs_entries(Z, A)
    else:
        entries = [dict(reac="", iso="", flux=fl, exp_b=ex) for _, fl, ex in triples]
    rows = dict(file=[], spectrum=[], xseff_b=[], xsexp_b=[], ratio=[])
    for ent in entries:
        stem = REAC.get(ent["reac"], "")
        ext = "tot"
        cands = [f"{stem}.tot"]
        if ent["iso"] == "g":
            cands = [f"{stem}.L00"]
        elif ent["iso"] == "m":  # the first isomer file that exists, L01..
            cands = [f"{stem}.L{m:02d}" for m in range(1, 41)]
        sp = spectrum(ent["flux"])
        if sp is None:
            warnings.warn(f"TALYS-warning: integral spectrum file {ent['flux']}.txt does not exist", stacklevel=2)
            continue
        ex = None
        name = cands[0]
        for c in cands:
            ex = excitation(res, c) if stem else None
            if ex is not None:
                name = c
                break
        if ex is None:
            warnings.warn(f"TALYS-warning: cross section file {name if stem else '.' + ext} does not exist",
                          stacklevel=2)
            continue
        eff = effective_b(ex[0], ex[1], sp[0], sp[1])
        rows["file"].append(name)
        rows["spectrum"].append(ent["flux"])
        rows["xseff_b"].append(eff)
        rows["xsexp_b"].append(ent["exp_b"])
        rows["ratio"].append(eff / ent["exp_b"] if ent["exp_b"] > 0.0 else 1.0)
    return {"integral.dat": {k: (np.asarray(v) if k in ("xseff_b", "xsexp_b", "ratio") else v)
                             for k, v in rows.items()}}
