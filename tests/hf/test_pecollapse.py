"""PECOLLAPSE: flux-conserving PE->discrete collapse (`pecollapse c|c2`), synthetic one-case batch."""
from types import SimpleNamespace

import numpy as np
import torch

from physics.hf.preeq import exciton as X


def _case(mode_k0=1):
    E = 40
    eg = np.concatenate([[0.0], np.arange(1, E + 1) * 0.5])[:E]
    de = np.full(E, 0.5)
    etop = eg + 0.25
    C, P, S = 1, 4, 3
    rng = np.random.default_rng(1)
    xsstep = torch.zeros(C, 7, P, E, dtype=torch.float64)
    for t in range(7):
        sh = np.where((eg > 1.0) & (eg < 15.0), np.sqrt(np.clip(eg - 1.0, 0, None)) * np.exp(-0.3 * eg), 0.0)
        for p in range(1, P):
            xsstep[0, t, p] = torch.from_numpy(sh * rng.uniform(0.5, 1.5))
    ps = torch.from_numpy(np.where(eg > 9.0, 0.3, 0.0)).expand(C, 7, E).clone()
    z = torch.zeros(C, 7, E, dtype=torch.float64)
    spectra = dict(xsstep=xsstep, xspreeqps=ps, xspreeqki=z.clone(), xspreeqbu=z.clone(),
                   xsstep2=torch.rand(C, S, 7, E, dtype=torch.float64))
    spectra["xspreeq"] = xsstep.sum(2) + ps
    esd = [14.1 - x for x in (0.0, 0.3, 0.8, 1.1, 1.9, 2.4, 3.0, 3.6)]
    nd = int(np.searchsorted(etop, esd[-1]))
    inp = SimpleNamespace(C=C, E=E, k0=mode_k0, egrid_mev=torch.from_numpy(eg)[None], deltae_mev=torch.from_numpy(de)[None],
                          einc_mev=torch.tensor([14.1]), Z=26, A=56, xsflux_mb=torch.tensor([1.0e9], dtype=torch.float64))
    disc = SimpleNamespace(eoutdis_mev=[[np.array(esd + [-1.0])] * 7], nendisc=[[nd] * 7], nlast=(7,) * 7,
                           xsdirdisc_mb=[[np.zeros(9)] * 7], etop_mev=torch.from_numpy(etop)[None], ebegin=(1,) * 7,
                           eend=[[30] * 7])
    return spectra, inp, disc


def _run(mode):
    spectra, inp, disc = _case()
    pre = {k: v.clone() for k, v in spectra.items()}
    res = dict(spectra)
    res.update(X.preeq_correct(res, inp, disc, None))
    if mode != "n":
        res.update(X.pecollapse(res, pre, inp, disc, mode))
    tot = X.preeq_total(res, inp, disc)
    return pre, inp, disc, tot


def test_pecollapse_conserves_and_leaves_k0():
    for mode in ("c", "c2"):
        pre, inp, disc, tot = _run(mode)
        off = _run("n")[3]
        de = inp.deltae_mev[0].numpy()
        for t in range(7):
            full = float((pre["xspreeq"][0, t, 1:31] * torch.from_numpy(de[1:31])).sum())
            got = float(tot["xspreeqtot"][0, t] + tot["xspreeqdisctot"][0, t])
            if t == inp.k0:
                assert torch.equal(tot["xspreeqdisc"][0, t], off["xspreeqdisc"][0, t])
                assert float(tot["xspreeqtot"][0, t]) == float(off["xspreeqtot"][0, t])
            else:
                assert abs(got - full) <= 1e-12 * full
        if mode == "c":  # continuum untouched
            assert torch.equal(tot["xspreeqtot"], off["xspreeqtot"])


def test_pecollapse_off_is_talys():
    spectra, inp, disc = _case()
    assert X.pecollapse_mode(SimpleNamespace(pecollapse="n")) == "n"
    a = X.preeq_correct(dict(spectra), inp, disc, None)
    d = X.pecollapse(dict(spectra, **a), {k: v.clone() for k, v in spectra.items()}, inp, disc, "n")
    assert d == {}


def test_cumlin_exact():
    x = np.array([0.0, 1.0, 3.0]); y = np.array([0.0, 2.0, 0.0])
    q = np.array([0.0, 0.5, 1.0, 2.0, 3.0])
    assert np.allclose(X._cumlin(x, y, q), [0.0, 0.25, 1.0, 2.5, 3.0])
