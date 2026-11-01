"""Measured data in figures: error bars and bar charts (02-boxgraph.md, Values read from
figures; 05-building.md, One shared digitizer).

Test figures are drawn with matplotlib, so every true value and bar end is known."""

import math
import shutil
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

DPI = 200
FX = Path(__file__).parent / "fixtures"
needs_poppler = pytest.mark.skipif(shutil.which("pdftoppm") is None, reason="needs poppler")

PX = [1.0, 3.0, 4.5, 7.0, 9.0]
PY = [20.0, 45.0, 60.0, 30.0, 75.0]
ERR = [5.0, 8.0, 0.4, 6.0, 10.0]  # the third is smaller than the marker


def axes_of(ax, fig):
    fig.canvas.draw()
    h = fig.canvas.get_width_height()[1]

    def to_px(x, y):
        X, Y = ax.transData.transform((x, y))
        return X, h - Y

    lo, hi = ax.get_ylim()
    xt = [(to_px(t, lo)[0], t) for t in ax.get_xticks() if ax.get_xlim()[0] <= t <= ax.get_xlim()[1]]
    yt = [(to_px(0, t)[1], t) for t in ax.get_yticks() if lo <= t <= hi]
    return D.Axis("linear", xt[:2]), D.Axis(ax.get_yscale() if ax.get_yscale() == "linear" else "log10", yt[:2]), to_px


def save(fig, tmp):
    path = tmp / "fig.png"
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return D.load_image(path)


def scatter(tmp, bar_color="blue", logy=False, lower=None):
    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=DPI)
    lo_err = ERR if lower is None else lower
    ax.errorbar(PX, PY, yerr=[lo_err, ERR], fmt="s", color="blue", ecolor=bar_color, ms=6, capsize=3, elinewidth=1)
    if logy:
        ax.set_yscale("log")
        ax.set_ylim(5, 200)
    else:
        ax.set_ylim(0, 100)
    ax.set_xlim(0, 10)
    x, y, _ = axes_of(ax, fig)
    return save(fig, tmp), x, y


def test_error_bars_of_markers_are_read_without_moving_the_markers(tmp_path):
    """Each marker's value is its centre and each error bar's ends are read, within the reading precision."""
    img, x, y = scatter(tmp_path)
    rs = D.read_markers(img, x, y, color="#0000ff", error_bars=True)
    assert len(rs) == len(PX)
    for r, tx, ty, e in zip(rs, PX, PY, ERR):
        assert abs(r.x - tx) < 0.1 and r.lo <= ty <= r.hi, r
        if e < 1.0:
            continue
        assert r.bar_lo == pytest.approx(ty - e, abs=0.8) and r.bar_hi == pytest.approx(ty + e, abs=0.8), r


def test_a_bar_hidden_by_its_marker_is_reported_as_at_most_the_marker(tmp_path):
    """An error bar shorter than the marker is not invented: the reading says it lies within the marker."""
    img, x, y = scatter(tmp_path)
    r = D.read_markers(img, x, y, color="#0000ff", error_bars=True)[2]
    assert r.bar_lo is not None and r.bar_lo <= PY[2] - ERR[2] and r.bar_hi >= PY[2] + ERR[2]
    assert "within the marker" in r.note or "at most" in r.note


def test_error_bars_in_another_colour_are_read(tmp_path):
    """Black error bars on blue markers are read when the bar colour is given."""
    img, x, y = scatter(tmp_path, bar_color="black")
    rs = D.read_markers(img, x, y, color="#0000ff", error_bars=True, bar_color="#000000", box=_inside(x, y, img))
    assert len(rs) == len(PX)
    r = rs[4]
    assert r.bar_lo == pytest.approx(PY[4] - ERR[4], abs=0.8) and r.bar_hi == pytest.approx(PY[4] + ERR[4], abs=0.8)


