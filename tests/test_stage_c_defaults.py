"""REDTEAM M7: retraining from the repository must not pull evaluated-library values in by default."""
import inspect

from models.stage_c_data import build_bundle
from models.train_stage_c import train_stage_c


def test_no_teacher_library_by_default():
    assert inspect.signature(build_bundle).parameters["teacher_key"].default == ""
    assert inspect.signature(train_stage_c).parameters["teacher_weight"].default == 0.0


def test_resonance_bound_policy_default_is_library_free():
    src = inspect.getsource(build_bundle)
    assert '_env("RRR_POLICY", "indep")' in src
