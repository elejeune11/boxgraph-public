"""Models against other papers' measurements (04-synthesis.md, 05-building.md: "a model in another
paper may predict them"): a record says which of its models predicts which measurement of another
record, the build runs it on that record's conditions and judges it at the measurement's precision."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from boxgraph.store import load_record
from boxgraph.synthesis import build_synthesis, to_json
from boxgraph.validate import validate

FX = Path(__file__).parent / "fixtures"


def _records(tmp_path: Path, edit=None) -> Path:
    root = tmp_path / "records"
    for name in ("toy", "toy2"):
        shutil.copytree(FX / name, root / name)
    if edit:
        f = root / "toy2" / "validations.yaml"
        entries = yaml.safe_load(f.read_text())
        edit(entries[0])
        f.write_text(yaml.safe_dump(entries))
    return root


@pytest.fixture(scope="module")
def syn(tmp_path_factory):
    root = _records(tmp_path_factory.mktemp("v"))
    return json.loads(json.dumps(to_json(build_synthesis(root, cache_dir=tmp_path_factory.mktemp("c"))), default=str))


def test_a_model_is_judged_against_another_papers_measurement(syn):
    """A model of one record, run on another record's conditions, is judged value by value against that record's measurement."""
    v = next(x for x in syn["validations"] if x["id"] == "toy2/val_lifetime_vs_toy_curve")
    assert v["status"] == "checked" and v["verdict"] == "reproduced"
    assert v["against"] == "toy/t_curve" and v["model"] == "toy2/lifetime"
    assert len(v["per_value"]) == 3 and v["printed_text"] == ["5.0", "2.7", "1.5"]
    assert "toy/lifetime = toy2/tau" in v["correspondences"] and "toy/force = toy2/f" in v["correspondences"]


def test_quantities_of_two_records_must_be_named_as_the_same(tmp_path):
    """Two records name their quantities independently: a validation that does not say which of its quantities another record's quantity is cannot be checked."""
    root = _records(tmp_path, edit=lambda e: e.pop("quantities"))
    v = next(x for x in to_json(build_synthesis(root, cache_dir=tmp_path / "c"))["validations"])
    assert v["status"] != "checked" and "quantit" in v["status"]


def test_a_measurement_in_a_record_not_in_the_synthesis_cannot_be_checked(tmp_path):
    """A validation against a record that is not in the Synthesis says so, and does not stop the build."""
    root = _records(tmp_path, edit=lambda e: e.update(against="absent/t_curve", sweep={"f": "absent/t_curve"}))
    v = to_json(build_synthesis(root, cache_dir=tmp_path / "c"))["validations"][0]
    assert v["status"].startswith("cannot be checked") and "absent" in v["status"]


@pytest.mark.parametrize("edit, says", [
    (lambda e: e.update(basis=""), "basis"),
    (lambda e: e.update(output="nope"), "nope"),
    (lambda e: e.update(against="t_curve"), "against"),
    (lambda e: e.update(inputs={"tau0": "tau0"}), "fb"),
])
def test_a_validation_says_why_and_names_a_real_model_output_and_inputs(tmp_path, edit, says):
    """A validation must give its basis, name an output and all the inputs of its model, and point at a datum of another record."""
    root = _records(tmp_path, edit=edit)
    errs = validate(load_record(root / "toy2"), run=False).errors
    assert any(says in e for e in errs), errs


def test_the_validations_of_two_records_can_be_checked_on_their_own(tmp_path):
    """`boxgraph validations records --only a,b` evaluates the validations between two records and exits 0 when each is checked."""
    root = _records(tmp_path)
    r = subprocess.run([sys.executable, "-m", "boxgraph", "validations", str(root), "--only", "toy,toy2",
                        "--cache", str(tmp_path / "c")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "val_lifetime_vs_toy_curve" in r.stdout and "reproduced" in r.stdout


def test_a_validation_that_cannot_be_checked_fails_the_check(tmp_path):
    """The same command exits 1 when a validation between the two records cannot be checked, naming why."""
    root = _records(tmp_path, edit=lambda e: e.pop("quantities"))
    r = subprocess.run([sys.executable, "-m", "boxgraph", "validations", str(root), "--only", "toy,toy2",
                        "--cache", str(tmp_path / "c")], capture_output=True, text=True)
    assert r.returncode == 1 and "quantit" in r.stdout


def test_the_written_review_reports_each_validation_and_traces_it(tmp_path):
    """The written review says, in its section across papers, which model was judged against which measurement and with what verdict, traced to the build."""
    from boxgraph.report import build_index, render_markdown, review, trace_check

    syn = build_synthesis(_records(tmp_path), cache_dir=tmp_path / "c")
    sents = review(syn)
    assert not trace_check(sents, build_index(syn))
    md = render_markdown(syn, sents)
    assert "toy2/lifetime" in md and "toy/t_curve" in md and "val_lifetime_vs_toy_curve" in md


def test_a_model_fitted_to_another_papers_measurement_is_judged_as_fit_quality(tmp_path):
    """A model fitted to another paper's measurement is entered with purpose fit_quality: it is judged the same way, and reported as a fit, not a test."""
    root = _records(tmp_path, edit=lambda e: e.update(purpose="fit_quality"))
    v = to_json(build_synthesis(root, cache_dir=tmp_path / "c"))["validations"][0]
    assert v["purpose"] == "fit_quality" and v["verdict"] == "reproduced"
