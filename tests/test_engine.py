"""The build of one record (02-boxgraph.md): runs, comparisons, verdicts,
refinement, alternatives of added inputs, conditions, quantities."""

import math

from boxgraph.engine import Builder, conditions_agree


def test_runs_produce_outputs_with_origin_from_role(toy_build):
    """A run produces an output whose origin follows from the model's role."""
    rr = toy_build.runs["run_decay"]
    assert rr.ok, rr.error
    v = toy_build.values["t_pred"]
    assert v.kind == "output" and v.origin == "predicted" and v.run == "run_decay"
    assert math.isclose(v.value, 2.7174, rel_tol=1e-4)


def test_results_are_produced_not_asserted(toy_build):
    """Every computed value in the build was made by a recorded run (principle 5)."""
    # every non-printed, non-added value in the build was made by a run
    for v in toy_build.values.values():
        if v.kind == "output":
            assert v.run in toy_build.runs


def test_added_inputs_are_tracked_on_runs(toy_build):
    """A run records which of its inputs were added rather than printed."""
    assert toy_build.runs["run_decay"].added_inputs == ["xb_added"]


def test_reproduction_verdict(toy_build):
    """A printed result that follows from its model and inputs is reproduced."""
    c = toy_build.comparisons["cmp_good"]
    assert c.ok and c.verdict == "reproduced"


def test_misprint_is_not_reproduced_across_scales(toy_build):
    """A misprinted log value is judged in the printed scale and found not reproduced."""
    c = toy_build.comparisons["cmp_log"]
    assert c.ok, c.error
    assert c.verdict == "not reproduced"
    # compared in the printed scale (log10 s): about 15 decades apart
    assert math.isclose(c.computed_value, math.log10(2.7174), rel_tol=1e-3)
    assert c.difference > 15


def test_printed_value_is_never_corrected(toy_build, toy):
    """The printed value stays exactly as printed after the build (principle 1)."""
    printed = next(d for d in toy.record.data if d.id == "logt_printed")
    assert printed.printed == "-14.7"
    assert toy_build.values["logt_printed"].value == -14.7


def test_curve_is_one_datum_judged_value_by_value(toy_build):
    """A curve is one datum, produced by a sweep and judged point by point."""
    c = toy_build.comparisons["cmp_curve"]
    assert c.ok, c.error
    assert c.per_value == ["reproduced", "reproduced", "reproduced"]
    assert c.verdict == "reproduced"
    assert toy_build.values["t_curve_pred"].is_table


def _with_hot_comparison(toy, conditions_ok=None):
    from boxgraph.schema import Comparison

    rec = toy.record.model_copy(deep=True)
    rec.comparisons.append(Comparison(id="cmp_hot", purpose="validation", computed="t_pred", printed="t_hot",
                                      conditions_ok=conditions_ok))
    return type(toy)(path=toy.path, record=rec, model_code=toy.model_code)


def test_conditions_that_disagree_block_a_comparison(toy, tmp_path):
    """Values under different conditions are not compared without a reason."""
    c = Builder(_with_hot_comparison(toy), cache_dir=tmp_path).build().comparisons["cmp_hot"]
    assert not c.ok
    assert "conditions disagree" in c.error


def test_a_label_lets_differing_conditions_be_compared(toy, tmp_path):
    """A labelled reason lets values under different conditions be compared."""
    t = _with_hot_comparison(toy, conditions_ok="10 K changes the rate by under 4%, inside the printed precision")
    c = Builder(t, cache_dir=tmp_path).build().comparisons["cmp_hot"]
    assert c.ok and c.verdict == "reproduced"
    assert "temperature" in c.conditions_note


def test_conditions_rule():
    """Conditions agree when every condition both name matches; one-sided conditions are noted."""
    assert conditions_agree({"T": "300 K"}, {"T": "300 K"})[0]
    assert conditions_agree({"T": "300 K"}, {"T": "26.85 degC"})[0]
    ok, notes = conditions_agree({"T": "300 K"}, {})
    assert ok and "one side only" in notes[0]
    assert not conditions_agree({"T": "300 K"}, {"T": "310 K"})[0]