def test_unequal_error_bars_on_a_log_axis_are_read(tmp_path):
    """On a log axis the two ends of a bar are read separately, not assumed symmetric."""
    lower = [e / 2 for e in ERR]
    img, x, y = scatter(tmp_path, logy=True, lower=lower)
    r = D.read_markers(img, x, y, color="#0000ff", error_bars=True)[4]
    assert r.bar_lo == pytest.approx(PY[4] - lower[4], rel=0.03)
    assert r.bar_hi == pytest.approx(PY[4] + ERR[4], rel=0.03)


def _inside(x, y, img):
    """The plot interior in pixels (c0, r0, c1, r1), from the axis calibration."""
    return (x.to_pixel(0.0) + 3, y.to_pixel(100.0 if y.scale == "linear" else 200.0) + 3,
            x.to_pixel(10.0) - 3, y.to_pixel(0.0 if y.scale == "linear" else 5.0) - 3)


def test_a_bar_chart_is_read_bar_by_bar(tmp_path):
    """Separate bars are read at their centres, with their heights."""
    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=DPI)
    ax.bar(PX, PY, width=0.8, color="#2a7ab0")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 100)
    x, y, _ = axes_of(ax, fig)
    img = save(fig, tmp_path)
    rs = D.read_bars(img, x, y, color="#2a7ab0", box=_inside(x, y, img))
    assert [round(r.x, 1) for r in rs] == PX
    for r, ty in zip(rs, PY):
        assert r.lo <= ty <= r.hi, r


def test_a_histogram_of_touching_bins_is_read_bin_by_bin(tmp_path):
    """Touching bins of one colour are split where the height changes."""
    edges = np.arange(0, 11, 1.0)
    counts = [5, 12, 30, 55, 70, 62, 40, 22, 9, 3]
    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=DPI)
    ax.bar(edges[:-1] + 0.5, counts, width=1.0, color="#888888")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 100)
    x, y, _ = axes_of(ax, fig)
    img = save(fig, tmp_path)
    rs = D.read_bars(img, x, y, color="#888888", box=_inside(x, y, img))
    assert len(rs) == len(counts)
    for r, c, mid in zip(rs, counts, edges[:-1] + 0.5):
        assert abs(r.x - mid) < 0.1 and r.lo <= c <= r.hi, r


@pytest.mark.parametrize("hidden", [False, True])
def test_a_bar_chart_with_error_bars_reads_both_ends_or_says_the_lower_is_mirrored(tmp_path, hidden):
    """On a bar chart both bar ends are read where drawn over the bar; a lower end hidden behind it is taken as the mirror, and said so."""
    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=DPI)
    ax.bar(PX, PY, width=0.8, color="#2a7ab0", yerr=ERR, ecolor="black", capsize=3,
           error_kw={"zorder": 0.5} if hidden else {})
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 100)
    x, y, _ = axes_of(ax, fig)
    img = save(fig, tmp_path)
    rs = D.read_bars(img, x, y, color="#2a7ab0", box=_inside(x, y, img), error_bars=True, bar_color="#000000")
    assert len(rs) == len(PX)
    r = rs[4]
    assert r.bar_hi == pytest.approx(PY[4] + ERR[4], abs=0.8)
    assert r.bar_lo == pytest.approx(PY[4] - ERR[4], abs=0.8)
    assert ("mirror" in r.note) == hidden, r.note


# -- in a record --------------------------------------------------------------------------

def t_true(F):
    return (1 / 0.2) * math.exp(-F * 0.5 / 4.1)


FS = [2.0, 5.0, 10.0, 15.0]


def make_paper(root: Path) -> dict:
    """A measured figure: points with SEM bars; the point at F = 10 is five bars off the model."""
    (root / "corpus").mkdir(parents=True)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ys = [t_true(f) for f in FS]
    ys[2] += 5 * 0.4
    ax.errorbar(FS, ys, yerr=0.4, fmt="o", color="#d62728", ms=5, capsize=3)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 6)
    xt = [t for t in ax.get_xticks() if 0 <= t <= 20]
    yt = [t for t in ax.get_yticks() if 0 <= t <= 6]
    fig.text(0.1, 0.01, "Mean lifetime; error bars are SEM (n = 12).")
    fig.savefig(root / "corpus" / "fig.pdf")
    plt.close(fig)
    img = D.render(root / "corpus" / "fig.pdf", 1, dpi=300)
    found = D.find_axes(img)
    xmarks = [[float(p), f"{v:g}"] for p, v in zip(found.x_ticks, xt)]
    ymarks = [[float(p), f"{v:g}"] for p, v in zip(sorted(found.y_ticks, reverse=True), yt)]
    return {"x": xmarks, "y": ymarks, "box": list(found.box), "size": [img.shape[1], img.shape[0]]}


