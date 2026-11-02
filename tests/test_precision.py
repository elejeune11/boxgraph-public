"""Verdicts at printed precision (02-boxgraph.md, Figure 4)."""

import math

import pytest

from boxgraph import precision as P
from boxgraph.precision import Verdict as V


@pytest.mark.parametrize(
    "text, value, lo, hi, how",
    [
        ("4.7", 4.7, 4.65, 4.75, "digits"),
        ("-14.7", -14.7, -14.75, -14.65, "digits"),
        ("0.01", 0.01, 0.005, 0.015, "digits"),
        ("200", 200, 199.5, 200.5, "digits"),
        ("1.3 x 10^-10", 1.3e-10, 1.25e-10, 1.35e-10, "digits"),
        ("1.3 × 10⁻¹⁰", 1.3e-10, 1.25e-10, 1.35e-10, "digits"),
        ("5e-6", 5e-6, 4.5e-6, 5.5e-6, "digits"),
        ("4.7 ± 0.3", 4.7, 4.4, 5.0, "uncertainty"),
        ("4–5", 4.5, 4.0, 5.0, "range"),
        ("10 to 100", 55, 10, 100, "range"),
        ("1 x 10^5 to 3 x 10^5", 2e5, 1e5, 3e5, "range"),
    ],
)
def test_parse_with_precision(text, value, lo, hi, how):
    """A printed value is read into a value and the interval its printing allows: last digit, scientific notation, superscripts, uncertainty, range."""
    p = P.parse(text)
    assert p.how == how
    assert math.isclose(p.value, value, rel_tol=1e-9)
    assert math.isclose(p.lo, lo, rel_tol=1e-9, abs_tol=1e-15)
    assert math.isclose(p.hi, hi, rel_tol=1e-9, abs_tol=1e-15)


@pytest.mark.parametrize("text", ["~7", "≈ 0.01", "about 5", "of order 10", "10^-5", "10⁻⁵", "< 3", "> 1e3"])
def test_no_precision_gets_no_verdict(text):
    """Approximate values, bounds and bare powers of ten carry no precision, so they get no verdict."""
    p = P.parse(text)
    assert not p.has_precision
    assert P.verdict(p.value, p) == V.no_verdict


def test_uncertainty_replaces_digits():
    """A printed uncertainty replaces the precision of the printed digits."""
    p = P.parse("4.7 ± 0.3")
    assert P.verdict(4.95, p) == V.reproduced  # outside the digits, inside the uncertainty


@pytest.mark.parametrize(
    "computed, expected",
    [
        (4.70, V.reproduced),
        (4.65, V.reproduced),
        (4.75, V.reproduced),
        (4.76, V.close),  # outside by less than the width (0.1) again
        (4.85, V.close),
        (4.55, V.close),
        (4.86, V.not_reproduced),
        (4.54, V.not_reproduced),
        (-4.7, V.not_reproduced),
    ],
)
def test_figure4_bands(computed, expected):
    """Reproduced inside the interval, close within one width outside it, not reproduced beyond (Figure 4)."""
    assert P.verdict(computed, P.parse("4.7")) == expected


def test_bell_misprint_is_not_reproduced():
    """Bell's printed log t = -14.7 against -4.7 from his equations is not reproduced."""
    # Bell prints log t = -14.7 where his own equations give -4.7: ten decades.
    assert P.verdict(-4.7, P.parse("-14.7")) == V.not_reproduced


def test_unreadable_raises():
    """Text that is not a number is refused, not guessed."""
    with pytest.raises(P.PrintedError):
        P.parse("several")


def test_combine_tables():
    """A table or curve is reproduced only if every value is, close if every value is at least close."""
    R, C, N, X = V.reproduced, V.close, V.not_reproduced, V.no_verdict
    assert P.combine([R, R]) == R
    assert P.combine([R, C]) == C
    assert P.combine([R, N, C]) == N
    assert P.combine([X, R]) == R
    assert P.combine([X, X]) == X