def test_alternatives_run_one_at_a_time_and_report_changed_verdicts(toy_build):
    """Each alternative of an added input is run one at a time, and verdicts it flips are reported."""
    alts = {a["alternative"]: a for a in toy_build.alternatives if a["added"] == "xb_added"}
    assert set(alts) == {"1.0", "0.51"}
    changed = {c["comparison"] for c in alts["1.0"]["verdict_changes"]}
    assert "cmp_good" in changed  # x_b = 1.0 nm flips the verdict: reported
    # a small change of the added input moves only the curve's last point to "close"
    small = {c["comparison"]: c["alternative"] for c in alts["0.51"]["verdict_changes"]}
    assert small == {"cmp_curve": "close"}


def test_refinement_settles_for_the_model(toy_build):
    """A result that settles as its step is refined belongs to the model (Figure 5)."""
    r = toy_build.refinements["ref_euler"]
    assert "error" not in r, r.get("error")
    assert r["settles"] and r["belongs_to"] == "model"
    assert r["shift"] <= 0.01


def test_refinement_that_settles_far_from_the_papers_setting_belongs_to_the_numerics(toy_build):
    """A result that settles, but far from its value at the paper's own setting, belongs to the numerics (principle 8)."""
    r = toy_build.refinements["ref_coarse"]
    assert r["settles"]
    assert r["belongs_to"] == "numerics"
    assert r["shift"] > 0.05  # 5.5 at the paper's step against about 5.0 refined


def test_refinement_keeps_moving_for_the_numerics(toy_build):
    """A result that keeps moving as its step is refined belongs to the numerics."""
    r = toy_build.refinements["ref_drift"]
    assert not r["settles"] and r["belongs_to"] == "numerics"


def test_build_is_deterministic(toy, tmp_path):
    """The same record builds to the same result twice (principle 11)."""
    a = Builder(toy, cache_dir=tmp_path / "a").build().to_json()
    b = Builder(toy, cache_dir=tmp_path / "b").build().to_json()
    assert a == b


def test_quantity_mismatch_is_refused(toy, tmp_path):
    """An input of the right dimension but the wrong quantity is refused (principle 6)."""
    rec = toy.record.model_copy(deep=True)
    rec.runs[0].inputs["xb"] = "x_wrong"  # a length, but not the quantity x_b
    toy2 = type(toy)(path=toy.path, record=rec, model_code=toy.model_code)
    b = Builder(toy2, cache_dir=tmp_path / "c").build()
    assert not b.runs["run_decay"].ok
    assert "expects quantity" in b.runs["run_decay"].error


def test_model_errors_are_reported_not_raised(toy, tmp_path):
    """A failing run is reported as a problem, not a crash."""
    rec = toy.record.model_copy(deep=True)
    rec.runs[0].inputs.pop("kT")
    toy2 = type(toy)(path=toy.path, record=rec, model_code=toy.model_code)
    b = Builder(toy2, cache_dir=tmp_path / "d").build()
    assert not b.runs["run_decay"].ok
    assert any("run_decay" in p for p in b.problems)


def test_a_torn_cache_file_is_recomputed(tmp_path):
    """A cache file cut short (a concurrent writer, a full disk) is run again, not read or crashed on."""
    from boxgraph import engine

    m = tmp_path / "m" / "model.py"
    m.parent.mkdir()
    m.write_text("def run(inputs, settings):\n    return {'y': inputs['x'] * 2}\n")
    calls = [{"inputs": {"x": 3.0}, "settings": {}}]
    first = engine.execute(m, calls, cache_dir=tmp_path / "cache")
    (cf,) = (tmp_path / "cache").glob("*.json")
    cf.write_text(cf.read_text()[:5])
    engine._CACHE.clear()
    assert engine.execute(m, calls, cache_dir=tmp_path / "cache") == first
    assert not list((tmp_path / "cache").glob("*.tmp*"))


