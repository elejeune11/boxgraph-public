"""Corrected variants of evidently misprinted equations (02-boxgraph.md, Misprinted equations)."""

import shutil
from pathlib import Path

import yaml

from boxgraph.store import load_record
from boxgraph.validate import validate_path

FX = Path(__file__).parent / "fixtures"


def _copy(tmp_path):
    shutil.copytree(FX / "misprint", tmp_path / "misprint")
    return tmp_path / "misprint"


def _edit_variant(rec: Path, **changes):
    f = rec / "models" / "sum_corrected" / "model.yaml"
    m = yaml.safe_load(f.read_text())
    for k, v in changes.items():
        if v is None:
            m.pop(k, None)
        else:
            m[k] = v
    f.write_text(yaml.safe_dump(m, sort_keys=False))


def test_a_record_holds_the_printed_model_and_its_corrected_variant():
    """A model may name the printed model it corrects, with each correction's equation, change and evidence."""
    rec = load_record(FX / "misprint").record
    v = next(m for m in rec.models if m.id == "sum_corrected")
    assert v.variant_of == "sum_printed" and v.corrections[0].equation == "Eq. 1" and v.corrections[0].evidence
    assert validate_path(FX / "misprint").sound


def test_a_variant_must_name_a_printed_model_of_its_record(tmp_path):
    """A variant of a model the record does not hold, or of another variant, is an error."""
    rec = _copy(tmp_path)
    _edit_variant(rec, variant_of="nowhere")
    assert any("variant of" in e for e in validate_path(rec).errors)
    _edit_variant(rec, variant_of="sum_corrected")
    assert any("variant of" in e for e in validate_path(rec).errors)


def test_a_variant_needs_its_corrections_and_each_its_evidence(tmp_path):
    """A variant with no corrections, a correction with no evidence, or corrections on a model that is no variant, is an error."""
    rec = _copy(tmp_path)
    _edit_variant(rec, corrections=[])
    assert any("corrections" in e for e in validate_path(rec).errors)
    _edit_variant(rec, corrections=[{"equation": "Eq. 1", "change": "plus for minus", "evidence": " "}])
    assert any("evidence" in e for e in validate_path(rec).errors)
    _edit_variant(rec, variant_of=None, corrections=[{"equation": "Eq. 1", "change": "plus", "evidence": "the text"}])
    assert any("variant" in e for e in validate_path(rec).errors)


def test_a_variants_verdicts_are_reported_apart_from_the_paper_as_printed(tmp_path):
    """The paper's own tally counts only the printed model; a variant's comparisons are tallied as corrected, with what was corrected."""
    from boxgraph.synthesis import build_synthesis

    rec = _copy(tmp_path)
    syn = build_synthesis(rec.parent, cache_dir=tmp_path / "cache")
    p = syn["papers"]["misprint"]
    assert p["tally"]["not reproduced"] == 1 and p["tally"]["reproduced"] == 0
    assert p["tally_by_purpose"]["reproduction, corrected"]["reproduced"] == 1
    v = next(v for v in p["verdicts"] if v["comparison"] == "cmp_corrected")
    assert v["variant"]["of"] == "sum_printed" and v["variant"]["corrections"][0]["equation"] == "Eq. 1"


def test_the_report_says_which_equation_a_variant_corrects(tmp_path):
    """The report names the corrected equation and its evidence beside the variant's verdict."""
    from boxgraph.report import render_markdown, review
    from boxgraph.synthesis import build_synthesis

    rec = _copy(tmp_path)
    syn = build_synthesis(rec.parent, cache_dir=tmp_path / "cache")
    md = render_markdown(syn, review(syn))
    assert "reproduction, corrected (Eq. 1)" in md
    assert any("Eq. 1" in s.text and "corrected" in s.text and "the printed y = 5.0 is a + b" in s.text for s in review(syn))


def test_the_variant_sentence_traces_to_the_synthesis(tmp_path):
    """Every id and number in the review's sentence about a variant is found in the Synthesis."""
    from boxgraph.report import build_index, review, trace_check
    from boxgraph.synthesis import build_synthesis

    rec = _copy(tmp_path)
    syn = build_synthesis(rec.parent, cache_dir=tmp_path / "cache")
    sents = [s for s in review(syn) if "never replacing the printed model" in s.text]
    assert sents and trace_check(sents, build_index(syn)) == []


def test_a_finding_says_when_a_corrected_variant_reproduces_what_the_printed_model_misses(tmp_path):
    """The printed model's miss stays a finding, naming the correction that reproduces it; a variant's own comparisons make no finding about the paper."""
    from boxgraph.synthesis import build_synthesis

    rec = _copy(tmp_path)
    syn = build_synthesis(rec.parent, cache_dir=tmp_path / "cache")
    fs = [f for f in syn["findings"] if f["kind"] == "not_reproduced" and f["source"] == "misprint"]
    assert len(fs) == 1 and "cmp_printed" in " ".join(fs[0]["trace"])
    assert "sum_corrected" in fs[0]["detail"] and "Eq. 1" in fs[0]["detail"] and "reproduced" in fs[0]["detail"]
