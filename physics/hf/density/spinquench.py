"""SPINQUENCH (Incognita extension, 2026-10-05): superfluid quenching of the spin-cutoff moment of inertia at low excitation.

Physics: below the pairing phase transition the nuclear moment of inertia is reduced from the rigid-body value (pairing correlations;
BCS gives I(T = 0) ~ 1/2 rigid in heavy nuclei, rising to rigid at the critical temperature T_c = 0.567 Delta_0). TALYS's analytical
spin cutoff uses the rigid-body (Fermi-gas, a/a~-scaled) moment at every energy above the matching energy, and interpolates linearly
from the discrete-level value at E_d to that Fermi-gas value at the matching energy E_m below it. The switch multiplies the Fermi-gas
value, wherever it is evaluated, by

    q(U) = 1/2 + 1/2 * min(1, U / U_c),   U_c = 0.567^2 * a~ * Delta_0^2,   Delta_0 = 12 / sqrt(A),

with U the Fermi-gas excitation the spin-cutoff formula itself uses (E - delta above E_m; U_m = E_m - P - Pshift for the matching
value s2m that anchors the CT interpolation) and a~ = alimit (the engine's asymptotic level-density parameter). Zero free parameters.

Only the SPIN DISTRIBUTION of the continuum level density changes: rho(E, J) = rho_tot(E) * R(J; sigma_Q^2). rho_tot(E) (the
Fermi-gas 1/sigma factor, the CT/FG matching) keeps the engine's sigma, so the total level density and the CT parameters are
unchanged; D0 moves only through R(J) at S_n, i.e. only where U(S_n) < U_c.
Domain: ground state (ibar 0) of every nucleus whose continuum rho(J) uses the analytical spin cutoff (ldmodel <= 3, or no table);
tabulated (HFB/BSkG3) nuclei keep their microscopic J distribution. The discrete value sigma_d^2 (E <= E_d) and the floor at
sigma_d^2 are TALYS's.

Modes (env INCOGNITA_SPINQUENCH): n (default, OFF: never enters this module's arithmetic), q (arm Q), qd (arm QD: the quenched value
only for E <= E_cut + 2 MeV (E_cut = energy of the last discrete level, the continuum start), the cascade-entry window; the engine's value above).
Sites: density.models.density (rho(E, J), Python), native ld.h rho_row (C rhogrid: ld.c CENGLD / nx2_ld.c NATIVEX2; scalars from
ld_nx2._par), emission.binary.bin_spin_cutoff (the pre-equilibrium spin spread of the binary grids: Python, nx2_emit.c, GPU).
"""

from __future__ import annotations

import math
import os

import numpy as np

ENV = "INCOGNITA_SPINQUENCH"
TC_OVER_DELTA = 0.567      # BCS: T_c = 0.567 Delta_0
QD_WINDOW_MEV = 2.0        # arm QD: E_cut + 2 MeV
#: (Z, A, Zinit, Ninit) -> E_cut = the energy of the last discrete level of the decay scheme (levels.nlev), recorded by
#: compound.dens_reference._ld_match before the record is matched (qd only)
ECUT: dict = {}


def note_ecut(Z: int, A: int, o, lv) -> None:
    if mode() != "qd":
        return
    try:
        ECUT[(int(Z), int(A), int(o.Zinit), int(o.Ninit))] = float(lv.e_mev[int(lv.nlev)])
    except Exception:
        pass


def mode() -> str:
    v = os.environ.get(ENV, "n").strip().lower()
    return v if v in ("q", "qd") else "n"


def _f(x) -> float:
    return float(x.detach().reshape(-1)[0]) if hasattr(x, "detach") else float(x)


def u_crit(ld) -> float:
    """U_c = (0.567 Delta_0)^2 a~, Delta_0 = 12/sqrt(A) (MeV)."""
    d0 = 12.0 / math.sqrt(float(ld.A))
    return (TC_OVER_DELTA * d0) ** 2 * _f(ld.alimit)


def qfac(U, uc: float):
    """q(U) = 1/2 + 1/2 min(1, max(U, 0)/U_c) (numpy or float)."""
    return 0.5 + 0.5 * np.minimum(1.0, np.maximum(U, 0.0) / uc)


def scalars(ld, ibar: int = 0):
    """(uc, qm, s2m, Ed, Em, sdisc, delta, xmax) or None when the switch is off / out of domain. Memoised per record."""
    m = mode()
    if m == "n" or ibar != 0:
        return None
    from physics.hf.density.parameters import _ld_memo, _sc_floats

    memo = _ld_memo(ld)
    key = ("spinquench", m)
    if key in memo:
        return memo[key]
    out = None
    if int(ld.ldmodel) <= 3 or not ld.has_table(0):
        scutconst, Em, Ed, sdisc, s2m, colld, delta = _sc_floats(ld, 0, 0, 4.0)
        uc = u_crit(ld)
        Um = Em - _f(ld.pair_mev) - _f(ld.Pshift_mev[0])
        qm = float(qfac(Um, uc)) if Um > 0.0 else 1.0
        if m == "qd":
            key = (int(ld.Z), int(ld.A), int(ld.Z) + int(ld.Zix), int(ld.A) - int(ld.Z) + int(ld.Nix))
            if key not in ECUT:
                raise RuntimeError(f"SPINQUENCH qd: no E_cut recorded for {key}")
            xmax = ECUT[key] + QD_WINDOW_MEV
        else:
            xmax = 1.0e30
        out = (uc, qm, s2m, Ed, Em, sdisc, delta, xmax)
    memo[key] = out
    return out


def quench_np(ld, eex, sc, ibar: int = 0):
    """sigma_Q^2 for the engine's sigma^2 `sc` at energies `eex` (numpy arrays, same shape); `sc` itself when off."""
    s = scalars(ld, ibar)
    if s is None:
        return sc
    uc, qm, s2m, Ed, Em, sdisc, delta, xmax = s
    eex = np.asarray(eex, dtype=np.float64)
    sc = np.asarray(sc, dtype=np.float64)
    with np.errstate(all="ignore"):
        f = (eex - Ed) / (Em - Ed) if Em != Ed else np.zeros_like(eex)
        ct = sc - f * (1.0 - qm) * s2m
        U = eex - delta
        fg = np.where(U > 0.0, qfac(U, uc) * sc, sc)
    out = np.where(eex <= Ed, sc, np.where(eex <= Em, ct, fg))
    out = np.maximum(out, sdisc)
    out = np.where(eex <= Ed, sc, out)
    return np.where(eex > xmax, sc, out)  # qd: engine value above the window


def quench_t(ld, eex, sc, ibar: int = 0):
    """Tensor wrapper (no gradient through the quench factor; the switch is a forward-model option)."""
    if scalars(ld, ibar) is None:
        return sc
    import torch

    e = eex.detach().cpu().numpy() if hasattr(eex, "detach") else np.asarray(eex)
    s = sc.detach().cpu().numpy() if hasattr(sc, "detach") else np.asarray(sc)
    e, s = np.broadcast_arrays(e, s)
    return torch.as_tensor(quench_np(ld, e, s, ibar), dtype=sc.dtype if hasattr(sc, "dtype") else torch.float64)


def c_params(ld) -> tuple[float, float, float]:
    """(uc, qm, xmax) for the C kernels' P_SQ_* slots; uc = 0 means off."""
    s = scalars(ld, 0)
    if s is None:
        return 0.0, 1.0, 1.0e30
    return s[0], s[1], s[7]


__all__ = ["ENV", "mode", "u_crit", "qfac", "scalars", "quench_np", "quench_t", "c_params"]
