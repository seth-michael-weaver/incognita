"""JOINTCOMP: partial-wave joint anchoring of keV capture (default OFF; used only by the JOINTCOMP combiner, never by a plain run).

Rule JS (development notes): measured D0 and <Gg> are s-wave resonance quantities. The s-wave entrance part of the capture cross
section is taken from the run whose compound cells are anchored to them (ANCH); the p- and d-wave entrance parts are taken from the
field run (F, the B62P deck). sigma_JS(E) = fs_A(E) * sigma_A(E) + (1 - fs_F(E)) * sigma_F(E).

fs(E) = the s-wave share of capture from the run's own ingredients, Hauser-Feshbach without width fluctuations:
  sigma_l = pi lambdabar^2 sum_{J,pi} g_J n_lJ T_l T_g(J,pi) / (sum_l' n_l'J T_l' + T_g(J,pi)),  l = 0, 1, 2
  T_l = 2 pi sqrt(E[eV]) S_l v_l (TALYS spr.f90 convention: S_l from Tlinc, R = 1.35 A^(1/3) fm; S2 := S0),
  T_g(J, pi) = 2 pi <Gg>_pi / D(J, pi), rho(J, pi) = rho_pi P(J) (Ericson, engine spin cutoff at S_n), parity equipartition,
  1/D0 = sum_{J in s-wave} rho(J, pi_t) fixes rho_pi; <Gg>_pi_t = gamgam_th, <Gg>_-pi_t = gamgam_th_p (the engine's own values).
  n_lJ = number of entrance channel spins s in {|I-1/2|, I+1/2} with |l - s| <= J <= l + s (parity (-1)^l pi_t).
Inelastic competition and WFC are ignored (they act on all l alike to first order at keV); only the share is used.
"""
import json
import numpy as np

HBARC2_FAC = 0.6566e6  # pi lambdabar^2 [b] ~ 0.6566e6/E[eV] * ((A+1)/A)^2 (TERRALD step0b convention, x1e3 -> mb)


def _spin(s2, J):
    return (2 * J + 1) / (2 * s2) * np.exp(-(J + 0.5) ** 2 / (2 * s2))


def partial_capture(q):
    """Per-l capture estimate (mb) on the run's energy grid from an engine npz (dict-like). Returns e_ev, sig[l=0..2, nE]."""
    g = lambda k: float(np.asarray(q["ing_" + k]).item()) if np.ndim(q["ing_" + k]) == 0 else np.asarray(q["ing_" + k], float)
    At, I = g("At"), g("target_spin"); ld = json.loads(str(q["ing_ld_cn_json"]))
    s2 = float(ld.get("spin cutoff parameter(Sn)", g("spincut_sn"))); D0 = g("d0theo_ev"); Gs, Gp = g("gamgam_th_ev"), g("gamgam_th_p_ev")
    if not np.isfinite(Gp) or Gp <= 0: Gp = Gs
    e = np.asarray(q["e_ev"], float); einc = np.asarray(q["ing_e_inc_mev"], float) * 1e6
    S0 = np.interp(e, einc, g("s0_e4")) * 1e-4; S1 = np.interp(e, einc, g("s1_e4")) * 1e-4
    Jc = np.arange(0, 40) + (0.5 if abs((I + 0.5) - round(I + 0.5)) > 1e-6 else 0.0)  # compound J (half-integer iff I integer)
    chs = [abs(I - 0.5), I + 0.5] if I > 0 else [0.5]
    n = np.array([[sum(1 for s in chs if abs(l - s) - 1e-9 <= J <= l + s + 1e-9) for J in Jc] for l in range(3)], float)
    P = _spin(s2, Jc)
    rho_pi = 1.0 / (D0 * float((P * (n[0] > 0)).sum()))  # per parity, per eV
    R = 1.35 * At ** (1 / 3); k = np.sqrt(e) * 2.19698e-4 * At / (At + 1)  # fm^-1 (k = 2.19698e-3 sqrt(E[eV]) /fm *1e-1 for neutron)
    x = (R * k) ** 2
    v = [np.ones_like(e), x / (1 + x), x * x / (9 + 3 * x + x * x)]
    T = [2 * np.pi * np.sqrt(e) * S * vl for S, vl in zip((S0, S1, S0), v)]
    lam2 = HBARC2_FAC / e * ((At + 1) / At) ** 2 * 1e3
    gJ = (2 * Jc + 1) / (2 * (2 * I + 1))
    sig = np.zeros((3, len(e)))
    for par, G in ((0, Gs), (1, Gp)):  # par 0 = target parity (l even), 1 = opposite (l odd)
        Tg = 2 * np.pi * G * rho_pi * P  # per J
        ls = [0, 2] if par == 0 else [1]
        Tn = sum(n[l][:, None] * T[l][None, :] for l in ls)
        for l in ls:
            sig[l] += (gJ[:, None] * n[l][:, None] * T[l][None, :] * Tg[:, None] / (Tn + Tg[:, None])).sum(0) * lam2
    return e, sig


