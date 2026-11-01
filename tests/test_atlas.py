"""ModelAtlas (03-modelatlas.md): relations are tested, not believed;
families are what verified same-as relations join."""

import pytest

from boxgraph.atlas import families
from boxgraph.atlas import test_relation as check
from boxgraph.store import load_record


@pytest.fixture(scope="module")
def atlas(request):
    from pathlib import Path

    fx = Path(__file__).parent / "fixtures"
    recs = {r.id: r for r in (load_record(fx / "toy"), load_record(fx / "toy2"))}
    rels = {rel.id: rel for rel in recs["toy2"].record.relations}
    results = {rid: check(rel, recs) for rid, rel in rels.items()}
    return recs, rels, results


def test_same_as_under_a_mapping_is_verified(atlas):
    """The same law in other variables and units verifies as same-as under its mapping."""
    r = atlas[2]["rel_same"]
    assert r.status == "verified", r.detail
    assert r.method in ("symbolic", "numeric")


def test_stated_same_as_that_is_false_is_refuted(atlas):
    """A stated same-as that is false is refuted by the numeric test."""
    r = atlas[2]["rel_wrong"]
    assert r.status == "refuted", r.detail
    assert r.method == "numeric"  # one side has no symbolic form


def test_constant_factor_is_not_verified_with_what_holds_instead(atlas):
    """A relation off by a constant factor is not verified, and says what holds instead."""
    r = atlas[2]["rel_factor"]
    assert r.status == "not_verified"
    assert "factor" in r.holds_instead


def test_reduces_to_in_a_limit(atlas):
    """A model that becomes another in a stated limit verifies as reduces-to."""
    assert atlas[2]["rel_limit"].status == "verified"


def test_derived_from_with_applicable_steps(atlas):
    """A derivation whose steps can be applied verifies."""
    assert atlas[2]["rel_derived"].status == "verified"


def test_derived_from_in_words_is_unverifiable(atlas):
    """A derivation given only in words is unverifiable, not believed."""
    r = atlas[2]["rel_derived_words"]
    assert r.status == "unverifiable"
    assert "cannot be applied" in r.detail


def test_approximation_is_measured(atlas):
    """An approximation's error over its regime is measured."""
    r = atlas[2]["rel_approx"]
    assert r.status == "verified"
    assert 0 < r.error < 0.01


def test_scales_as(atlas):
    """Two models with the same scaling in their shared variables verify as scales-as."""
    assert atlas[2]["rel_scales"].status == "verified"


def test_too_plain_is_flagged(atlas):
    """A form too plain to mean anything, such as a bare ratio, is flagged."""
    r = atlas[2]["rel_plain"]
    assert r.status == "verified"
    assert r.too_plain


def test_families_join_only_verified_same_as_and_not_plain(atlas):
    """Only verified, non-trivial same-as relations join a family."""
    recs, rels, results = atlas
    fams = families(rels.values(), results)
    assert {"toy/decay", "toy2/lifetime"} in [set(f) for f in fams]
    flat = {m for f in fams for m in f}
    assert "toy2/wrongsign" not in flat  # refuted
    assert "toy2/zeroforce" not in flat  # reduces to / derived from: structure, not family
    assert "toy2/linear" not in flat  # approximation never joins
    assert "toy2/ratio_a" not in flat  # too plain


def test_families_do_not_depend_on_order(atlas):
    """Families are the same whatever order relations are listed in."""
    recs, rels, results = atlas
    a = families(list(rels.values()), results)
    b = families(list(reversed(list(rels.values()))), results)
    assert sorted(map(sorted, a)) == sorted(map(sorted, b))


def test_unknown_model_is_unverifiable(atlas):
    """A relation to a model not in the record is unverifiable."""
    recs, rels, _ = atlas
    rel = rels["rel_same"].model_copy(update={"b": "toy2/ghost"})
    assert check(rel, recs).status == "unverifiable"


def test_scales_as_is_never_verified_without_a_comparison(atlas):
    """Scales-as compares slopes even where a regime starts at zero, and with no shared variable it is unverifiable, not verified."""
    assert atlas[2]["rel_scales_from_zero"].status == "not_verified", atlas[2]["rel_scales_from_zero"].detail
    assert atlas[2]["rel_scales_nothing_shared"].status == "unverifiable"


def test_a_symbolic_form_that_disagrees_with_the_code_is_not_trusted(atlas):
    """A same-as relation is never verified from symbolic forms that disagree with what the models' code computes."""
    r = atlas[2]["rel_liar"]
    assert r.status != "verified", r.detail
    assert "symbolic" in r.detail


def test_a_symbolic_form_with_a_special_function_is_checked_against_the_code(atlas):
    """A symbolic form using a special function (Lambert W) is evaluated and compared with the code, not rejected."""
    r = atlas[2]["rel_lambert"]
    assert r.status == "verified", r.detail
