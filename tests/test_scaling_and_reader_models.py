"""Scaling laws printed without a prefactor, and models the reader reconstructed (DECISIONS, Scaling laws
and reconstructed models).

A law printed as lambda ~ t (E/Es)^(1/3) fixes how the result scales, not its size. Its values are judged
on their shape only: against one measurement the build gives the prefactor the measurement implies and no
verdict; against two or more it fits the one constant and judges what is left. A model the reader built
because the paper does not give its analysis is reported apart from the paper's own results."""

import shutil
from pathlib import Path

import pytest
import yaml

from boxgraph.engine import Builder
from boxgraph.store import load_record
from boxgraph.synthesis import build_synthesis
from boxgraph.validate import validate_path

FX = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    return Builder(load_record(FX / "scaling"), cache_dir=tmp_path_factory.mktemp("c")).build()


def _copy(tmp_path):
    shutil.copytree(FX / "scaling", tmp_path / "scaling", ignore=shutil.ignore_patterns("__pycache__"))
    return tmp_path / "scaling"


def _edit_model(rec: Path, mid: str, **changes):
    f = rec / "models" / mid / "model.yaml"
    m = yaml.safe_load(f.read_text())
    for k, v in changes.items():
        if v is None:
            m.pop(k, None)
        else:
            m[k] = v
    f.write_text(yaml.safe_dump(m, sort_keys=False))


def test_a_model_may_say_its_prefactor_is_unknown_and_a_model_may_be_marked_reconstructed():
    """`prefactor: unknown` and `reconstructed: <why>` are part of a model; the fixture is sound."""
    rec = load_record(FX / "scaling").record
    m = {x.id: x for x in rec.models}
    assert m["deep_law"].prefactor == "unknown" and m["period"].prefactor == "stated"
    assert m["plate_guess"].reconstructed and m["period"].reconstructed is None
    assert validate_path(FX / "scaling").sound


def test_prefactor_takes_only_stated_or_unknown_and_reconstructed_needs_a_reason(tmp_path):
    """Any other prefactor value, or an empty reason for a reconstruction, is an error."""
    rec = _copy(tmp_path)
    _edit_model(rec, "deep_law", prefactor="maybe")
    assert not validate_path(rec).sound
    _edit_model(rec, "deep_law", prefactor="unknown")
    _edit_model(rec, "plate_guess", reconstructed=" ")
    assert any("reconstructed" in e for e in validate_path(rec).errors)


def test_against_one_measurement_a_scaling_law_gives_the_implied_prefactor_and_no_verdict(built):
    """lambda ~ t (E/Es)^(1/3) = 2 mm against a measured 4.0 mm: no verdict, implied prefactor 2."""
    r = built.comparisons["cmp_one"]
    assert r.ok and r.verdict == "no verdict"
    assert r.prefactor_model == "deep_law" and r.implied_prefactor == pytest.approx(2.0)


def test_against_a_curve_the_prefactor_is_fitted_and_the_shape_is_judged(built):
    """Against 4, 8, 16 mm at t = 1, 2, 4 mm the fitted prefactor is 2 and the scaled values reproduce."""
    r = built.comparisons["cmp_curve"]
    assert r.verdict == "reproduced" and r.implied_prefactor == pytest.approx(2.0)
    assert r.computed_value == pytest.approx([4.0, 8.0, 16.0])
    assert "fitted" in r.prefactor_note


def test_a_curve_of_the_wrong_shape_is_not_reproduced_even_with_the_best_prefactor(built):
    """Against 4, 5, 6 mm (not proportional to t) no single prefactor fits: not reproduced."""
    assert built.comparisons["cmp_flat"].verdict == "not reproduced"


def test_a_curve_of_one_point_is_treated_like_one_measurement(built):
    """With a single point there is no shape to judge: no verdict, the implied prefactor only."""
    r = built.comparisons["cmp_single_row"]
    assert r.verdict == "no verdict" and r.implied_prefactor == pytest.approx(2.0)


def test_a_value_computed_through_further_models_gets_no_verdict(built):
    """A value that depends on a scaling law through another model is not judged; the note names the law."""
    r = built.comparisons["cmp_period"]
    assert r.verdict == "no verdict" and r.implied_prefactor is None
    assert r.prefactor_model == "deep_law" and "through" in r.prefactor_note
    assert built.values["period_pred"].prefactor_model == "deep_law"


def test_a_reconstructed_model_and_a_model_with_no_citation_are_the_readers(built):
    """Values from a reconstructed model, or from a model the paper does not state at all, carry the reader's mark."""
    assert built.values["lam_plate"].reader_model == "plate_guess"
    assert built.values["lam_check"].reader_model == "reader_check"
    assert built.values["lam_pred"].reader_model is None


def test_in_a_this_work_record_an_uncited_model_is_not_marked(tmp_path):
    """A record of the reader's own work cites none of its models; they are not set apart."""
    rec = _copy(tmp_path)
    src = yaml.safe_load((rec / "source.yaml").read_text())
    src["kind"] = "this_work"
    (rec / "source.yaml").write_text(yaml.safe_dump(src))
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    assert b.values["lam_check"].reader_model is None
    assert b.values["lam_plate"].reader_model == "plate_guess"  # an explicit reconstruction still is


def test_in_released_code_or_data_an_uncited_model_is_processing_not_the_readers(tmp_path):
    """In a dataset or software record an uncited model processes the source's own files: it is not set apart."""
    rec = _copy(tmp_path)
    src = yaml.safe_load((rec / "source.yaml").read_text())
    src["kind"] = "dataset"
    (rec / "source.yaml").write_text(yaml.safe_dump(src))
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    assert b.values["lam_check"].reader_model is None


def test_the_synthesis_reports_these_comparisons_apart_from_the_papers_own(tmp_path):
    """Purposes are labelled 'prefactor unknown' and "reader's model"; the paper's own tally counts neither."""
    root = tmp_path / "r"
    root.mkdir()
    shutil.copytree(FX / "scaling", root / "scaling", ignore=shutil.ignore_patterns("__pycache__"))
    syn = build_synthesis(root, cache_dir=tmp_path / "c")
    p = syn["papers"]["scaling"]
    by = p["tally_by_purpose"]
    assert by["reproduction, prefactor unknown"]["not reproduced"] == 1
    assert by["validation, prefactor unknown"]["reproduced"] == 1
    assert by["reproduction, reader's model"]["not reproduced"] == 1
    assert by["consistency, reader's model"]["reproduced"] == 1
    assert sum(p["tally"].values()) == 0  # neither kind counts as the paper's own reproduction
    v = {x["comparison"]: x for x in p["verdicts"]}
    assert v["cmp_one"]["implied_prefactor"] == pytest.approx(2.0)


def test_findings_say_whose_model_failed(tmp_path):
    """A reconstruction that misses is a reader_model_differs finding; a scaling law of the wrong shape is
    not_reproduced, with its fitted prefactor in the detail."""
    root = tmp_path / "r"
    root.mkdir()
    shutil.copytree(FX / "scaling", root / "scaling", ignore=shutil.ignore_patterns("__pycache__"))
    syn = build_synthesis(root, cache_dir=tmp_path / "c")
    kinds = {f["subject"]: f for f in syn["findings"]}
    assert kinds["scaling/lam_unpublished"]["kind"] == "reader_model_differs"
    assert "plate_guess" in kinds["scaling/lam_unpublished"]["detail"]
    assert kinds["scaling/lam_flat"]["kind"] == "not_reproduced"
    assert "prefactor" in kinds["scaling/lam_flat"]["detail"]
