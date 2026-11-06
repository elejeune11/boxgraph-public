"""Printed values and verdicts at printed precision (02-boxgraph.md, Verdicts).

A printed string is parsed into a central value and an interval allowed by
how it was printed:

- decimals or significant figures, incl. scientific notation: last printed digit;
- 'v ± u': the uncertainty replaces the printed digits;
- 'a–b' or 'a to b': the range;
- '~v', '≈v', 'about v', 'of order', '<v', '>v', a bare power of ten: no precision.

A verdict is computed, never stored: reproduced inside the interval, close
when outside it by no more than its own width again, otherwise not reproduced.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum

SUPERSCRIPT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")
MINUS = str.maketrans({"−": "-", "–": "-", "—": "-", "‒": "-"})

NO_PRECISION_MARKERS = ("~", "≈", "≃", "∼", "about", "approx", "of order", "order of", "<", ">", "≤", "≥", "≲", "≳", "roughly", "some")


class Verdict(str, Enum):
    reproduced = "reproduced"
    close = "close"
    not_reproduced = "not reproduced"
    no_verdict = "no verdict"


@dataclass(frozen=True)
class Printed:
    text: str
    value: float
    lo: float | None  # interval allowed by the printing; None = no precision
    hi: float | None
    how: str  # 'digits', 'uncertainty', 'range', 'none'

    @property
    def has_precision(self) -> bool:
        return self.lo is not None


class PrintedError(ValueError):
    pass


_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)"
_TIMES = r"\s*(?:x|×|\*|·)\s*"
_POW = r"10\s*(?:\^|\*\*)\s*\(?\s*([-+]?\d+)\s*\)?"
_POW_NC = r"10\s*(?:\^|\*\*)\s*\(?\s*[-+]?\d+\s*\)?"
_SCI = re.compile(rf"^({_NUM}){_TIMES}{_POW}$", re.I)
_E = re.compile(r"^([-+]?(?:\d+\.?\d*|\.\d+))[eE]([-+]?\d+)$")
_BARE_POW = re.compile(rf"^{_POW}$")
_PLAIN = re.compile(rf"^{_NUM}$")


def _normalise(s: str) -> str:
    s = re.sub(r"10([⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)", lambda m: "10^" + m.group(1).translate(SUPERSCRIPT), s.strip())
    s = s.translate(SUPERSCRIPT).translate(MINUS)
    s = s.replace(" ", " ").replace(" ", " ")
    s = re.sub(r"\s+", " ", s)
    return s


def _digits(mantissa: str) -> float:
    """Half a unit in the last printed digit of a plain number string."""
    m = mantissa.lstrip("+-")
    if "." in m:
        decimals = len(m.split(".")[1])
        return 0.5 * 10 ** (-decimals)
    return 0.5


def _parse_number(s: str) -> tuple[float, float | None]:
    """A single printed number -> (value, half-width or None)."""
    s = s.strip()
    m = _SCI.match(s)
    if m:
        mant, exp = m.group(1), int(m.group(2))
        return float(mant) * 10**exp, _digits(mant) * 10**exp
    m = _E.match(s)
    if m:
        mant, exp = m.group(1), int(m.group(2))
        return float(mant) * 10**exp, _digits(mant) * 10**exp
    m = _BARE_POW.match(s)
    if m:  # '10^-5' is an order of magnitude, not a digit
        return 10.0 ** int(m.group(1)), None
    if _PLAIN.match(s):
        return float(s), _digits(s)
    raise PrintedError(f"cannot read a number from {s!r}")


def parse(text: str) -> Printed:
    """Parse a printed value. Units must not be included."""
    if text is None:
        raise PrintedError("no printed value")
    raw = str(text)
    s = _normalise(raw)
    low = s.lower()
    approx = re.compile("|".join(re.escape(m) for m in ("~", "≈", "≃", "∼", "about", "approx.", "approximately", "roughly")))
    bare = approx.sub("", s).strip()
    if bare != s.strip():  # an approximate range ('0 to ~30', '~5 to 50'): read, with no precision
        m = re.match(rf"^(?P<a>{_NUM})\s*(?:to|-)\s*(?P<b>{_NUM})$", re.sub(r"\s+", " ", bare))
        if m and not _PLAIN.match(bare):
            a, _ = _parse_number(m.group("a"))
            b, _ = _parse_number(m.group("b"))
            return Printed(raw, (a + b) / 2, None, None, "none")
    for marker in NO_PRECISION_MARKERS:
        if low.startswith(marker):
            rest = s[len(marker):].strip()
            value, _ = _parse_number(rest)
            return Printed(raw, value, None, None, "none")
    # a power of ten printed once after two numbers applies to both:
    # '4.7 ± 0.3 × 10^-5', '(4.7 ± 0.3) × 10^-5', '2–3 × 10^-5', '2 to 3 × 10^-5'
    m = re.match(rf"^\(?\s*(?P<a>{_NUM})\s*(?P<op>±|\+/-|\+-|to|-)\s*(?P<b>{_NUM})\s*\)?{_TIMES}{_POW}$", s)
    if m:
        f = 10.0 ** int(m.group(len(m.groups())))
        a, b = float(m.group("a")) * f, float(m.group("b")) * f
        if m.group("op") in ("±", "+/-", "+-"):
            return Printed(raw, a, a - abs(b), a + abs(b), "uncertainty")
        lo, hi = min(a, b), max(a, b)
        return Printed(raw, (lo + hi) / 2, lo, hi, "range")
    # uncertainty: v ± u, v +/- u
    m = re.match(r"^(.+?)\s*(?:±|\+/-|\+-)\s*(.+)$", s)
    if m:
        v, _ = _parse_number(m.group(1))
        u_text = m.group(2)
        u, _ = _parse_number(u_text)
        u = abs(u)
        return Printed(raw, v, v - u, v + u, "uncertainty")
    # range: 'a to b', or 'a - b' with spaces / en-dash already normalised to '-'
    one = rf"{_NUM}(?:{_TIMES}{_POW_NC}|[eE][-+]?\d+)?"
    m = re.match(rf"^(?P<a>{one})\s*(?:to|-)\s*(?P<b>{one})$", s)
    if m and not _PLAIN.match(s) and not _SCI.match(s) and not _E.match(s):
        a, _ = _parse_number(m.group("a"))
        b, _ = _parse_number(m.group("b"))
        lo, hi = min(a, b), max(a, b)
        return Printed(raw, (lo + hi) / 2, lo, hi, "range")
    value, h = _parse_number(s)
    if h is None:
        return Printed(raw, value, None, None, "none")
    return Printed(raw, value, value - h, value + h, "digits")


SE_MULTIPLE = 2.0  # a computed value with sampling error stands for mean ± 2 standard errors


def verdict(computed: float, printed: Printed, se: float = 0.0, band: tuple[float, float] | None = None) -> Verdict:
    """Verdict for a computed value against a printed one, in the same unit and scale.

    A computed value with sampling error `se` (a model with randomness, run
    several times) is the interval mean ± 2 se. Reproduced when it overlaps the
    printed interval. Close when the gap is at most the printed interval's width
    and, if the printed interval excludes zero, the value has its sign and is
    within a factor of ten of it. Otherwise not reproduced. With se = 0 this is
    Figure 4's rule. `band`, the range the rounding of the inputs allows, widens
    the computed interval the same way."""
    if not printed.has_precision:
        return Verdict.no_verdict
    if computed is None or (isinstance(computed, float) and math.isnan(computed)):
        return Verdict.not_reproduced
    lo, hi = printed.lo, printed.hi
    half = SE_MULTIPLE * abs(se or 0.0)
    clo, chi = computed - half, computed + half
    if band is not None:
        clo, chi = min(clo, band[0]), max(chi, band[1])
    if chi >= lo and clo <= hi:
        return Verdict.reproduced
    if lo > 0 or hi < 0:
        # away from zero, close also needs the printed value's sign and order of magnitude:
        # a value a millionfold off, or of the other sign, is not close however wide the printed digits
        mid = (lo + hi) / 2
        nearest = min(max(mid, clo), chi) if clo <= mid <= chi else (chi if chi < mid else clo)
        if nearest * mid <= 0 or not (abs(mid) / 10 <= abs(nearest) <= abs(mid) * 10):
            return Verdict.not_reproduced
    width = hi - lo
    gap = lo - chi if chi < lo else clo - hi
    if gap <= width * (1 + 1e-12):
        return Verdict.close
    return Verdict.not_reproduced


def combine(verdicts: list[Verdict]) -> Verdict:
    """A table or curve: reproduced if every value is, close if every value is
    at least close, otherwise not reproduced. Values with no verdict are skipped;
    if none has one, no verdict."""
    vs = [v for v in verdicts if v != Verdict.no_verdict]
    if not vs:
        return Verdict.no_verdict
    if all(v == Verdict.reproduced for v in vs):
        return Verdict.reproduced
    if all(v in (Verdict.reproduced, Verdict.close) for v in vs):
        return Verdict.close
    return Verdict.not_reproduced
