"""Figure readings in records (02-boxgraph.md, Values read from figures).

A small paper is made as a real PDF: one figure with the model's curve in blue
and a deliberately misprinted curve (60% too high) in red. A record reads both
from the page; the build rebuilds the readings and compares them with runs."""

import math
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402
import yaml  # noqa: E402

from boxgraph import digitize as D  # noqa: E402
from boxgraph.engine import Builder  # noqa: E402
from boxgraph.store import load_record  # noqa: E402
from boxgraph.validate import validate  # noqa: E402

FX = Path(__file__).parent / "fixtures"
needs_poppler = pytest.mark.skipif(shutil.which("pdftoppm") is None, reason="needs poppler")


def t_true(F):
    return (1 / 0.2) * math.exp(-F * 0.5 / 4.1)


def make_paper(root: Path) -> dict:
    """Write corpus/fig.pdf and return the calibration found on its page."""
    (root / "corpus").mkdir(parents=True)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    Fs = np.linspace(0, 20, 300)
    ax.plot(Fs, [t_true(f) for f in Fs], color="#0000ff", lw=1.2)
    ax.plot(Fs, [1.6 * t_true(f) for f in Fs], color="#ff0000", lw=1.2)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 10)
    ax.set_xlabel("F (pN)")
    ax.set_ylabel("t (s)")
    xt = [t for t in ax.get_xticks() if 0 <= t <= 20]
    yt = [t for t in ax.get_yticks() if 0 <= t <= 10]
    fig.savefig(root / "corpus" / "fig.pdf")
    plt.close(fig)
    img = D.render(root / "corpus" / "fig.pdf", 1, dpi=300)
    found = D.find_axes(img)
    assert len(found.x_ticks) == len(xt) and len(found.y_ticks) == len(yt)
    xmarks = [[float(p), f"{v:g}"] for p, v in zip(found.x_ticks, xt)]
    ymarks = [[float(p), f"{v:g}"] for p, v in zip(sorted(found.y_ticks, reverse=True), yt)]
    return {"x": xmarks, "y": ymarks, "box": list(found.box), "size": [img.shape[1], img.shape[0]]}


def reading(fid, color, cal, at=("2", "5", "10", "15")):
    W, H = cal["size"]
    return {"id": fid, "page": 1, "where": "Fig. 1", "dpi": 300, "crop": [0, 0, W, H], "box": cal["box"],
            "x": {"quantity": "force", "unit": "pN", "marks": cal["x"]},
            "y": {"quantity": "lifetime", "unit": "s", "marks": cal["y"]},
            "mode": "curve", "color": color, "at": list(at), "what": f"the {color} curve"}


@pytest.fixture(scope="module")
def paper(tmp_path_factory):
    root = tmp_path_factory.mktemp("paper")
    cal = make_paper(root)
    rec = root / "records" / "toy"
    shutil.copytree(FX / "toy", rec)
    src = yaml.safe_load((rec / "source.yaml").read_text())
    src["file"] = "corpus/fig.pdf"
    (rec / "source.yaml").write_text(yaml.safe_dump(src))
    (rec / "figures.yaml").write_text(yaml.safe_dump([reading("fig1_blue", "#0000ff", cal),
                                                      reading("fig1_red", "#ff0000", cal)]))
    data = yaml.safe_load((rec / "data.yaml").read_text())
    for did, fid in (("t_fig", "fig1_blue"), ("t_fig_red", "fig1_red")):
        data.append({"id": did, "quantity": "lifetime", "unit": "s", "origin": "predicted", "figure": fid,
                     "citation": {"page": 1, "where": "Fig. 1", "none": "a figure; it has no text to quote"}})
    (rec / "data.yaml").write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    runs = yaml.safe_load((rec / "runs.yaml").read_text())
    for rid, did in (("run_fig", "t_fig"), ("run_fig_red", "t_fig_red")):
        runs.append({"id": rid, "model": "decay", "inputs": {"k0": "k0", "xb": "xb_added", "kT": "kT"},
                     "sweep": {"F": did}, "outputs": {"t": f"{did}_pred"}})
    (rec / "runs.yaml").write_text(yaml.safe_dump(runs, sort_keys=False))
    comps = yaml.safe_load((rec / "comparisons.yaml").read_text())
    comps += [{"id": "cmp_fig", "purpose": "reproduction", "computed": "t_fig_pred", "printed": "t_fig"},
              {"id": "cmp_fig_red", "purpose": "reproduction", "computed": "t_fig_red_pred", "printed": "t_fig_red"}]
    (rec / "comparisons.yaml").write_text(yaml.safe_dump(comps, sort_keys=False))
    return root, rec, cal


