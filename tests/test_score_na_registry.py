"""scripts/registry/score_na_registry.py: interpolation, log ratios and band flags on a synthetic registry."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

spec = importlib.util.spec_from_file_location("snr", Path(__file__).resolve().parents[1] / "scripts/registry/score_na_registry.py")
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)


def _preds():
    e = [5.0, 14.0, 20.0]
    return pd.DataFrame(dict(Z=40, A=96, e_mev=e, sigma_na_mb_v1=[1.0, 10.0, 10.0], sigma_nxa_mb_v1=[1.0, 12.0, 12.0],
                             sigma_na_mb_hybrid=[2.0, 20.0, 20.0], sigma_na_mb_default_talys=[0.5, 5.0, 5.0],
                             log10_halfwidth68_v1=0.3, log10_halfwidth95_v1=0.7))


def test_scores_total_and_helium():
    rows = pd.DataFrame([dict(entry="1", subentry="1002", reaction="x", kind="na", Z=40, A=96, e_mev=14.0, data_mb=10.0, year=2027),
                         dict(entry="1", subentry="1003", reaction="x", kind="nxa", Z=40, A=96, e_mev=14.0, data_mb=24.0, year=2027),
                         dict(entry="1", subentry="1004", reaction="x", kind="na_state", Z=40, A=96, e_mev=14.0, data_mb=1.0, year=2027)])
    s = S.score(rows, _preds()).set_index("subentry")
    assert abs(s.loc["1002", "lr_v1"]) < 1e-12 and abs(s.loc["1002", "lr_hybrid"] - np.log10(2)) < 1e-12
    assert abs(s.loc["1003", "lr_v1"] - np.log10(0.5)) < 1e-12 and bool(s.loc["1003", "in68_v1"]) is False
    assert np.isnan(s.loc["1004", "lr_v1"])


def test_log_log_interpolation():
    assert abs(S.model_at(_preds(), 9.5, "sigma_na_mb_v1") - 10 ** (np.log10(1) + (9.5 - 5) / 9 * 1)) < 1e-9
    assert np.isnan(S.model_at(_preds(), 25.0, "sigma_na_mb_v1"))