def s_share(q):
    e, s = partial_capture(q)
    tot = s.sum(0)
    return e, np.where(tot > 0, s[0] / np.where(tot > 0, tot, 1), 0.0)


CAPTURE_KEYS = ("capture_mb", "ch_xs000000", "tot_ng")


def combine(qF, qA):
    """Rule JS on two engine npz (field F, anchored A) of the same target and grid. Returns dict of the capture keys + fs arrays."""
    e = np.asarray(qF["e_ev"], float)
    if not np.allclose(e, np.asarray(qA["e_ev"], float)): raise ValueError("grid mismatch")
    _, fF = s_share(qF); _, fA = s_share(qA)
    out = {"fs_F": fF, "fs_A": fA}
    for kk in CAPTURE_KEYS:
        if kk in qF.files and kk in qA.files:
            out[kk] = fA * np.asarray(qA[kk], float) + (1 - fF) * np.asarray(qF[kk], float)
    cF = np.asarray(qF["capture_mb"], float); r = np.where(cF > 0, out["capture_mb"] / np.where(cF > 0, cF, 1), 1.0)
    for kk in qF.files:  # isomer / level splits of capture: field split, JS total
        if kk.startswith("lv_ng."): out[kk] = np.asarray(qF[kk], float) * r
    return out


# ISOROTPASS (development notes, development notes): where the compound's even-even core is a measured rotor (R42 = E(4+_1)/E(2+_1)
# >= 3.0, RIPL-4/ENSDF levels, isorot_r42.csv), rho/f errors near S_n are parity-blind, so the measured D0/<Gg> anchor passes to both
# parities: the composite takes the anchored run (ANCH) whole instead of rule JS. INCOGNITA_ISOROTPASS=0 restores plain JS everywhere.
ISOROT_R42_MIN = 3.0
_R42 = None


def core_r42(Z, A):
    """Measured R42 of the even-even core of compound (Z, A+1) (Z, N rounded down to even); nan if not tabulated."""
    global _R42
    if _R42 is None:
        import csv, os
        with open(os.path.join(os.path.dirname(__file__), "isorot_r42.csv")) as f:
            _R42 = {(int(r["Z"]), int(r["A"])): float(r["R42"]) for r in csv.DictReader(f)}
    nc = A + 1 - Z; zc, ncr = Z - Z % 2, nc - nc % 2
    return _R42.get((zc, zc + ncr), float("nan"))


def isorot_full(Z, A):
    """True -> the JS composite of target (Z, A) uses the anchored run whole (ISOROTPASS); default ON, INCOGNITA_ISOROTPASS=0 -> False."""
    import os
    if os.environ.get("INCOGNITA_ISOROTPASS", "1") == "0": return False
    return bool(core_r42(Z, A) >= ISOROT_R42_MIN)