def edit(path, fn):
    data = yaml.safe_load(path.read_text())
    fn(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def copy(paper, tmp_path):
    root, rec, cal = paper
    new = tmp_path / "paper"
    shutil.copytree(root, new)
    return new, new / "records" / "toy", cal


@needs_poppler
def test_a_figure_datum_is_read_from_the_page_with_its_precision(paper, tmp_path):
    """A datum read from a figure is rebuilt from the page: a curve indexed by x, each value with the reading's interval."""
    root, rec, _ = paper
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    v = b.values["t_fig"]
    assert v.is_table and v.index == [2.0, 5.0, 10.0, 15.0] and v.index_quantity == "force"
    for F, p in zip(v.index, v.printed_values):
        assert p.how == "figure" and p.lo <= t_true(F) <= p.hi
        assert p.hi - p.lo < 0.25  # tight: a few hundredths of the 10 s axis


@needs_poppler
def test_a_true_curve_reproduces_and_a_misprinted_one_does_not(paper, tmp_path):
    """The model reproduces the curve drawn from it; the curve drawn 60% too high is not reproduced."""
    root, rec, _ = paper
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    assert b.comparisons["cmp_fig"].verdict == "reproduced", b.comparisons["cmp_fig"]
    assert b.comparisons["cmp_fig_red"].verdict == "not reproduced"


@needs_poppler
def test_the_record_with_figures_is_sound_and_overlays_are_written(paper, tmp_path):
    """A record with calibrated figure readings is sound, and each reading is drawn over its figure for checking."""
    root, rec, _ = paper
    r = validate(load_record(rec), cache_dir=tmp_path / "c")
    assert r.sound, r.errors
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    assert Path(b.figures["fig1_blue"]["overlay"]).exists()


@needs_poppler
def test_a_mislabelled_mark_is_caught(paper, tmp_path):
    """A calibration mark given the wrong label makes the marks disagree, and the record is unsound."""
    root, rec, _ = copy(paper, tmp_path)
    edit(rec / "figures.yaml", lambda fs: fs[0]["y"]["marks"][1].__setitem__(1, "7"))
    r = validate(load_record(rec), cache_dir=tmp_path / "c")
    assert any("fig1_blue" in e and "marks" in e for e in r.errors), r.errors


@needs_poppler
def test_two_marks_are_allowed_but_warned(paper, tmp_path):
    """Two marks per axis calibrate, but cannot catch a mislabel, so the record is warned."""
    root, rec, _ = copy(paper, tmp_path)
    edit(rec / "figures.yaml", lambda fs: fs[0]["x"].__setitem__("marks", fs[0]["x"]["marks"][:2]))
    r = validate(load_record(rec), cache_dir=tmp_path / "c")
    assert r.sound, r.errors
    assert any("fig1_blue" in w and "third mark" in w for w in r.warnings)


@needs_poppler
def test_a_position_the_curve_does_not_reach_is_an_error(paper, tmp_path):
    """Reading a curve where it is not drawn is an error, not a guess."""
    root, rec, _ = copy(paper, tmp_path)
    edit(rec / "figures.yaml", lambda fs: fs[0].__setitem__("color", "#00ff00"))
    r = validate(load_record(rec), cache_dir=tmp_path / "c")
    assert any("fig1_blue" in e and "no pixels" in e for e in r.errors), r.errors


def test_a_datum_has_exactly_one_of_printed_table_or_figure():
    """A datum is printed, a table, or read from a figure: exactly one."""
    from pydantic import ValidationError

    from boxgraph.schema import Datum

    base = {"id": "d", "quantity": "q", "unit": "s", "origin": "predicted", "citation": {"none": "x"}}
    Datum(**base, figure="f")
    with pytest.raises(ValidationError):
        Datum(**base, figure="f", printed="1")
    with pytest.raises(ValidationError):
        Datum(**base)


def test_a_figure_datum_must_name_a_known_reading(tmp_path):
    """A datum pointing at a figure reading that does not exist is caught."""
    rec = tmp_path / "toy"
    shutil.copytree(FX / "toy", rec)
    edit(rec / "data.yaml", lambda d: d.append({"id": "t_x", "quantity": "lifetime", "unit": "s", "origin": "predicted",
                                                "figure": "ghost", "citation": {"none": "x"}}))
    r = validate(load_record(rec), run=False)
    assert any("ghost" in e for e in r.errors)


@needs_poppler
def test_command_line_shows_axis_candidates_and_checks_a_reading(paper, tmp_path):
    """`boxgraph figure axes` numbers the tick candidates; `boxgraph figure check` prints a reading and draws it."""
    root, rec, cal = paper
    out = tmp_path / "cands.png"
    r = subprocess.run([sys.executable, "-m", "boxgraph", "figure", "axes", str(root / "corpus" / "fig.pdf"), "1",
                        "--out", str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "x ticks" in r.stdout and out.exists()
    chk = tmp_path / "check.png"
    r = subprocess.run([sys.executable, "-m", "boxgraph", "figure", "check", str(rec), "fig1_blue", "--out", str(chk)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "x = 5" in r.stdout and chk.exists()


@needs_poppler
def test_the_report_shows_each_figure_reading_for_checking(paper, tmp_path):
    """The report shows every figure reading drawn over its figure, next to the paper's verdicts."""
    root, rec, _ = paper
    out = tmp_path / "build"
    r = subprocess.run([sys.executable, "-m", "boxgraph", "build", str(root / "records"), "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    html = (out / "report.html").read_text()
    assert (out / "figures" / "toy" / "fig1_blue.png").exists()
    assert "data:image/png;base64," in html and "src='figures/" not in html


@needs_poppler
def test_a_figure_check_page_shows_each_overlay_with_its_readings_and_flags(paper, tmp_path):
    """figures.html holds every overlay in the file, each with its read points, intervals, calibration and the verdicts that use it."""
    root, rec, _ = paper
    out = tmp_path / "build"
    r = subprocess.run([sys.executable, "-m", "boxgraph", "build", str(root / "records"), "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    html = (out / "figures.html").read_text()
    assert html.count("data:image/png;base64,") == len(list((out / "figures" / "toy").glob("*.png")))
    assert "fig1_blue" in html and "fig1_red" in html and "misfit" in html
    assert "cmp_fig_red" in html and "not reproduced" in html


@needs_poppler
def test_the_synthesis_lists_each_figure_reading_with_its_points_and_the_comparisons_using_it(paper, tmp_path):
    """Each figure in the synthesis carries its points with intervals and the comparisons whose printed side it is."""
    from boxgraph.synthesis import build_synthesis

    root, rec, _ = paper
    s = build_synthesis(root / "records", cache_dir=tmp_path / "c")
    f = {f["id"]: f for f in s["papers"]["toy"]["figures"]}["fig1_red"]
    assert len(f["readings"]) == 4 and all(p["lo"] <= p["y"] <= p["hi"] for p in f["readings"])
    assert [u["comparison"] for u in f["used_by"]] == ["cmp_fig_red"] and f["used_by"][0]["verdict"] == "not reproduced"


@needs_poppler
def test_a_figure_finding_names_the_points_that_fail(paper, tmp_path):
    """A not-reproduced figure reading names the x positions that fail, with the reading and the computed value."""
    from boxgraph.synthesis import build_synthesis

    root, rec, _ = paper
    s = build_synthesis(root / "records", cache_dir=tmp_path / "c")
    f = next(f for f in s["findings"] if f["kind"] == "not_reproduced" and f["subject"] == "toy/t_fig_red")
    assert "at force = 5 pN" in f["detail"] and "read from Fig. 1" in f["detail"]


@needs_poppler
def test_a_standalone_spec_is_read_by_the_same_code_as_the_build(paper, tmp_path):
    """`boxgraph figure read SPEC` reads a figure from a spec file outside any record, with the build's own code."""
    import json

    root, rec, cal = paper
    spec = reading("blue", "#0000ff", cal) | {"pdf": str(root / "corpus" / "fig.pdf")}
    (tmp_path / "spec.yaml").write_text(yaml.safe_dump(spec))
    out = tmp_path / "read.json"
    r = subprocess.run([sys.executable, "-m", "boxgraph", "figure", "read", str(tmp_path / "spec.yaml"),
                        "--out", str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    res = json.loads(out.read_text())
    for rd in res["readings"]:
        assert rd["found"] and rd["lo"] <= t_true(rd["x"]) <= rd["hi"]


@needs_poppler
def test_without_the_pdf_figure_readings_are_checked_for_structure_only(paper, tmp_path):
    """Without its PDF (never committed), a record's figure readings are checked for structure; running them needs the PDF."""
    new, rec, _ = copy(paper, tmp_path)
    (new / "corpus" / "fig.pdf").unlink()
    structure = validate(load_record(rec), run=False)
    assert structure.sound, structure.errors
    full = validate(load_record(rec), cache_dir=tmp_path / "c")
    assert any("source file" in e for e in full.errors)
