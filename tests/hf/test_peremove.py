"""PEREMOVE: last discrete bin's [Elast, Etop] piece removed from the continuum once (1); + NL own two-point window (2).
Synthetic one-case batch shared with test_pecollapse."""
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from physics.hf.core.grids import locate_scalar
from physics.hf.preeq import exciton as X
from tests.hf.test_pecollapse import _case


def _run(on, remove):
    spectra, inp, disc = _case()
    pre = {k: v.clone() for k, v in spectra.items()}
    res = dict(spectra)
    res.update(X.preeq_correct(res, inp, disc, None))
    res.update(X.peunits(res, pre, inp, disc, on, remove))
    nofrac = res.pop("_peremove_nofrac", None)
    return pre, inp, disc, X.preeq_total(res, inp, disc, nofrac=nofrac)


def test_peremove_mode_and_refusal():
    assert X.peremove_mode(SimpleNamespace(peremove="n")) == "n"
    assert X.peremove_mode(SimpleNamespace(peremove="2")) == "2"
    with pytest.raises(ValueError):
        X.peremove_mode(SimpleNamespace(peremove="3"))
    spectra, inp, disc = _case()
    with pytest.raises(ValueError):
        X.peunits(dict(spectra, **X.preeq_correct(dict(spectra), inp, disc, None)), spectra, inp, disc, False, "1")


def test_peremove_n_is_peunits():
    a, b = _run(True, "n")[3], _run(True, "n")[3]
    for k in ("xspreeqtot", "xspreeqdisc", "xspreeqsum"):
        assert torch.equal(a[k], b[k])


def test_peremove_books():
    pre, inp, disc, u = _run(True, "n")
    r1 = _run(True, "1")[3]
    r2 = _run(True, "2")[3]
    nd, NL = disc.nendisc[0][0], disc.nlast[0]
    de = float(inp.deltae_mev[0, nd])
    esd = disc.eoutdis_mev[0][0]
    elast = float(esd[NL])
    frac = float(disc.etop_mev[0, nd]) - elast
    eg = inp.egrid_mev[0].numpy()
    for t in range(7):
        if t == inp.k0:  # k0 untouched
            for k in ("xspreeqtot", "xspreeqtotps"):
                assert float(r1[k][0, t]) == float(u[k][0, t]) == float(r2[k][0, t])
            assert torch.equal(r2["xspreeqdisc"][0, t], u["xspreeqdisc"][0, t])
            continue
        xs = float(pre["xspreeq"][0, t, nd])
        # R1: the continuum book gains exactly the second removal xs(1-Rb)*frac, NL = the piece removed once
        gain = float(r1["xspreeqtot"][0, t] - u["xspreeqtot"][0, t])
        assert abs(gain - xs * (1 - frac / de) * frac) <= 1e-12 * xs
        assert abs(float(r1["xspreeqdisc"][0, t, NL]) - xs * frac) <= 1e-12 * xs * frac
        assert torch.equal(r1["xspreeqdisc"][0, t, :NL], u["xspreeqdisc"][0, t, :NL])
        # R2: same continuum as R1, NL = TALYS's own two-point window sample on the un-scaled spectrum
        assert float(r2["xspreeqtot"][0, t]) == float(r1["xspreeqtot"][0, t])
        e2 = 0.5 * (elast + float(esd[NL - 1]))
        n1, n2 = locate_scalar(eg, nd, 30, elast), locate_scalar(eg, nd, 30, e2)
        own = 0.5 * float(pre["xspreeq"][0, t, n1] + pre["xspreeq"][0, t, n2]) * (e2 - elast)
        assert abs(float(r2["xspreeqdisc"][0, t, NL]) - own) <= 1e-12 * own
        assert torch.equal(r2["xspreeqdisc"][0, t, :NL], u["xspreeqdisc"][0, t, :NL])
