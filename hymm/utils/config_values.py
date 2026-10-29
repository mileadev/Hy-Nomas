"""Safely parse checkpoint selection ratios from Hydra configuration."""

from __future__ import annotations

from fractions import Fraction
import math


def checkpoint_ratio(value: object) -> float:
    """Accept decimals or fractions, rejecting arbitrary Python expressions."""
    if isinstance(value, bool):
        raise ValueError("Checkpoint ratio cannot be Boolean")
    try:
        result = float(Fraction(str(value).strip()))
    except (ValueError, ZeroDivisionError, TypeError, OverflowError) as exc:
        raise ValueError("Checkpoint ratio must be numeric or a simple fraction") from exc
    if not math.isfinite(result) or not 0 <= result <= 1:
        raise ValueError("Checkpoint ratio must be between 0 and 1")
    return result
