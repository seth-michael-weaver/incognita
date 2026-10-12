"""PEWINDOW: levels 1..NL (a) or NL only (l) take the exact integral of the piecewise-linear un-zeroed PE spectrum over their TALYS
windows; implies PEREMOVE 1. Synthetic one-case batch shared with test_pecollapse."""
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from physics.hf.preeq import exciton as X
from tests.hf.test_pecollapse import _case


def _run(remove, window):
    spectra, inp, disc = _case()
    pre = {k: v.clone() for k, v in spectra.items()}
    res = dict(spectra)
    res.update(X.preeq_correct(res, inp, disc, None))
    res.update(X.peunits(res, pre, inp, disc, True, remove, window))
    nofrac = res.pop("_peremove_nofrac", None)
    return pre, inp, disc, X.preeq_total(res, inp, disc, nofrac=nofrac)


def test_pewindow_mode_and_refusal():
    assert X.pewindow_mode(SimpleNamespace(pewindow="n")) == "n"
    assert X.pewindow_mode(SimpleNamespace(pewindow="a")) == "a"
    assert X.pewindow_mode(SimpleNamespace(pewindow="l")) == "l"
    with pytest.raises(ValueError):
        X.pewindow_mode(SimpleNamespace(pewindow="x"))
    spectra, inp, disc = _case()
    res = dict(spectra, **X.preeq_correct(dict(spectra), inp, disc, None))
    with pytest.raises(ValueError):
        X.peunits(res, spectra, inp, disc, False, "1", "a")
    with pytest.raises(ValueError):
        X.peunits(res, spectra, inp, disc, True, "2", "a")


def test_pewindow_exact_integral():
    pre, inp, disc, r1 = _run("1", "n")
    wa = _run("1", "a")[3]
    wl = _run("1", "l")[3]
    NL = disc.nlast[0]
    esd = [float(v) for v in disc.eoutdis_mev[0][0]]
    eg = inp.egrid_mev[0].numpy().astype(float)
    for t in range(7):
        if t == inp.k0:
            assert torch.equal(wa["xspreeqdisc"][0, t], r1["xspreeqdisc"][0, t])
            continue
        # continuum book identical to PEREMOVE 1; level 0 untouched
        assert float(wa["xspreeqtot"][0, t]) == float(r1["xspreeqtot"][0, t]) == float(wl["xspreeqtot"][0, t])
        assert float(wa["xspreeqdisc"][0, t, 0]) == float(r1["xspreeqdisc"][0, t, 0])
        # dense brute-force integral of the linear interpolant over each window
        y = pre["xspreeq"][0, t].numpy().astype(float)
        f = lambda lo, up: np.trapezoid(np.interp(np.linspace(lo, up, 200001), eg, y), np.linspace(lo, up, 200001))
        tot = 0.0
        for i in range(1, NL + 1):
            up = 0.5 * (esd[i] + esd[i - 1])
            lo = esd[NL] if i == NL else 0.5 * (esd[i] + esd[i + 1])
            ref = f(lo, up)
            tot += float(wa["xspreeqdisc"][0, t, i])
            assert abs(float(wa["xspreeqdisc"][0, t, i]) - ref) <= 1e-6 * max(ref, 1e-30)
        assert abs(float(wl["xspreeqdisc"][0, t, NL]) - float(wa["xspreeqdisc"][0, t, NL])) <= 1e-15 * float(wa["xspreeqdisc"][0, t, NL])
        assert torch.equal(wl["xspreeqdisc"][0, t, :NL], r1["xspreeqdisc"][0, t, :NL])
        # windows tile [Elast, (E0+E1)/2]: sum of levels 1..NL = one integral over the union
        un = f(esd[NL], 0.5 * (esd[0] + esd[1]))
        assert abs(tot - un) <= 1e-6 * un
