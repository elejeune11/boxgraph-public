"""Units and quantities (principle 6). Built on pint; nothing field-specific."""

from __future__ import annotations

import math
from functools import lru_cache

import pint

ureg = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)
ureg.define("molar = mole / liter = M")
ureg.define("dalton_ = 1.66053906660e-27 kilogram")  # 'Da' already exists; keep explicit alias
ureg.define("bond = [] ")  # counts: 'per bond' is dimensionless bookkeeping
ureg.define("cell_ = []")
ureg.define("receptor = []")
ureg.define("molecule = []")
Q_ = ureg.Quantity


class UnitError(ValueError):
    pass


_ALIASES = {
    "": "dimensionless",
    "1": "dimensionless",
    "-": "dimensionless",
    "none": "dimensionless",
    "µm": "micrometer",
    "μm": "micrometer",
    "um": "micrometer",
    "sec": "second",
    "dyne": "dyne",
    "dynes": "dyne",
}


def _clean(unit: str) -> str:
    u = (unit or "").strip()
    if u in _ALIASES:
        return _ALIASES[u]
    u = u.replace("µ", "u").replace("μ", "u").replace("·", "*").replace("−", "-")
    u = u.replace("^", "**")
    return u


@lru_cache(maxsize=4096)
def parse_unit(unit: str) -> pint.Unit:
    try:
        return ureg.Unit(_clean(unit)) if _clean(unit) != "dimensionless" else ureg.dimensionless
    except Exception:
        try:
            q = ureg.parse_expression(_clean(unit))
            return q.units if hasattr(q, "units") else ureg.dimensionless
        except Exception as e:  # noqa: BLE001
            raise UnitError(f"cannot read unit {unit!r}: {e}") from None


@lru_cache(maxsize=4096)
def parse_dimension(dim: str):
    d = (dim or "").strip()
    if d in ("", "1", "dimensionless", "[]"):
        return ureg.dimensionless.dimensionality
    try:
        return ureg.get_dimensionality(d)
    except Exception as e:  # noqa: BLE001
        raise UnitError(f"cannot read dimension {dim!r}: {e}") from None


def unit_matches_dimension(unit: str, dim: str) -> bool:
    return parse_unit(unit).dimensionality == parse_dimension(dim)


def dimension_of(unit: str) -> str:
    return str(parse_unit(unit).dimensionality)


def _to_linear(value: float, scale: str) -> float:
    if scale == "linear":
        return value
    if scale == "log10":
        return 10.0**value
    if scale == "ln":
        return math.exp(value)
    raise UnitError(f"unknown scale {scale}")


def _from_linear(value: float, scale: str) -> float:
    if scale == "linear":
        return value
    if value <= 0:
        return float("nan")
    if scale == "log10":
        return math.log10(value)
    if scale == "ln":
        return math.log(value)
    raise UnitError(f"unknown scale {scale}")


def convert(value: float, from_unit: str, to_unit: str, from_scale: str = "linear", to_scale: str = "linear") -> float:
    """Convert a number between units and scales. A log-scale value v in unit u
    means log10(x / u)."""
    lin = _to_linear(value, from_scale)
    fu, tu = parse_unit(from_unit), parse_unit(to_unit)
    if fu.dimensionality != tu.dimensionality:
        raise UnitError(f"cannot convert {from_unit!r} ({fu.dimensionality}) to {to_unit!r} ({tu.dimensionality})")
    lin = Q_(lin, fu).to(tu).magnitude
    return _from_linear(float(lin), to_scale)


def same_dimension(u1: str, u2: str) -> bool:
    return parse_unit(u1).dimensionality == parse_unit(u2).dimensionality
