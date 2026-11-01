"""Soundness of a record (02-boxgraph.md): every value traces to the paper or
is labelled as added, every model that can run does, units and quantities agree."""

import shutil

import pytest
import yaml

from boxgraph.store import load_record
from boxgraph.validate import quote_on_page, validate


@pytest.fixture
def work(toy_path, tmp_path):
    d = tmp_path / "toy"
    shutil.copytree(toy_path, d)
    return d


def edit(path, fn):
    data = yaml.safe_load(path.read_text())
    fn(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def errors_of(d):
    return validate(load_record(d)).errors


def test_toy_is_sound(toy):
    """The fixture record is sound."""
    r = validate(toy)
    assert r.sound, r.errors


def test_unit_must_match_quantity_dimension(work):
    """A datum whose unit does not fit its quantity makes the record unsound."""
    edit(work / "data.yaml", lambda d: d[1].update(unit="nm"))  # F is a force
    assert any("dimension" in e and "F" in e for e in errors_of(work))


def test_unknown_quantity(work):
    """A datum measuring an undeclared quantity makes the record unsound."""
    edit(work / "data.yaml", lambda d: d[0].update(quantity="nope"))
    assert any("unknown quantity" in e for e in errors_of(work))


def test_duplicate_ids(work):
    """Ids are unique within a record."""
    edit(work / "data.yaml", lambda d: d.append(dict(d[0])))
    assert any("duplicate id" in e for e in errors_of(work))


def test_unreadable_printed_value(work):
    """A printed value that cannot be read makes the record unsound."""
    edit(work / "data.yaml", lambda d: d[0].update(printed="several"))
    assert any("cannot read" in e for e in errors_of(work))


def test_quote_must_be_on_its_page(work):
    """A quote that is not on its cited page is caught."""
    edit(work / "data.yaml", lambda d: d[0].update(citation={"page": 1, "quote": "k0 = 9.9 per hour"}))
    assert any("quote not found" in e for e in errors_of(work))


def test_quote_on_wrong_page(work):
    """A real quote cited to the wrong page is caught."""
    edit(work / "data.yaml", lambda d: d[0].update(citation={"page": 2, "quote": "k0 = 0.2 /s"}))
    assert any("quote not found" in e for e in errors_of(work))


def test_page_outside_document(work):
    """A citation to a page the source does not have is caught."""
    edit(work / "data.yaml", lambda d: d[0].update(citation={"page": 40, "quote": "k0 = 0.2 /s"}))
    assert any("no text for page 40" in e for e in errors_of(work))


def test_quote_matching_tolerates_ocr_noise():
    """Quote matching tolerates OCR noise but not paraphrase."""
    page = "the reverse rate constant k_ exp(yF/kT N b ) should be replaced"
    assert quote_on_page("k- exp(γF/kT Nb)", page)
    assert not quote_on_page("forward rate constant doubled", page)


def test_runs_must_run(work):
    """Every model that can run must run: a failing model makes the record unsound."""
    (work / "models" / "decay" / "model.py").write_text("def run(inputs, settings):\n    raise ValueError('boom')\n")
    assert any("run_decay" in e and "boom" in e for e in errors_of(work))


def test_unrunnable_model_needs_an_open_question(work):
    """A model that cannot be made runnable needs an open question saying why."""
    edit(work / "models" / "drift" / "model.yaml", lambda m: m.update(runnable=False, not_runnable_reason="only in words"))
    edit(work / "runs.yaml", lambda rs: rs.remove(next(r for r in rs if r["model"] == "drift")))
    edit(work / "refinements.yaml", lambda rs: rs.remove(next(r for r in rs if r["run"] == "run_drift")))
    errs = errors_of(work)
    assert any("drift" in e and "open question" in e for e in errs)
    edit(work / "questions.yaml", lambda q: q.append({"id": "q_drift", "kind": "unstated_model", "about": ["drift"], "text": "only in words"}))
    assert errors_of(work) == []


def test_runnable_model_needs_code(work):
    """A model marked runnable needs its code."""
    (work / "models" / "drift" / "model.py").unlink()
    assert any("drift" in e and "model.py" in e for e in errors_of(work))


def test_port_units_match_quantities(work):
    """Model input and output units must fit their quantities."""
    edit(work / "models" / "decay" / "model.yaml", lambda m: m["inputs"]["F"].update(unit="s"))
    assert any("decay" in e and "dimension" in e for e in errors_of(work))


def test_comparison_refers_to_known_nodes(work):
    """A comparison must refer to values in the record."""
    edit(work / "comparisons.yaml", lambda c: c.append({"id": "c_x", "purpose": "reproduction", "computed": "t_pred", "printed": "ghost"}))
    assert any("ghost" in e for e in errors_of(work))


def test_question_about_unknown_node(work):
    """An open question must be about something in the record."""
    edit(work / "questions.yaml", lambda q: q.append({"id": "q_x", "kind": "reading", "about": ["ghost"], "text": "?"}))
    assert any("ghost" in e for e in errors_of(work))


def test_warnings_do_not_break_soundness(work):
    """Warnings, such as an added input without alternatives, do not make a record unsound."""
    edit(work / "added.yaml", lambda a: a[0].update(alternatives=[]))
    r = validate(load_record(work))
    assert r.sound
    assert any("no alternatives" in w for w in r.warnings)


def test_printed_prediction_without_comparison_warns(work):
    """A printed result never compared with a run is flagged."""
    edit(work / "comparisons.yaml", lambda c: c.pop(0))
    r = validate(load_record(work))
    assert any("logt_printed" in w and "never compared" in w for w in r.warnings)


def test_a_cited_link_must_name_a_cited_datum_and_never_change_one(tmp_path):
    """A link in cited.yaml names a datum of this record that says where it comes from, and never contradicts data.yaml."""
    from pathlib import Path

    d = tmp_path / "toy2"
    shutil.copytree(Path(__file__).parent / "fixtures" / "toy2", d)
    assert not [e for e in errors_of(d) if "cited.yaml" in e]
    (d / "cited.yaml").write_text(
        "- {datum: nowhere, from_datum: k0, evidence: x}\n"           # no such datum
        "- {datum: k0_not_cited, from_datum: k0, evidence: x}\n"      # a datum that names no source
        "- {datum: k0_cited, from_datum: other, evidence: x}\n")      # data.yaml already says k0
    edit(d / "data.yaml", lambda ds: ds.append({"id": "k0_not_cited", "quantity": "k0", "unit": "1/s", "origin": "reported",
                                                "printed": "0.2", "citation": {"none": "test fixture"}}))
    errs = [e for e in errors_of(d) if "cited.yaml" in e]
    assert any("nowhere" in e for e in errs)
    assert any("k0_not_cited" in e and "from_source" in e for e in errs)
    assert any("k0_cited" in e and "data.yaml" in e for e in errs)


def test_a_record_with_nothing_read_is_not_sound(tmp_path):
    """A record whose id does not match its folder, or that holds no data and no models, is not sound."""
    from pathlib import Path

    d = tmp_path / "empty2020"
    d.mkdir()
    shutil.copy(Path(__file__).parent / "fixtures" / "toy" / "source.yaml", d / "source.yaml")
    errs = errors_of(d)
    assert any("folder" in e for e in errs) and any("no data" in e for e in errs)
