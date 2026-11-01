"""Mistakes in a record are reported as problems of that record; they never crash a build,
a validation or the Synthesis (a sound record is what the build reports, not a precondition)."""

import shutil
from pathlib import Path

import yaml

from boxgraph.engine import Builder
from boxgraph.store import load_record
from boxgraph.synthesis import build_synthesis
from boxgraph.validate import validate

FX = Path(__file__).parent / "fixtures"


def _toy(tmp_path, name="toy"):
    d = tmp_path / name
    shutil.copytree(FX / name, d)
    return d


def _edit(path, fn):
    data = yaml.safe_load(path.read_text())
    fn(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def test_a_refinement_of_an_unknown_output_is_a_problem(tmp_path):
    """A refinement naming an output its run does not have is reported, not raised."""
    d = _toy(tmp_path)
    _edit(d / "refinements.yaml", lambda rs: rs[0].update(output="nonexistent"))
    b = Builder(load_record(d), cache_dir=tmp_path / "c").build()
    assert any("nonexistent" in p for p in b.problems)


def test_a_tolerance_with_a_unit_is_an_error_of_the_record(tmp_path):
    """A refinement tolerance that is neither a percentage nor a number is a validation error, and the build reports it."""
    d = _toy(tmp_path)
    _edit(d / "refinements.yaml", lambda rs: rs[0].update(tolerance="0.01 s"))
    assert any("tolerance" in e for e in validate(load_record(d), run=False).errors)
    b = Builder(load_record(d), cache_dir=tmp_path / "c").build()
    assert any("tolerance" in p for p in b.problems)


def test_a_model_that_prints_still_runs(tmp_path):
    """Output a model prints does not corrupt the reply from the isolated runner."""
    d = _toy(tmp_path)
    src = d / "models" / "decay" / "model.py"
    src.write_text(src.read_text().replace("def run(inputs, settings):", "def run(inputs, settings):\n    print('debug output')"))
    b = Builder(load_record(d), cache_dir=tmp_path / "c").build()
    assert b.runs["run_decay"].ok, b.runs["run_decay"].error


def test_a_relation_whose_test_fails_is_unverifiable_not_a_crash(tmp_path):
    """A relation whose test cannot be carried out (here a mapping outside its domain) is unverifiable, and the Synthesis is still built."""
    root = tmp_path / "r"
    for n in ("toy", "toy2"):
        shutil.copytree(FX / n, root / n)
    _edit(root / "toy2" / "relations.yaml", lambda rs: rs.append(
        {"id": "rel_dims", "kind": "same_as", "a": "toy/decay", "b": "toy2/zeroforce", "mapping": {"k0": "log(-k0)"},
         "regime": {"k0": [0.1, 1], "F": [0, 5], "xb": [0.1, 1], "kT": [4, 4.3]}, "provenance": "proposed",
         "reason": "test fixture"}))
    syn = build_synthesis(root, cache_dir=tmp_path / "c")
    rel = next(r for r in syn["relations"] if r["key"] == "toy2/rel_dims")
    assert rel["status"] == "unverifiable"
