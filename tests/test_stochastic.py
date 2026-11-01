"""Models with randomness (02-boxgraph.md, Verdicts): run several times with
different seeds; the value is the mean with its standard error; verdicts
allow for it."""

import importlib.util
import shutil
import statistics
from pathlib import Path

import pytest
import yaml

from boxgraph.engine import Builder
from boxgraph.store import load_record
from boxgraph.validate import validate

FX = Path(__file__).parent / "fixtures"

NOISY = """import random


def run(inputs, settings):
    rng = random.Random(settings["seed"])
    return {"t": 5.0 + rng.gauss(0.0, 0.3)}
"""


def edit(path, fn):
    data = yaml.safe_load(path.read_text()) if path.exists() else []
    fn(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


@pytest.fixture
def rec(tmp_path):
    d = tmp_path / "toy"
    shutil.copytree(FX / "toy", d)
    m = d / "models" / "noisy"
    m.mkdir()
    (m / "model.py").write_text(NOISY)
    (m / "model.yaml").write_text(yaml.safe_dump({
        "id": "noisy", "name": "a lifetime with sampling noise", "stochastic": True,
        "stated": {"page": 2, "quote": "integrated numerically"},
        "inputs": {"k0": {"quantity": "k0", "unit": "1/s"}}, "outputs": {"t": {"quantity": "lifetime", "unit": "s"}},
        "settings": {"seed": 1}}))
    cit = {"page": 2, "quote": "integrated numerically"}
    edit(d / "data.yaml", lambda ds: ds.extend([
        {"id": "t_noisy_ok", "quantity": "lifetime", "unit": "s", "origin": "predicted", "printed": "5.0", "citation": cit},
        {"id": "t_noisy_bad", "quantity": "lifetime", "unit": "s", "origin": "predicted", "printed": "6.0", "citation": cit}]))
    edit(d / "runs.yaml", lambda rs: rs.extend([
        {"id": "run_noisy", "model": "noisy", "inputs": {"k0": "k0"}, "outputs": {"t": "t_noisy"}},
        {"id": "run_noisy3", "model": "noisy", "inputs": {"k0": "k0"}, "outputs": {"t": "t_noisy3"}, "replicates": 3}]))
    edit(d / "comparisons.yaml", lambda cs: cs.extend([
        {"id": "cmp_noisy_ok", "purpose": "reproduction", "computed": "t_noisy", "printed": "t_noisy_ok"},
        {"id": "cmp_noisy_bad", "purpose": "reproduction", "computed": "t_noisy", "printed": "t_noisy_bad"}]))
    edit(d / "refinements.yaml", lambda rs: rs.append(
        {"id": "ref_noisy", "run": "run_noisy", "setting": "seed", "factors": [1, 2], "mode": "multiply",
         "output": "t", "tolerance": "20%", "tolerance_basis": "added", "tolerance_added": True}))
    return d


def direct(d, seeds):
    spec = importlib.util.spec_from_file_location("noisy", d / "models" / "noisy" / "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return [mod.run({"k0": 0.2}, {"seed": s})["t"] for s in seeds]


def test_a_random_model_is_run_several_times_and_reports_mean_and_standard_error(rec, tmp_path):
    """A model with randomness runs five times by default, with seeds seed, seed+1, ...; its value is the mean, with a standard error."""
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    v = b.values["t_noisy"]
    xs = direct(rec, [1, 2, 3, 4, 5])
    assert v.value == pytest.approx(statistics.mean(xs))
    assert v.se == pytest.approx(statistics.stdev(xs) / len(xs) ** 0.5)
    assert b.runs["run_noisy"].replicates == 5


def test_the_number_of_runs_can_be_set(rec, tmp_path):
    """A run can say how many times to repeat a model with randomness."""
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    assert b.runs["run_noisy3"].replicates == 3
    assert b.values["t_noisy3"].value == pytest.approx(statistics.mean(direct(rec, [1, 2, 3])))


def test_verdicts_allow_for_the_sampling_error(rec, tmp_path):
    """The mean ± 2 standard errors reproduces a value it overlaps and not one far outside it."""
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    ok, bad = b.comparisons["cmp_noisy_ok"], b.comparisons["cmp_noisy_bad"]
    assert ok.computed_se > 0
    assert ok.verdict == "reproduced", ok
    assert bad.verdict == "not reproduced"


def test_a_model_without_randomness_is_run_once_with_no_sampling_error(rec, tmp_path):
    """A model without randomness runs once, and its value has no sampling error."""
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    assert b.runs["run_decay"].replicates == 1
    assert not b.values["t_pred"].se


def test_a_random_model_needs_a_seed(rec):
    """A model marked as random must take a seed among its settings, so its runs can be repeated."""
    edit(rec / "models" / "noisy" / "model.yaml", lambda m: m.update(settings={}))
    r = validate(load_record(rec), run=False)
    assert any("noisy" in e and "seed" in e for e in r.errors)


def test_the_build_with_repeated_runs_is_deterministic(rec, tmp_path):
    """Repeated runs use fixed seeds, so the build is the same every time."""
    a = Builder(load_record(rec), cache_dir=tmp_path / "a").build().to_json()
    b = Builder(load_record(rec), cache_dir=tmp_path / "b").build().to_json()
    assert a == b


def test_the_synthesis_reports_the_sampling_error_with_each_verdict(rec, tmp_path):
    """Each verdict in the synthesis carries the computed side's standard error, None when there is none."""
    from boxgraph.synthesis import build_synthesis
    root = tmp_path / "records"
    root.mkdir()
    shutil.move(str(rec), root / "toy")
    s = build_synthesis(root, cache_dir=tmp_path / "c")
    rows = {v["comparison"]: v for v in s["papers"]["toy"]["verdicts"]}
    assert rows["cmp_noisy_ok"]["computed_se"] > 0
    assert all("computed_se" in v for v in rows.values())


def test_the_report_shows_the_computed_value_as_mean_plus_minus_two_standard_errors():
    """A computed value with sampling error is shown as mean ± 2 SE; one without is shown alone."""
    from boxgraph.report import _fmt_computed
    assert _fmt_computed(5.0, 0.15) == "5 ± 0.3"
    assert _fmt_computed([1.0, 2.0], [0.05, 0.1]) == "[1 ± 0.1, 2 ± 0.2]"
    assert _fmt_computed(5.0, None) == "5"
