"""Reject executable checkpoint ratios while preserving fraction syntax."""

import pytest
import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[2] / "hymm" / "utils" / "config_values.py"
SPEC = importlib.util.spec_from_file_location("checkpoint_config_values", MODULE)
assert SPEC is not None and SPEC.loader is not None
cfg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cfg)
checkpoint_ratio = cfg.checkpoint_ratio


@pytest.mark.parametrize("input,expected", [
    ("1/3", 1/3), ("0.5", 0.5), (1, 1.0), (0, 0.0), ("1e-3", 0.001),
])
def test_supported_checkpoint_ratios(input, expected):
    assert checkpoint_ratio(input) == pytest.approx(expected)


@pytest.mark.parametrize("value", [
    "__import__('os').system('echo x')", "1+1", "1/0", "nan",
    "inf", "-0.2", 1.01, True, None,
])
def test_rejects_unsafe_ratio_expressions(value):
    with pytest.raises(ValueError):
        checkpoint_ratio(value)