@pytest.fixture
def measured(tmp_path):
    root = tmp_path / "paper"
    cal = make_paper(root)
    rec = root / "records" / "toy"
    shutil.copytree(FX / "toy", rec)
    src = yaml.safe_load((rec / "source.yaml").read_text())
    src["file"] = "corpus/fig.pdf"
    (rec / "source.yaml").write_text(yaml.safe_dump(src))
    page1 = rec / "text" / "page-001.txt"
    page1.write_text(page1.read_text() + "\nMean lifetime; error bars are SEM (n = 12).\n")
    W, H = cal["size"]
    fr = {"id": "fig_meas", "page": 1, "where": "Fig. 1", "dpi": 300, "crop": [0, 0, W, H], "box": cal["box"],
          "x": {"quantity": "force", "unit": "pN", "marks": cal["x"]},
          "y": {"quantity": "lifetime", "unit": "s", "marks": cal["y"]},
          "mode": "markers", "color": "#d62728", "what": "the measured lifetimes, red circles with error bars",
          "error_bars": "sem", "error_bars_citation": {"page": 1, "quote": "error bars are SEM"}}
    (rec / "figures.yaml").write_text(yaml.safe_dump([fr], sort_keys=False))
    data = yaml.safe_load((rec / "data.yaml").read_text())
    data.append({"id": "t_meas", "quantity": "lifetime", "unit": "s", "origin": "measured", "figure": "fig_meas",
                 "conditions": {"temperature": "300 K"}, "citation": {"page": 1, "where": "Fig. 1", "none": "a figure; it has no text to quote"}})
    (rec / "data.yaml").write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    runs = yaml.safe_load((rec / "runs.yaml").read_text())
    runs.append({"id": "run_meas", "model": "decay", "inputs": {"k0": "k0", "xb": "xb_added", "kT": "kT"},
                 "sweep": {"F": "t_meas"}, "outputs": {"t": "t_meas_pred"}})
    (rec / "runs.yaml").write_text(yaml.safe_dump(runs, sort_keys=False))
    comps = yaml.safe_load((rec / "comparisons.yaml").read_text())
    comps.append({"id": "val_meas", "purpose": "validation", "computed": "t_meas_pred", "printed": "t_meas"})
    (rec / "comparisons.yaml").write_text(yaml.safe_dump(comps, sort_keys=False))
    return root, rec


@needs_poppler
def test_measured_points_with_error_bars_validate_a_model_point_by_point(measured, tmp_path):
    """A measured datum read from a figure takes its error bars as its printed interval; the off point fails."""
    root, rec = measured
    b = Builder(load_record(rec), cache_dir=tmp_path / "c").build()
    c = b.comparisons["val_meas"]
    assert c.per_value == ["reproduced", "reproduced", "not reproduced", "reproduced"], c
    assert all("SEM" in t for t in c.printed_text), c.printed_text


@needs_poppler
def test_error_bars_need_their_meaning_cited(measured):
    """A reading with error bars must say what they are (SEM, SD, ...) and quote where the paper says so."""
    root, rec = measured
    r0 = validate(load_record(rec))
    assert r0.sound, r0.errors
    figs = yaml.safe_load((rec / "figures.yaml").read_text())
    del figs[0]["error_bars_citation"]
    (rec / "figures.yaml").write_text(yaml.safe_dump(figs, sort_keys=False))
    r = validate(load_record(rec))
    assert any("fig_meas" in e and "error bars" in e for e in r.errors), r.errors
