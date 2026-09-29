"""The threshold-relative grid (models/threshold_grid.py): exact round trip, and inert when off."""
import numpy as np
import pytest
import torch

from models.residual.fno import SpectralResidual
from models.threshold_grid import (
    LENGTH,
    ThresholdGridResidual,
    forward_index,
    from_window,
    inverse_index,
    offsets,
    residual_class,
    threshold_index,
    to_window,
)
from models.train_stage_c import StageCBundle, train_stage_c

E = 64
GRID = np.logspace(3, np.log10(2e7), E)      # the Stage C grid: 64 log points, 1 keV - 20 MeV


def _channel(thr_ev: np.ndarray) -> torch.Tensor:
    """What StageCBundle builds: log10(E / E_thr) clipped to [-2, 1]."""
    g = torch.tensor(GRID, dtype=torch.float32)
    t = torch.tensor(thr_ev, dtype=torch.float32)
    return torch.log10(g[None, :] / t[:, None]).clamp(-2.0, 1.0)


THR = np.array([5.32e6, 6.18e6, 8.11e6, 8.93e6, 11.40e6, 13.63e6])   # the bundle's range


def test_threshold_index_recovers_the_kink() -> None:
    k = threshold_index(_channel(THR))
    want = np.log10(THR / GRID[0]) / np.log10(GRID[1] / GRID[0])
    assert np.allclose(k.numpy(), want, atol=2e-3)


@pytest.mark.parametrize("layout", ["align", "pad"])
def test_round_trip_is_exact_on_the_scoring_grid(layout: str) -> None:
    chan = _channel(THR)
    off = offsets(chan, E, layout)
    fwd, inv = forward_index(off, E), inverse_index(off, E)
    x = torch.randn(len(THR), E, dtype=torch.float64)
    assert torch.equal(from_window(to_window(x, fwd), inv), x)
    x3 = torch.randn(len(THR), E, 3)
    back = torch.stack([from_window(to_window(x3, fwd)[..., c], inv) for c in range(3)], -1)
    assert torch.equal(back, x3)
    assert to_window(x, fwd).shape == (len(THR), LENGTH)


def test_align_puts_every_threshold_on_one_slot_and_pad_does_not() -> None:
    chan = _channel(THR)
    k = threshold_index(chan)
    slot_align = k + offsets(chan, E, "align")
    slot_pad = k + offsets(chan, E, "pad")
    assert float(slot_align.max() - slot_align.min()) <= 1.0     # within one bin (rounding)
    assert float(slot_pad.max() - slot_pad.min()) > 5.0          # the spread is untouched


def test_padding_replicates_the_edges() -> None:
    chan = _channel(THR)
    off = offsets(chan, E, "align")
    x = torch.arange(E, dtype=torch.float32).repeat(len(THR), 1)
    w = to_window(x, forward_index(off, E))
    for i, o in enumerate(off.tolist()):
        assert torch.all(w[i, :o] == 0) and torch.all(w[i, o + E:] == E - 1)


def test_a_flat_channel_is_refused() -> None:
    with pytest.raises(ValueError, match="unclipped"):
        offsets(torch.zeros(3, E), E, "align")


def test_circular_alignment_would_be_a_no_op() -> None:
    """Why the window is padded: one FNO layer commutes with a circular roll of the grid."""
    torch.manual_seed(0)
    m = SpectralResidual(n_energy=E, embed_dim=8, n_modes=4, width=32).double()
    sb = torch.rand(1, E, dtype=torch.float64) + 0.1
    emb = torch.randn(1, 8, dtype=torch.float64)
    thr = torch.randn(1, E, dtype=torch.float64)
    r, s = m(sb, emb, thr)
    r2, s2 = m(sb.roll(7, 1), emb, thr.roll(7, 1))
    assert torch.allclose(r2, r.roll(7, 1), atol=1e-12)
    assert torch.allclose(s2, s.roll(7, 1), atol=1e-12)


def test_grid_model_outputs_physical_shapes_and_differs_from_plain() -> None:
    torch.manual_seed(1)
    plain = SpectralResidual(n_energy=E, embed_dim=8, n_modes=4, width=32)
    torch.manual_seed(1)
    grid = ThresholdGridResidual(n_energy=E, embed_dim=8, n_modes=4, width=32, layout="align")
    # same parameters, same RNG consumption: the window length enters no weight
    for (ka, va), (kb, vb) in zip(plain.state_dict().items(), grid.state_dict().items(),
                                  strict=True):
        assert ka == kb and torch.equal(va, vb)
    sb = torch.rand(len(THR), E) + 0.1
    emb = torch.randn(len(THR), 8)
    r, s = grid(sb, emb, _channel(THR))
    assert r.shape == (len(THR), E) and s.shape == (len(THR), E)
    assert bool((r > 0).all()) and bool((s > 0).all())
    assert not torch.allclose(r, plain(sb, emb, _channel(THR))[0])


def _bundle() -> StageCBundle:
    g = torch.Generator().manual_seed(3)
    n = len(THR)
    sb = torch.rand(n, E, generator=g) * 0.5 + 0.1
    trust = (torch.rand(n, E, generator=g) > 0.6).float()
    is_test = torch.zeros(n, E)
    is_test[:, -6:] = 1.0
    return StageCBundle(nuclides=[f"n{i}" for i in range(n)], grid_ev=GRID, stage_b_b=sb,
                        target_log=torch.log10(sb) + 0.1 * trust, trust=trust,
                        teacher_log=torch.log10(sb), embeddings=torch.randn(n, 8, generator=g),
                        is_test=is_test, threshold_ev=torch.tensor(THR, dtype=torch.float32))


def test_switch_off_is_the_unmodified_trainer(monkeypatch) -> None:
    monkeypatch.delenv("INCOGNITA_THRESHOLD_GRID", raising=False)
    assert residual_class() is SpectralResidual
    a, _ = train_stage_c(_bundle(), epochs=12, urr_first_epochs=4, width=16, n_modes=4)
    monkeypatch.setenv("INCOGNITA_THRESHOLD_GRID", "off")
    assert residual_class() is SpectralResidual
    b, _ = train_stage_c(_bundle(), epochs=12, urr_first_epochs=4, width=16, n_modes=4)
    assert type(a) is SpectralResidual
    for va, vb in zip(a.state_dict().values(), b.state_dict().values(), strict=True):
        assert torch.equal(va, vb)
    monkeypatch.setenv("INCOGNITA_THRESHOLD_GRID", "align")
    c, _ = train_stage_c(_bundle(), epochs=12, urr_first_epochs=4, width=16, n_modes=4)
    assert isinstance(c, ThresholdGridResidual)
    monkeypatch.setenv("INCOGNITA_THRESHOLD_GRID", "sideways")
    with pytest.raises(ValueError):
        residual_class()
