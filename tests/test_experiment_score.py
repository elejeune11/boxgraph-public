"""Scoring the digitizer comparison: errors as a fraction of the axis, honest intervals, consistency."""

import math

import pytest

from experiments.digitizer_ab.score import consistency, normalized, score_run

LIN = {"at": [1, 2, 3], "y": [10.0, 20.0, 30.0], "scale": "linear", "span": [0, 100]}
LOG = {"at": [1, 2], "y": [10.0, 100.0], "scale": "log10", "span": [1, 1000]}


def ans(*rows):
    return {"readings": [{"x": x, "y": y, "lo": lo, "hi": hi} for x, y, lo, hi in rows]}


def test_errors_are_a_fraction_of_the_axis():
    """An error is measured as a fraction of the axis span, in decades on a log axis."""
    assert normalized(12, 10, LIN) == pytest.approx(0.02)
    assert normalized(100, 10, LOG) == pytest.approx(1 / 3)


def test_a_perfect_reading_scores_zero_error_and_full_coverage():
    """Exact values with intervals containing the truth score zero error and full coverage."""
    s = score_run(ans((1, 10, 9, 11), (2, 20, 19, 21), (3, 30, 29, 31)), LIN)
    assert s["mean_err"] == 0 and s["coverage"] == 1 and s["missing"] == 0
    assert s["mean_width"] == pytest.approx(0.02)


def test_an_interval_that_misses_the_truth_lowers_coverage():
    """A confident interval that misses the truth counts against coverage, however close the value."""
    s = score_run(ans((1, 10.5, 10.4, 10.6), (2, 20, 19, 21), (3, 30, 29, 31)), LIN)
    assert s["coverage"] == pytest.approx(2 / 3)


def test_missing_and_unmatched_readings_count_as_missing():
    """A position not answered, or answered without a value, counts as missing."""
    s = score_run(ans((1, 10, 9, 11), (3, None, None, None)), LIN)
    assert s["missing"] == 2 and s["coverage"] == pytest.approx(1 / 3)


def test_readings_are_matched_to_the_nearest_requested_x():
    """Readings are matched by x, so their order does not matter."""
    s = score_run(ans((3, 30, 29, 31), (1, 10, 9, 11), (2, 20, 19, 21)), LIN)
    assert s["mean_err"] == 0


def test_consistency_between_two_runs():
    """Two runs of one method are compared value by value as a fraction of the axis."""
    a = ans((1, 10, 9, 11), (2, 20, 19, 21), (3, 30, 29, 31))
    b = ans((1, 12, 11, 13), (2, 20, 19, 21), (3, 30, 29, 31))
    assert consistency(a, b, LIN) == pytest.approx(0.02 / 3)
    assert math.isnan(consistency(ans(), b, LIN))
