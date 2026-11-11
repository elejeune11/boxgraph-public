"""Curve inputs and outputs: a model port that takes or gives a whole curve (DECISIONS, Records).

The fixture `curves` holds a measured velocity trace; one model averages it over the beat, in other units
than the record's, and another gives its increments as a curve indexed by the trace's own x values."""

import math
from pathlib import Path

import pytest

from boxgraph.engine import Builder
from boxgraph.schema import Run
from boxgraph.store import load_record
from boxgraph.validate import validate

CURVES = Path(__file__).parent / "fixtures" / "curves"


@pytest.fixture
def curves():
    return load_record(CURVES)


@pytest.fixture
def curves_build(curves, tmp_path):
    return Builder(curves, cache_dir=tmp_path / "cache").build()


def test_a_curve_port_receives_the_whole_curve_in_its_own_units(curves_build):
    """A run passes a curve datum whole to a curve port, x and y converted to the port's units."""
    rr = curves_build.runs["run_mean"]
    assert rr.ok, rr.error
    v = curves_build.values["U_mean_pred"]
    assert v.unit == "cm/s" and math.isclose(v.value, 43.75, rel_tol=1e-9)
    assert rr.inputs["U"] == {"curve_of": "U_trace", "x": [0.0, 100.0, 200.0, 300.0, 400.0],
                              "y": [20.0, 50.0, 60.0, 40.0, 30.0]}


def test_a_value_computed_from_a_curve_is_judged_like_any_other(curves_build):
    """The average of a measured trace is compared with the printed average at its precision."""
    c = curves_build.comparisons["cmp_mean"]
    assert c.ok, c.error
    assert c.verdict == "reproduced"


def test_a_curve_output_is_a_curve_judged_point_by_point(curves_build):
    """A curve port's output is a curve indexed by the x values the model returns, judged value by value."""
    v = curves_build.values["dU_pred"]
    assert v.is_table and v.index_quantity == "time" and v.index == [0.0, 0.1, 0.2, 0.3, 0.4]
    c = curves_build.comparisons["cmp_increments"]
    assert c.ok, c.error
    assert c.verdict == "reproduced" and len(c.per_value) == 5


def _build_with(curves, tmp_path, **run):
    lr = type(curves)(path=curves.path, record=curves.record.model_copy(deep=True), model_code=curves.model_code)
    lr.record.runs.append(Run(**run))
    return lr, Builder(lr, cache_dir=tmp_path / "c").build()


def test_a_single_value_on_a_curve_port_is_refused(curves, tmp_path):
    """A curve port given one number is an error of the run, not a silent broadcast."""
    lr, b = _build_with(curves, tmp_path, id="run_bad", model="trace_mean", inputs={"U": "U_mean"}, outputs={"U_mean": "bad"})
    assert not b.runs["run_bad"].ok and "takes a curve" in b.runs["run_bad"].error
    assert any("takes a curve" in p for p in validate(lr, run=False).errors)


def test_a_curve_on_a_single_value_port_is_refused(curves, tmp_path):
    """A curve given to a port that takes one number points to a sweep or a curve port instead."""
    lr = type(curves)(path=curves.path, record=curves.record.model_copy(deep=True), model_code=curves.model_code)
    m = next(m for m in lr.record.models if m.id == "trace_mean")
    lr.record.models.append(m.model_copy(update={"id": "scalar_mean", "inputs": {
        "U": m.inputs["U"].model_copy(update={"curve": None})}}))
    lr.model_code["scalar_mean"] = lr.model_code["trace_mean"]
    lr.record.runs.append(Run(id="run_scalar", model="scalar_mean", inputs={"U": "U_trace"}, outputs={"U_mean": "s"}))
    b = Builder(lr, cache_dir=tmp_path / "c").build()
    assert not b.runs["run_scalar"].ok and "is a curve" in b.runs["run_scalar"].error
    assert any("is a curve" in p for p in validate(lr, run=False).errors)


def test_a_curve_indexed_by_another_quantity_is_refused(curves, tmp_path):
    """A curve port names its x quantity; a curve indexed by another quantity is not passed to it."""
    lr = type(curves)(path=curves.path, record=curves.record.model_copy(deep=True), model_code=curves.model_code)
    m = next(m for m in lr.record.models if m.id == "trace_mean")
    port = m.inputs["U"]
    m.inputs["U"] = port.model_copy(update={"curve": port.curve.model_copy(update={"quantity": "velocity", "unit": "m/s"})})
    b = Builder(lr, cache_dir=tmp_path / "c").build()
    assert not b.runs["run_mean"].ok and "indexed by" in b.runs["run_mean"].error


def test_the_curves_fixture_is_sound(curves):
    """The fixture with curve ports validates with no errors."""
    rep = validate(curves, run=False)
    assert rep.sound, rep.errors


def test_a_relation_between_curve_models_is_unverifiable_not_broken(curves):
    """A relation whose models take or give a whole curve is reported unverifiable: relations sample single values."""
    from boxgraph.atlas import test_relation
    from boxgraph.schema import Relation

    rel = Relation(id="rel_x", kind="same_as", a="curves/increments", b="curves/trace_mean", provenance="proposed",
                   reason="a test")
    res = test_relation(rel, {"curves": curves})
    assert res.status == "unverifiable" and "whole curve" in res.detail
