"""Verdicts that carry the rounding of printed inputs (02-boxgraph.md, Verdicts: rounded inputs)."""

from pathlib import Path

from boxgraph import precision as P
from boxgraph.engine import ROUNDING_MAX_INPUTS, ROUNDING_TRY_WITHIN, Builder, Value, rounding_inputs
from boxgraph.store import load_record

FX = Path(__file__).parent / "fixtures"


def _build():
    return Builder(load_record(FX / "rounded")).build()


def test_a_result_off_only_by_its_inputs_rounding_is_reproduced():
    """A result computed from an input printed rounded (1.3 for 1.26) is reproduced once that rounding is carried into the computed value."""
    c = _build().comparisons["cmp_rounding"]
    assert c.verdict == "reproduced" and abs(c.computed_value - 4.55) < 1e-9
    r = c.input_rounding
    assert r["varied"] == ["a", "b"] and r["band"][0] <= 4.41 <= r["band"][1]


def test_a_miss_rounding_cannot_explain_stays_not_reproduced():
    """A result 7% off is tried with its inputs' rounding, and stays not reproduced when the range does not reach it."""
    c = _build().comparisons["cmp_beyond"]
    assert c.verdict == "not reproduced" and c.input_rounding["band"][0] > 4.205


def test_a_miss_beyond_the_trial_limit_is_judged_as_computed():
    """A result off by more than the limit is judged as computed, and the comparison says rounding was not tried."""
    c = _build().comparisons["cmp_far"]
    assert c.verdict == "not reproduced" and "not tried" in c.input_rounding["note"]
    assert ROUNDING_TRY_WITHIN == 0.10


def test_a_curve_carries_its_inputs_rounding_value_by_value():
    """A curve's values each get the range their inputs' rounding allows; a swept index is exact and is not varied."""
    c = _build().comparisons["cmp_curve"]
    assert c.verdict == "reproduced" and c.input_rounding["varied"] == ["a"]
    assert len(c.input_rounding["band"]) == 2 and all(lo <= p <= hi for (lo, hi), p in zip(c.input_rounding["band"], (1.26, 2.52)))


def test_added_inputs_are_never_varied():
    """An added input has no printed rounding: only printed inputs are varied."""
    assert "c_added" not in _build().comparisons["cmp_rounding"].input_rounding["varied"]


def test_a_reproduced_result_needs_no_rounding_and_runs_nothing_more():
    """A result reproduced as computed is left as it is: no extra runs, no rounding record."""
    b = Builder(load_record(FX / "toy")).build()
    good = b.comparisons["cmp_good"]
    assert good.verdict == "reproduced" and good.input_rounding is None


def test_at_most_the_most_coarsely_printed_inputs_are_varied():
    """At most a fixed number of inputs are varied, the most coarsely printed (largest relative range) first."""
    vals = {f"x{i}": Value(id=f"x{i}", quantity="q", unit="m", scale="linear", origin="reported", kind="printed",
                           value=1.0, printed=P.parse("1" if i == 0 else "1." + "0" * i)) for i in range(12)}
    chosen = rounding_inputs({f"s{i}": f"x{i}" for i in range(12)}, vals)
    assert chosen == [f"x{i}" for i in range(ROUNDING_MAX_INPUTS)] and ROUNDING_MAX_INPUTS == 8


def test_a_range_from_rounding_is_judged_like_an_interval():
    """A computed range overlapping the printed interval is reproduced; one within the printed width of it is close."""
    p = P.parse("4.41")
    assert P.verdict(4.55, p) == P.Verdict.not_reproduced
    assert P.verdict(4.55, p, band=(4.31, 4.79)) == P.Verdict.reproduced
    assert P.verdict(4.55, p, band=(4.42, 4.6)) == P.Verdict.close


def test_the_synthesis_and_report_say_when_the_inputs_rounding_was_used(tmp_path):
    """The Synthesis keeps the range and the inputs varied, and the report's verdict says the inputs' rounding was used."""
    import shutil

    from boxgraph.report import render_markdown, review
    from boxgraph.synthesis import build_synthesis

    shutil.copytree(FX / "rounded", tmp_path / "rounded")
    syn = build_synthesis(tmp_path, cache_dir=tmp_path / "cache")
    v = next(v for v in syn["papers"]["rounded"]["verdicts"] if v["comparison"] == "cmp_rounding")
    assert v["verdict"] == "reproduced" and v["input_rounding"]["varied"] == ["a", "b"]
    md = render_markdown(syn, review(syn))
    assert "reproduced, with the inputs' rounding (a, b)" in md
