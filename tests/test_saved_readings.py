"""Saved figure readings (DECISIONS, Saved figure readings).

The papers are never published, so a build without them cannot read a figure. A build that can
read them saves the numbers it read beside the record (readings.json); a build without the paper
uses those numbers, and a build with it reads again and checks them. Without either, only the
values read from that figure are left out: the rest of the record is still sound and compared."""

import json
import shutil

import pytest
import yaml
from test_figures import FX, make_paper, needs_poppler, reading

from boxgraph.engine import Builder
from boxgraph.store import load_record
from boxgraph.synthesis import build_synthesis
from boxgraph.validate import validate


@pytest.fixture(scope="module")
def saved(tmp_path_factory):
    """A toy record read from its PDF, its readings saved, as a template to copy."""
    root = tmp_path_factory.mktemp("saved")
    cal = make_paper(root)
    rec = root / "records" / "toy"
    shutil.copytree(FX / "toy", rec)
    src = yaml.safe_load((rec / "source.yaml").read_text())
    src["file"] = "corpus/fig.pdf"
    (rec / "source.yaml").write_text(yaml.safe_dump(src))
    (rec / "figures.yaml").write_text(yaml.safe_dump([reading("fig1_blue", "#0000ff", cal)]))
    data = yaml.safe_load((rec / "data.yaml").read_text())
    data.append({"id": "t_fig", "quantity": "lifetime", "unit": "s", "origin": "predicted", "figure": "fig1_blue",
                 "citation": {"page": 1, "where": "Fig. 1", "none": "a figure; it has no text to quote"}})
    (rec / "data.yaml").write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    runs = yaml.safe_load((rec / "runs.yaml").read_text())
    runs.append({"id": "run_fig", "model": "decay", "inputs": {"k0": "k0", "xb": "xb_added", "kT": "kT"},
                 "sweep": {"F": "t_fig"}, "outputs": {"t": "t_fig_pred"}})
    (rec / "runs.yaml").write_text(yaml.safe_dump(runs, sort_keys=False))
    comps = yaml.safe_load((rec / "comparisons.yaml").read_text())
    comps.append({"id": "cmp_fig", "purpose": "reproduction", "computed": "t_fig_pred", "printed": "t_fig"})
    (rec / "comparisons.yaml").write_text(yaml.safe_dump(comps, sort_keys=False))
    build_synthesis(root / "records", cache_dir=root / "cache", save_readings=True)
    return root


def _copy(saved, tmp_path, pdf=True, readings=True):
    root = tmp_path / "paper"
    shutil.copytree(saved, root, ignore=shutil.ignore_patterns("cache"))
    if not pdf:
        (root / "corpus" / "fig.pdf").unlink()
    if not readings:
        (root / "records" / "toy" / "readings.json").unlink()
    return root, root / "records" / "toy"


@needs_poppler
def test_a_build_that_reads_the_figures_saves_their_numbers_beside_the_record(saved):
    """With save_readings, the numbers read from each figure are written to readings.json, with the recipe they came from."""
    s = json.loads((saved / "records" / "toy" / "readings.json").read_text())
    assert set(s) == {"fig1_blue"}
    assert s["fig1_blue"]["recipe"] and [r["x"] for r in s["fig1_blue"]["readings"]] == [2.0, 5.0, 10.0, 15.0]


@needs_poppler
def test_saved_readings_are_not_part_of_the_record_digest(saved, tmp_path):
    """Saving readings does not change the record's digest: they are a product of the build, not authored."""
    root, rec = _copy(saved, tmp_path)
    before = load_record(rec).digest()
    (rec / "readings.json").unlink()
    assert load_record(rec).digest() == before


@needs_poppler
def test_without_the_paper_the_saved_numbers_are_used_and_the_record_is_sound(saved, tmp_path):
    """Without the PDF, the build uses the saved readings: the same values, the same verdict, and the record is sound."""
    with_pdf = Builder(load_record(saved / "records" / "toy"), cache_dir=tmp_path / "c1").build()
    root, rec = _copy(saved, tmp_path, pdf=False)
    assert validate(load_record(rec), cache_dir=tmp_path / "c2").sound
    b = Builder(load_record(rec), cache_dir=tmp_path / "c2").build()
    assert not b.problems, b.problems
    assert b.values["t_fig"].values == with_pdf.values["t_fig"].values
    assert b.comparisons["cmp_fig"].verdict == with_pdf.comparisons["cmp_fig"].verdict == "reproduced"
    assert b.figures["fig1_blue"]["from_saved"] is True
    assert any("saved" in w for w in b.warnings)


@needs_poppler
def test_with_the_paper_a_reading_that_differs_from_the_saved_one_is_reported(saved, tmp_path):
    """With the PDF, the build reads the figure again and reports where it differs from the saved numbers."""
    root, rec = _copy(saved, tmp_path)
    s = json.loads((rec / "readings.json").read_text())
    s["fig1_blue"]["readings"][1]["y"] += 1.0
    (rec / "readings.json").write_text(json.dumps(s))
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    assert b.figures["fig1_blue"]["saved"] == "differs"
    assert any("differs from the saved reading" in w and "5" in w for w in b.warnings), b.warnings
    assert b.comparisons["cmp_fig"].verdict == "reproduced"  # the page, not the saved file, is used


@needs_poppler
def test_a_saved_reading_for_another_recipe_is_not_used(saved, tmp_path):
    """A reading saved before its recipe changed is stale: without the PDF it is not used, and its values are left out."""
    root, rec = _copy(saved, tmp_path, pdf=False)
    figs = yaml.safe_load((rec / "figures.yaml").read_text())
    figs[0]["at"] = ["2", "5", "10"]
    (rec / "figures.yaml").write_text(yaml.safe_dump(figs))
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    assert b.figures["fig1_blue"]["readings"] == [] and b.figures["fig1_blue"]["saved"] == "stale"
    assert not b.problems, b.problems


@needs_poppler
def test_without_the_paper_or_a_saved_reading_only_that_figure_is_left_out(saved, tmp_path):
    """With neither, the record is still sound: the figure's comparison is left out with a warning, the rest are judged."""
    root, rec = _copy(saved, tmp_path, pdf=False, readings=False)
    assert validate(load_record(rec), cache_dir=tmp_path / "c").sound
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    assert not b.problems, b.problems
    assert b.comparisons["cmp_good"].verdict == "reproduced"
    assert any("cmp_fig" in w and "left out" in w for w in b.warnings), b.warnings
    syn = build_synthesis(root / "records", cache_dir=tmp_path / "c")
    assert syn["papers"]["toy"]["sound"]
