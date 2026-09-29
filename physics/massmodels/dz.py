"""Duflo-Zuker masses.

* :func:`dz10_binding_mev` is a line-by-line Python port of the 10-parameter formula
  ``du_zu_10.feb96`` (J. Duflo and A.P. Zuker, Feb 1996; ``raw/mass_models/dz/``),
  quoted rms 506 keV on the 1810 masses known in 1996.
* :func:`load_dz28_table` reads ``DZ28_RBF.txt`` (Wang and Liu, PRC 84 (2011) 051303):
  DZ28 binding energies, with and without the RBF correction, converted to mass excesses.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from physics.massmodels.paths import DZ_DIR, ME_H_KEV, ME_N_KEV

__all__ = ["dz10_binding_mev", "dz10_mass_excess_kev", "dz10_table", "load_dz28_table"]

DZ10_CITATION = "Duflo and Zuker, PRC 52 (1995) R23; 10-parameter form, AMDC Feb 1996"
DZ28_CITATION = (
    "Duflo and Zuker 28-parameter formula as tabulated by Wang and Liu, PRC 84 (2011) 051303"
)

# Fortran ``b(10)`` coefficients.
_B = (0.7043, 17.7418, 16.2562, 37.5562, 53.9017, 0.4711, 2.1307, 0.0210, 40.5356, 6.0632)


def dz10_binding_mev(nx: int, nz: int) -> float:
    """Binding energy (MeV) of the nucleus with ``nx`` neutrons and ``nz`` protons.

    Straight port of ``subroutine mass10``; variable names follow the Fortran so the two
    can be read side by side. Integer divisions are kept as Fortran truncation.
    """
    nn = (nx, nz)
    a = float(nx + nz)
    t = float(abs(nx - nz))
    r = a ** (1.0 / 3.0)
    rc = r * (1.0 - 0.25 * (t / a) ** 2)  # charge radius
    ra = (rc * rc) / r

    dyda = [0.0] * 11  # 1-indexed like the Fortran
    z2 = float(nz * (nz - 1))
    dyda[1] = (-z2 + 0.76 * z2 ** (2.0 / 3.0)) / rc  # Coulomb energy

    y = [0.0, 0.0, 0.0]
    for ndef in (1, 2):  # 1 spherical, 2 deformed
        ju = 4 if ndef == 2 else 0
        y[ndef] = 0.0
        for kk in range(2, 11):
            dyda[kk] = 0.0
        op = [0.0, 0.0, 0.0]
        os_ = [0.0, 0.0, 0.0]
        n2 = [0, 0, 0]
        dx = [0.0, 0.0, 0.0]
        qx = [0.0, 0.0, 0.0]
        pp = [0.0, 0.0, 0.0]
        for j in (1, 2):
            noc = [0] * 20  # noc(18) in the Fortran; 1-indexed
            onp = [[0.0] * 3 for _ in range(10)]  # onp(0:8, 2)  -> onp[ip][1|2]
            n2[j] = 2 * (nn[j - 1] // 2)  # for pairing
            ncum = 0
            i = 0
            while True:  # sub-shells (ssh) j and r filling
                i += 1
                i2 = (i // 2) * 2
                if i2 != i:
                    idd = i + 1  # for ssh j
                else:
                    idd = i * (i - 2) // 4  # for ssh r
                ncum += idd
                if ncum < nn[j - 1]:
                    noc[i] = idd  # nb of nucleons in each ssh
                    continue
                break
            imax = i + 1  # last subshell nb
            ip = (i - 1) // 2  # HO number (p)
            ipm = i // 2
            pp[j] = float(ip)
            moc = nn[j - 1] - ncum + idd
            noc[i] = moc - ju  # nb of nucleons in last ssh
            noc[i + 1] = ju
            if i2 != i:  # ssh j
                oei = float(moc + ip * (ip - 1))  # nb of nucleons in last EI shell
                dei = float(ip * (ip + 1) + 2)  # size of the EI shell
            else:  # ssh r
                oei = float(moc - ju)
                dei = float((ip + 1) * (ip + 2) + 2)
            qx[j] = oei * (dei - oei - ju) / dei  # n*(D-n)/D        S3(j)
            dx[j] = qx[j] * (2 * oei - dei)  # n*(D-n)*(2n-D)/D  Q
            if ndef == 2:
                qx[j] = qx[j] / math.sqrt(dei)  # scaling for deformed
            for ii in range(1, imax + 1):  # amplitudes
                ipp = (ii - 1) // 2
                fact = math.sqrt((ipp + 1.0) * (ipp + 2.0))
                onp[ipp][1] += noc[ii] / fact  # for FM term
                vm = -1.0
                if (2 * (ii // 2)) != ii:
                    vm = 0.5 * ipp  # for spin-orbit term
                onp[ipp][2] += noc[ii] * vm
            op[j] = 0.0
            os_[j] = 0.0
            for ipp in range(0, ipm + 1):  # FM and SO terms
                pi = float(ipp)
                den = ((pi + 1) * (pi + 2)) ** 1.5
                op[j] += onp[ipp][1]  # FM
                os_[j] += onp[ipp][2] * (1.0 + onp[ipp][1]) * (pi * pi / den) + onp[ipp][2] * (
                    1.0 - onp[ipp][1]
                ) * ((4 * pi - 5) / den)  # SO
            op[j] = op[j] * op[j]
        # end of loop over N and Z
        dyda[2] = op[1] + op[2]  # master term (FM): volume
        dyda[3] = -dyda[2] / ra  # surface
        dyda[2] = dyda[2] + os_[1] + os_[2]  # FM + SO
        dyda[4] = -t * (t + 2) / (r * r)  # isospin term: volume
        dyda[5] = -dyda[4] / ra  # surface
        if ndef == 1:
            dyda[6] = dx[1] + dx[2]  # S3 volume
            dyda[7] = -dyda[6] / ra  # surface
            px = math.sqrt(pp[1]) + math.sqrt(pp[2])
            dyda[8] = qx[1] * qx[2] * (2**px)  # QQ sph.
        else:
            dyda[9] = qx[1] * qx[2]  # QQ deform.
        dyda[5] = t * (1 - t) / (a * ra**3) + dyda[5]  # "Wigner term"
        # pairing
        if n2[1] != nn[0] and n2[2] != nn[1]:
            dyda[10] = t / a
        if nx > nz:
            if n2[1] == nn[0] and n2[2] != nn[1]:
                dyda[10] = 1 - t / a
            if n2[1] != nn[0] and n2[2] == nn[1]:
                dyda[10] = 1.0
        else:
            if n2[1] == nn[0] and n2[2] != nn[1]:
                dyda[10] = 1.0
            if n2[1] != nn[0] and n2[2] == nn[1]:
                dyda[10] = 1 - t / a
        if n2[2] == nn[1] and n2[1] == nn[0]:
            dyda[10] = 2 - t / a
        for mss in range(2, 11):
            dyda[mss] = dyda[mss] / ra
        for mss in range(1, 11):
            y[ndef] += dyda[mss] * _B[mss - 1]
    de = y[2] - y[1]
    e = y[2]  # binding energy for deformed nuclides
    if de <= 0.0 or nz <= 50:
        e = y[1]  # spherical nuclides
    return e


def dz10_mass_excess_kev(Z, N) -> np.ndarray:
    """Vectorised DZ10 atomic mass excess (keV). NaN where the formula is undefined (A < 2)."""
    Z = np.atleast_1d(np.asarray(Z, dtype=np.int64))
    N = np.atleast_1d(np.asarray(N, dtype=np.int64))
    out = np.full(Z.shape, np.nan)
    for k, (z, n) in enumerate(zip(Z.tolist(), N.tolist(), strict=True)):
        if z + n < 2 or z < 0 or n < 0:
            continue
        b = dz10_binding_mev(n, z) * 1000.0
        out[k] = z * ME_H_KEV + n * ME_N_KEV - b
    return out


def dz10_table(zmax: int = 130, nmax: int = 220) -> pd.DataFrame:
    """DZ10 on a rectangular (Z, N) grid, Z,N >= 8, as a table like the others."""
    Z, N = np.meshgrid(np.arange(8, zmax + 1), np.arange(8, nmax + 1), indexing="ij")
    Z = Z.ravel()
    N = N.ravel()
    return pd.DataFrame({"Z": Z, "N": N, "A": Z + N, "mass_excess_kev": dz10_mass_excess_kev(Z, N)})


def load_dz28_table(dz_dir: Path = DZ_DIR) -> pd.DataFrame:
    """``DZ28_RBF.txt`` -> Z, N, A, mass_excess_kev (DZ28), mass_excess_rbf_kev (DZ28+RBF)."""
    rows = []
    with (dz_dir / "DZ28_RBF.txt").open(encoding="latin-1") as fh:
        for line in fh:
            parts = line.replace(",", " ").split()
            if len(parts) != 4 or not parts[0].isdigit():
                continue
            rows.append([float(x) for x in parts])
    arr = np.array(rows, dtype=np.float64)
    df = pd.DataFrame(arr, columns=["A", "Z", "B_dz28", "B_dz28_rbf"])
    df["Z"] = df["Z"].astype(np.int64)
    df["A"] = df["A"].astype(np.int64)
    df["N"] = df["A"] - df["Z"]
    base = df["Z"] * ME_H_KEV + df["N"] * ME_N_KEV
    df["mass_excess_kev"] = base - df["B_dz28"] * 1000.0
    df["mass_excess_rbf_kev"] = base - df["B_dz28_rbf"] * 1000.0
    return df[["Z", "N", "A", "mass_excess_kev", "mass_excess_rbf_kev"]]
