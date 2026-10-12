"""PEUNITS: last discrete level gets xspreeq(nendisc) * frac (mb), synthetic one-case batch (shared with test_pecollapse)."""
from types import SimpleNamespace

import numpy as np
import torch

from physics.hf.preeq import exciton as X
from tests.hf.test_pecollapse import _case


def _run(on):
    spectra, inp, disc = _case()
    pre = {k: v.clone() for k, v in spectra.items()}
    res = dict(spectra)
    res.update(X.preeq_correct(res, inp, disc, None))
    res.update(X.peunits(res, pre, inp, disc, on))
    return pre, inp, disc, res


def test_peunits_off_is_talys():
    assert not X.peunits_on(SimpleNamespace(peunits=False))
    assert X.peunits_on(SimpleNamespace(peunits=True))
    pre, inp, disc, res = _run(False)
    off = X.preeq_correct(dict(_case()[0]), inp, disc, None)
    assert torch.equal(res["xspreeqdisc"], off["xspreeqdisc"])


def test_peunits_nl_gets_removed_flux_only():
    pre, inp, disc, on = _run(True)
    off = _run(False)[3]
    nd, NL = disc.nendisc[0][0], disc.nlast[0]
    de = float(inp.deltae_mev[0, nd])
    frac = float(disc.etop_mev[0, nd]) - float(disc.eoutdis_mev[0][0][NL])
    for t in range(7):
        if t == inp.k0:
            assert torch.equal(on["xspreeqdisc"][0, t], off["xspreeqdisc"][0, t])
            continue
        removed = float(pre["xspreeq"][0, t, nd] - on["xspreeq"][0, t, nd]) * de  # the (1 - Rboundary) scaling
        assert abs(float(on["xspreeqdisc"][0, t, NL]) - removed) <= 1e-12 * max(removed, 1e-300)
        assert abs(float(on["xspreeqdisc"][0, t, NL]) - float(off["xspreeqdisc"][0, t, NL]) * de) <= 1e-12 * removed
        assert torch.equal(on["xspreeqdisc"][0, t, :NL], off["xspreeqdisc"][0, t, :NL])
        assert abs(frac / de) <= 1.0
    for k in ("xspreeq", "xsstep", "xspreeqps"):
        assert torch.equal(on[k], off[k])
