"""Reject executable checkpoint ratios while preserving fraction syntax."""

import pytest

from hymm.utils.config_values import checkpoint_ratio


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
