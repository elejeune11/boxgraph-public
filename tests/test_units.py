"""Units and quantities are both checked (principle 6)."""

import math

import pytest

from boxgraph import units as U


@pytest.mark.parametrize(
    "unit, dim",
    [
        ("pN", "[force]"),
        ("dyne", "[force]"),
        ("cm^2/s", "[length] ** 2 / [time]"),
        ("um^2/s", "[length]**2/[time]"),
        ("µm^2", "[length]**2"),
        ("1/s", "1/[time]"),
        ("M^-1 s^-1", "[length]**3/[substance]/[time]"),
        ("pN/nm", "[force]/[length]"),
        ("eV", "[energy]"),
        ("dimensionless", "dimensionless"),
        ("", "dimensionless"),
        ("sec", "[time]"),
    ],
)
def test_unit_matches_dimension(unit, dim):
    """Units in common notations are checked against the dimension of their quantity."""
    assert U.unit_matches_dimension(unit, dim)


def test_mismatch_detected():
    """A unit of the wrong dimension is caught."""
    assert not U.unit_matches_dimension("pN", "[length]")


def test_convert():
    """Unit conversion between CGS and SI-derived units."""
    assert math.isclose(U.convert(1, "dyne", "pN"), 1e7)
    assert math.isclose(U.convert(1.3e-10, "cm^2/s", "um^2/s"), 1.3e-2)


def test_log_scales():
    """Values printed as logarithms convert correctly between scales and units."""
    assert math.isclose(U.convert(-4.7, "s", "s", "log10", "linear"), 10**-4.7)
    assert math.isclose(U.convert(1e-3, "s", "ms", "linear", "log10"), 0.0)
    assert math.isclose(U.convert(-4.7, "s", "ms", "log10", "log10"), -1.7)


def test_incompatible_conversion_raises():
    """Converting between different dimensions is refused."""
    with pytest.raises(U.UnitError):
        U.convert(1, "pN", "nm")


def test_unknown_unit_raises():
    """An unknown unit is refused."""
    with pytest.raises(U.UnitError):
        U.parse_unit("florbs")
