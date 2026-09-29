"""`jcore` / `pcore`: the spin and parity of the CORE level an odd-A target's weakly-coupled level
came from, which is the spin `directecis.f90:207-213` hands ECIS for the DWBA -- not the target
level's own `jdis`/`parlev`.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T13 (physics/hf/CONTRACT.md §7). Acceptance test: A-direct.

TALYS routines ported here (file:line of the subroutine/function statement):
    weakcoupling.f90:1 (weakcoupling)
    directecis.f90:1 (directecis)

T2 owns `physics/hf/structure/deformation.py` and its `weak_coupling` returns only the updated
`deform`, dropping `jcore(Zix, Nix, i5) = jdis(core, i)` and `pcore(...) = parlev(core, i)`
(weakcoupling.f90:135-136). T2 has finished, so rather than edit that file this module repeats
the *same* search and records the two arrays it throws away; the proposed patch is on
`<lab-run>/requests.md` as `[T13 -> T2]`. `test_ecis.py` pins the two searches to the same
answer -- the level set this returns a core spin for is exactly the set T2 gives a non-zero
`deform`.
"""

from __future__ import annotations

import numpy as np

from physics.hf.structure.deformation import NUMLEV2

_F = np.float32  # T2's single-precision helper (deformation.py:57)

__all__ = ["core_spins", "dwba_level_spins"]


def core_spins(target, target_levels, core, core_levels) -> tuple[np.ndarray, np.ndarray]:
    """(jcore, pcore) over levels 0..numlev2 of an odd-A target, zero where weak coupling put
    nothing. Arguments are exactly `structure.deformation.weak_coupling`'s, minus `options`.

    TALYS: weakcoupling.f90:1 (weakcoupling)
    Test: A-direct
    """
    nmax2 = target_levels.nlevmax2
    te = np.zeros(NUMLEV2 + 1)
    tj = np.zeros(NUMLEV2 + 1)
    te[: nmax2 + 1] = target_levels.all_e_mev.numpy()
    tj[: nmax2 + 1] = target_levels.all_spin.numpy()
    ce = np.zeros(NUMLEV2 + 1)
    cj = np.zeros(NUMLEV2 + 1)
    cp = np.zeros(NUMLEV2 + 1, dtype=np.int64)
    cm = core_levels.nlevmax2
    ce[: cm + 1] = core_levels.all_e_mev.numpy()
    cj[: cm + 1] = core_levels.all_spin.numpy()
    cp[: cm + 1] = core_levels.all_parity.numpy().astype(np.int64)
    deform = target.deform.copy()
    jcore = np.zeros(NUMLEV2 + 1)
    pcore = np.zeros(NUMLEV2 + 1, dtype=np.int64)
    j0 = _F(tj[0])
    for i in range(0, NUMLEV2 + 1):
        if i == 0 or target.leveltype[i] in ("R", "V") or core.deform[i] == 0.0:
            continue
        middle = 0
        for i2 in range(1, NUMLEV2 + 1):
            if te[i2] > ce[i]:
                middle = i2 + 1
                break
        jc = _F(cj[i])
        for j in range(int(abs(j0 - jc)), int(j0 + jc) + 1):
            done = False
            for i3 in range(0, NUMLEV2 + 1):
                for i4 in (1, -1):
                    if i3 == 0 and i4 == -1:
                        break
                    i5 = middle + i4 * i3
                    if i5 < 1 or i5 > nmax2 or deform[i5] != 0.0:
                        continue
                    if target.leveltype[i5] != "D" or int(tj[i5]) != j:
                        continue
                    deform[i5] = 1.0  # only the "taken" marker matters here
                    jcore[i5] = float(cj[i])
                    pcore[i5] = int(cp[i])
                    done = True
                    break
                if done:
                    break
    return jcore, pcore


def dwba_level_spins(struct, index, jcore, pcore, nlev: int) -> tuple[np.ndarray, np.ndarray]:
    """The (spin, parity) `directecis.f90:203-214` gives ECIS for each level of `index`.

    Even A: the level's own `jdis`/`parlev`. Odd A: the core spin, except that a target with a
    single known level, or level 1 with `jcore == 0`, is given a bare 2+.

    `pcore == 0` means "weakcoupling.f90 never assigned this level a core", and it is NOT a
    parity. `weakcoupling.f90:44` skips every level whose `leveltype` is 'R' or 'V', so a band
    head inside a rotational nucleus keeps `jcore = pcore = 0`, and directecis.f90:211-212 then
    writes `Jlevel(2) = 0.` and `Plevel(2) = cparity(0)`, which constants.f90:113 defines as a
    **blank**, not '-'. ECIS reads the blank as positive and solves a lambda = 0 form factor with
    the level's own `deform`. Returning 0 here instead makes `dwba.dwba_xs`'s natural-parity test
    (`pb != (-1) ** lam`) reject the level and hand back exactly zero.

    That is Am-241: level 4 (0.20588 MeV) is the K = 5/2+ band head, `Am.def` row
    `4 V 1 3 0 0.70000`, and `deformpar.f90:205-207` carries beta = 0.7 onto `deform(4)` because
    `vibband > maxband` demotes it to 'D' for that branch alone. TALYS gives it **870.35 mb** of
    the 1012.43 mb of direct at 0.5 MeV; the port gave 0, the flux went back to the compound
    nucleus, and Am-241's `total inelastic` sat 21 % low with `(n,f)`, `(n,g)` and compound
    elastic sharing the surplus (docs/results/hf-open2.md section 3).

    TALYS: directecis.f90:1 (directecis), weakcoupling.f90:1 (weakcoupling),
           constants.f90:1 (constants) -- `cparity` is set at constants.f90:113
    Test: A-direct / tests/hf/test_open2.py::test_am241_band_head_is_a_blank_parity_dwba_level
    """
    idx = np.asarray(index, dtype=np.int64)
    if struct.Atarget % 2 == 0:
        return struct.jdis[idx], struct.parlev[idx].astype(np.int64)
    spin = np.empty(idx.shape, dtype=float)
    par = np.empty(idx.shape, dtype=np.int64)
    for n, i in enumerate(idx.tolist()):
        if nlev == 1 or (i == 1 and jcore[i] == 0.0):
            spin[n], par[n] = 2.0, 1
        else:
            # cparity(0) is ' ', and ECIS reads a blank parity as positive
            spin[n], par[n] = float(jcore[i]), int(pcore[i]) or 1
    return spin, par