def test_a_curve_is_compared_only_at_the_same_x_values(tmp_path):
    """A computed curve is compared with a printed one only at the same x values (after unit conversion), never by list position."""
    import shutil
    from pathlib import Path

    import yaml

    from boxgraph.store import load_record

    d = tmp_path / "toy"
    shutil.copytree(Path(__file__).parent / "fixtures" / "toy", d)
    data = yaml.safe_load((d / "data.yaml").read_text())
    curve = next(x for x in data if x["id"] == "t_curve")
    rev = {**curve, "id": "t_curve_rev", "table": {**curve["table"], "index": list(reversed(curve["table"]["index"]))}}
    nn = {**curve, "id": "t_curve_nn", "table": {**curve["table"], "index_unit": "nN", "index": ["0", "0.005", "0.010"]}}
    data += [rev, nn]
    (d / "data.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
    comps = yaml.safe_load((d / "comparisons.yaml").read_text())
    comps += [{"id": "cmp_rev", "purpose": "reproduction", "computed": "t_curve_pred", "printed": "t_curve_rev"},
              {"id": "cmp_nn", "purpose": "reproduction", "computed": "t_curve_pred", "printed": "t_curve_nn"}]
    (d / "comparisons.yaml").write_text(yaml.safe_dump(comps, sort_keys=False))
    b = Builder(load_record(d), cache_dir=tmp_path / "c").build()
    assert not b.comparisons["cmp_rev"].ok and "x values" in b.comparisons["cmp_rev"].error
    assert b.comparisons["cmp_nn"].ok, b.comparisons["cmp_nn"].error
    assert b.comparisons["cmp_nn"].verdict == b.comparisons["cmp_curve"].verdict


def test_a_model_built_from_another_is_rerun_when_that_one_changes(tmp_path):
    """The cache key of a model covers the code of the models it is built from, so changing one never leaves stale results."""
    import shutil
    from pathlib import Path

    import yaml

    from boxgraph.store import load_record

    d = tmp_path / "toy"
    shutil.copytree(Path(__file__).parent / "fixtures" / "toy", d)
    w = d / "models" / "wrapper"
    w.mkdir()
    spec = yaml.safe_load((d / "models" / "decay" / "model.yaml").read_text())
    spec.update(id="wrapper", name="the decay model, loaded from its folder", built_from=["decay"])
    (w / "model.yaml").write_text(yaml.safe_dump(spec))
    (w / "model.py").write_text(
        "import importlib.util, os\n"
        "_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'decay', 'model.py')\n"
        "_s = importlib.util.spec_from_file_location('decay_inner', _p)\n"
        "_m = importlib.util.module_from_spec(_s)\n"
        "_s.loader.exec_module(_m)\n"
        "def run(i, s):\n    return _m.run(i, s)\n")
    runs = yaml.safe_load((d / "runs.yaml").read_text())
    runs.append({"id": "run_wrapper", "model": "wrapper", "inputs": {"k0": "k0", "F": "F", "xb": "xb_added", "kT": "kT"},
                 "outputs": {"t": "t_wrapped"}})
    (d / "runs.yaml").write_text(yaml.safe_dump(runs, sort_keys=False))
    first = Builder(load_record(d), cache_dir=tmp_path / "c").build().values["t_wrapped"].value
    src = d / "models" / "decay" / "model.py"
    src.write_text(src.read_text().replace('return {"t": (1 / inputs["k0"])', 'return {"t": (2 / inputs["k0"])'))
    from boxgraph import engine

    engine._CACHE.clear()
    second = Builder(load_record(d), cache_dir=tmp_path / "c").build().values["t_wrapped"].value
    assert math.isclose(second, 2 * first)


def test_inputs_that_disagree_on_a_condition_give_a_mixed_condition_whatever_their_order(tmp_path):
    """When a run's inputs name different values of one condition, its outputs carry both, sorted, and the build warns."""
    import shutil
    from pathlib import Path

    import yaml

    from boxgraph.store import load_record

    def build(order):
        d = tmp_path / "-".join(order)
        shutil.copytree(Path(__file__).parent / "fixtures" / "toy", d)
        data = yaml.safe_load((d / "data.yaml").read_text())
        for x in data:
            if x["id"] == "k0":
                x["conditions"] = {"temperature": "300 K"}
            if x["id"] == "F":
                x["conditions"] = {"temperature": "310 K"}
        (d / "data.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
        runs = yaml.safe_load((d / "runs.yaml").read_text())
        r = next(x for x in runs if x["id"] == "run_decay")
        r["inputs"] = {k: r["inputs"][k] for k in order}
        (d / "runs.yaml").write_text(yaml.safe_dump(runs, sort_keys=False))
        return Builder(load_record(d), cache_dir=tmp_path / "c").build()

    a, b = build(["k0", "F", "xb", "kT"]), build(["F", "k0", "xb", "kT"])
    assert a.values["t_pred"].conditions == b.values["t_pred"].conditions
    assert a.values["t_pred"].conditions["temperature"] == "300 K | 310 K"
    assert any("temperature" in w and "run_decay" in w for w in a.warnings)