def test_a_computed_interval_is_allowed_for():
    """A value with its own sampling error is reproduced when its interval overlaps the printed one."""
    p = P.parse("4.7")  # 4.65 to 4.75
    assert P.verdict(4.8, p) == V.close
    assert P.verdict(4.8, p, se=0.05) == V.reproduced  # 4.70 to 4.90 overlaps
    assert P.verdict(4.9, p, se=0.1) == V.reproduced  # 4.70 to 5.10 overlaps
    assert P.verdict(4.95, p, se=0.05) == V.close  # 4.85 to 5.05: a gap of 0.10, one printed width
    assert P.verdict(5.0, p, se=0.05) == V.not_reproduced  # 4.90 to 5.10: a gap of 0.15
    assert P.verdict(5.3, p, se=0.1) == V.not_reproduced


def test_without_sampling_error_the_rule_is_unchanged():
    """With no sampling error, the verdict is exactly the printed-precision rule of Figure 4."""
    p = P.parse("4.7")
    for c in (4.70, 4.76, 4.85, 4.86, 4.54):
        assert P.verdict(c, p, se=0.0) == P.verdict(c, p)


def test_a_shared_power_of_ten_applies_to_both_parts():
    """'4.7 ± 0.3 × 10^-5', '(4.7 ± 0.3) × 10^-5' and '2–3 × 10^-5' put the power of ten on both numbers, as printed."""
    for text in ("4.7 ± 0.3 x 10^-5", "(4.7 ± 0.3) × 10⁻⁵", "4.7 +/- 0.3 x 10^-5"):
        p = P.parse(text)
        assert math.isclose(p.value, 4.7e-5) and math.isclose(p.lo, 4.4e-5) and math.isclose(p.hi, 5.0e-5), text
    for text in ("2–3 × 10^-5", "2 to 3 x 10^-5", "2 - 3 × 10⁻⁵"):
        p = P.parse(text)
        assert math.isclose(p.lo, 2e-5) and math.isclose(p.hi, 3e-5), text
    p = P.parse("4.7e-5 ± 0.3e-5")  # each part with its own exponent still works
    assert math.isclose(p.lo, 4.4e-5)


def test_close_means_the_same_sign_and_order_of_magnitude():
    """Close keeps Figure 4's band, and, when the printed range excludes zero, also needs the same sign and a value within a factor of ten: a millionfold difference or a sign flip is not close."""
    one = P.parse("1")  # 0.5 to 1.5; Figure 4's band alone would call anything from -0.5 to 2.5 close
    assert P.verdict(1e-6, one) == V.not_reproduced
    assert P.verdict(-0.2, one) == V.not_reproduced
    assert P.verdict(0.3, one) == V.close and P.verdict(2.0, one) == V.close
    assert P.verdict(3.0, one) == V.not_reproduced
    p = P.parse("4.7")  # 4.65 to 4.75: unchanged, close from 4.55 to 4.85
    assert P.verdict(4.55, p) == V.close and P.verdict(4.54, p) == V.not_reproduced
    assert P.verdict(4.85, p) == V.close and P.verdict(4.86, p) == V.not_reproduced
    neg = P.parse("-2")  # -2.5 to -1.5, mirrored
    assert P.verdict(-1.0, neg) == V.close and P.verdict(-0.4, neg) == V.not_reproduced
    assert P.verdict(1e-9, neg) == V.not_reproduced
    zero = P.parse("0.0")  # a range that includes zero keeps the width rule alone
    assert P.verdict(0.12, zero) == V.close


@pytest.mark.parametrize("text, mid", [("0 to ∼30", 15.0), ("~5 to 50", 27.5), ("∼5 – ∼50", 27.5), ("about 2 to 3", 2.5)])
def test_an_approximate_range_is_read_but_has_no_precision(text, mid):
    """A range with an approximate end ('0 to ~30', '~5 to 50') is recorded as printed, has no precision, and so gets no verdict."""
    p = P.parse(text)
    assert p.how == "none" and p.value == pytest.approx(mid)
    assert P.verdict(mid, p) == P.Verdict.no_verdict
