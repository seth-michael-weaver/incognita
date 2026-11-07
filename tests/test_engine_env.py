"""incognita.engine.run: the arm and the cc_cache argument of EACH call reach the engine (no state from an earlier call)."""
import os

from incognita import engine


def test_cc_cache_argument_of_a_later_call_is_used(monkeypatch, tmp_path):
    monkeypatch.delenv("INCOGNITA_CC_CACHE", raising=False)
    engine._run_env("nodata", None)
    assert os.environ["INCOGNITA_CC_CACHE"].endswith(os.path.join(".cache", "incognita-cc"))
    engine._run_env("nodata", str(tmp_path))                 # was ignored: setdefault kept the first call's directory
    assert os.environ["INCOGNITA_CC_CACHE"] == str(tmp_path)


def test_user_environment_kept_without_argument(monkeypatch, tmp_path):
    monkeypatch.setenv("INCOGNITA_CC_CACHE", str(tmp_path))
    engine._run_env("nodata", None)
    assert os.environ["INCOGNITA_CC_CACHE"] == str(tmp_path)


def test_arm(monkeypatch):
    monkeypatch.setenv("INCOGNITA_TALYS_FIT", "x")
    engine._run_env("", None)
    assert "INCOGNITA_TALYS_FIT" not in os.environ
    engine._run_env("nodata", None)
    assert os.environ["INCOGNITA_TALYS_FIT"] == "nodata"
