"""CHANCAP: the exclusive-channel per-ejectile caps (channels.py caps / numchantot, deck keyword `chancap`)."""

import pytest

from physics.hf.emission import channels as CH

INC = [False, True, True, True, True, True, True, True]  # parinclude index 0 is type -1


@pytest.fixture
def env(monkeypatch):
    monkeypatch.delenv("INCOGNITA_CHANCAP", raising=False)
    monkeypatch.delenv("INCOGNITA_CHANCAP_EFF", raising=False)
    return monkeypatch


def test_switch(env):
    assert CH.caps() == CH.CHANCAP_CAPS and CH.numchantot() == 4 * CH.NUMCHANTOT  # keyword default y
    env.setenv("INCOGNITA_CHANCAP_EFF", "0")
    assert CH.caps() == (8, 4, 2, 1, 1, 3) and CH.numchantot() == CH.NUMCHANTOT
    env.setenv("INCOGNITA_CHANCAP", "1")  # the env var wins over the deck keyword
    assert CH.caps() == CH.CHANCAP_CAPS
    env.setenv("INCOGNITA_CHANCAP", "bogus")
    with pytest.raises(ValueError):
        CH.caps()


def test_be10_two_tritons(env):
    """Be-10* -> He-4 (Zix 2, Nix 4): channels.f90's triton limit 3zn/2A = 2; the stock cap numit = 1 keeps t + t out."""
    env.setenv("INCOGNITA_CHANCAP", "0")
    lim = CH._limits(2, 4, INC, 4)
    assert lim[3] == 1 and (0, 0, 0, 2, 0, 0) not in CH._channel_keys(2, 4, lim, 4)
    env.setenv("INCOGNITA_CHANCAP", "1")
    lim = CH._limits(2, 4, INC, 4)
    assert lim[3] == 2 and (0, 0, 0, 2, 0, 0) in CH._channel_keys(2, 4, lim, 4)
    assert CH._limits(2, 4, INC, 4, (8, 4, 2, 1, 1, 3))[3] == 1  # an explicit cap tuple wins


def test_keyword(env):
    """default_options writes the run's resolved keyword for the option-less channel sites."""
    import os

    from physics.hf.input.defaults import default_options

    assert default_options(26, 56, "n").chancap is True and os.environ["INCOGNITA_CHANCAP_EFF"] == "1"
    o = default_options(26, 56, "n", overrides={"chancap": "n"})
    assert o.chancap is False and os.environ["INCOGNITA_CHANCAP_EFF"] == "0" and CH.caps() == (8, 4, 2, 1, 1, 3)
