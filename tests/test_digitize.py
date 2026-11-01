"""Reading figures (02-boxgraph.md, Values read from figures; 05-building.md).

Test figures are drawn with matplotlib, so the true value of every point and
the pixel position of every tick are known exactly."""

import math
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402

from boxgraph import digitize as D  # noqa: E402

DPI = 200


def draw(kind="curve", color="red", logy=False, black=False, fmt="png", tmp=None):
    """Draw a figure; return (image path, ground truth dict)."""
    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=DPI)
    xs = np.linspace(0, 10, 400)
    truth = {}
    if kind == "curve":
        ys = 10 ** (xs / 4) if logy else 50 + 30 * np.sin(xs)
        ax.plot(xs, ys, color="black" if black else color, lw=1.5)
        truth["f"] = (lambda x: 10 ** (x / 4)) if logy else (lambda x: 50 + 30 * math.sin(x))
    else:
        px = np.array([1.0, 3.0, 4.5, 7.0, 9.0])
        py = np.array([20.0, 45.0, 60.0, 30.0, 75.0])
        ax.plot(px, py, "s", color=color, ms=6)
        truth["points"] = list(zip(px, py))
    if logy:
        ax.set_yscale("log")
        ax.set_ylim(1, 1000)
    else:
        ax.set_ylim(0, 100)
    ax.set_xlim(0, 10)
    fig.canvas.draw()
    h = fig.canvas.get_width_height()[1]

    def to_px(x, y):
        X, Y = ax.transData.transform((x, y))
        return X, h - Y

    truth["to_px"] = to_px
    truth["xticks"] = [(to_px(t, ax.get_ylim()[0])[0], t) for t in ax.get_xticks() if 0 <= t <= 10]
    yt = [t for t in ax.get_yticks() if ax.get_ylim()[0] <= t <= ax.get_ylim()[1]]
    truth["yticks"] = [(to_px(0, t)[1], t) for t in yt]
    path = tmp / f"fig.{fmt}"
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return path, truth


def axes_from_truth(truth, logy=False):
    x = D.Axis("linear", truth["xticks"][:2])
    y = D.Axis("log10" if logy else "linear", truth["yticks"][:2])
    return x, y


def test_axis_maps_pixels_to_values_and_back():
    """A linear or logarithmic axis maps pixels to values and back."""
    a = D.Axis("linear", [(100, 0.0), (300, 10.0)])
    assert a.to_value(200) == pytest.approx(5.0)
    assert a.to_pixel(7.5) == pytest.approx(250)
    lg = D.Axis("log10", [(400, 1.0), (100, 1000.0)])
    assert lg.to_value(300) == pytest.approx(10.0)
    assert lg.to_pixel(100.0) == pytest.approx(200)


def test_axis_with_more_marks_is_fitted_and_reports_its_residual():
    """More than two marks are fitted by least squares, and the misfit in pixels is reported."""
    a = D.Axis("linear", [(100, 0.0), (200, 5.0), (301, 10.0)])
    assert a.residual_px < 1.0
    assert a.to_value(200) == pytest.approx(5.0, abs=0.05)


def test_axis_needs_two_distinct_marks():
    """An axis calibrated with fewer than two distinct marks is refused."""
    with pytest.raises(D.CalibrationError):
        D.Axis("linear", [(100, 0.0), (100, 10.0)])
    with pytest.raises(D.CalibrationError):
        D.Axis("log10", [(100, 0.0), (200, 10.0)])


@pytest.mark.parametrize("dpi", [100, 200, 300])
@pytest.mark.parametrize("logy", [False, True])
def test_find_axes_locates_axis_lines_and_tick_marks(tmp_path, dpi, logy):
    """Every major tick, and no other, is found to within a pixel at any resolution, so calibration is exact."""
    global DPI
    DPI, old = dpi, DPI
    try:
        path, truth = draw(tmp=tmp_path, logy=logy)
    finally:
        DPI = old
    found = D.find_axes(D.load_image(path))
    assert len(found.x_ticks) == len(truth["xticks"])
    assert len(found.y_ticks) == len(truth["yticks"])
    for px, _ in truth["xticks"]:
        assert min(abs(px - t) for t in found.x_ticks) <= 1.0
    for py, _ in truth["yticks"]:
        assert min(abs(py - t) for t in found.y_ticks) <= 1.0
    if logy:
        assert found.y_minor, "minor ticks on a log axis are kept apart from the labelled ones"


def test_read_a_curve_at_given_positions(tmp_path):
    """A curve is read at given x values; each true value lies inside the reading's precision."""
    path, truth = draw(tmp=tmp_path)
    x, y = axes_from_truth(truth)
    xs = [0.5, 2.0, 3.3, 5.0, 7.7, 9.5]
    rs = D.read_curve(D.load_image(path), x, y, xs, color="#ff0000")
    for r, xv in zip(rs, xs):
        assert r.found, r.note
        assert r.lo <= truth["f"](xv) <= r.hi, (xv, r)
        assert r.hi - r.lo < 0.06 * 100  # precise to a few percent of the axis


def test_read_a_curve_on_a_log_axis(tmp_path):
    """On a logarithmic axis the reading and its precision are in data units."""
    path, truth = draw(logy=True, tmp=tmp_path)
    x, y = axes_from_truth(truth, logy=True)
    xs = [1.0, 4.0, 8.0]
    rs = D.read_curve(D.load_image(path), x, y, xs, color="#ff0000")
    for r, xv in zip(rs, xs):
        assert r.lo <= truth["f"](xv) <= r.hi, (xv, r)
        assert r.hi / r.lo < 1.15


def test_read_a_black_curve_inside_the_plot_box(tmp_path):
    """A curve the same colour as the axes is read inside the plot box, away from the axes."""
    path, truth = draw(black=True, tmp=tmp_path)
    img = D.load_image(path)
    box = D.find_axes(img).box
    x, y = axes_from_truth(truth)
    rs = D.read_curve(img, x, y, [2.0, 6.0], color="#000000", box=box)
    for r, xv in zip(rs, [2.0, 6.0]):
        assert r.found and r.lo <= truth["f"](xv) <= r.hi, (xv, r)


def test_read_plotted_points(tmp_path):
    """Plotted markers are found and read, each within its stated precision."""
    path, truth = draw(kind="markers", color="blue", tmp=tmp_path)
    x, y = axes_from_truth(truth)
    rs = D.read_markers(D.load_image(path), x, y, color="#0000ff")
    assert len(rs) == len(truth["points"])
    for r, (tx, ty) in zip(rs, truth["points"]):
        assert abs(r.x - tx) < 0.1
        assert r.lo <= ty <= r.hi


def test_a_position_with_no_curve_is_reported_not_guessed(tmp_path):
    """Where the curve is absent, the reading says so instead of guessing."""
    path, truth = draw(tmp=tmp_path)
    x, y = axes_from_truth(truth)
    r = D.read_curve(D.load_image(path), x, y, [5.0], color="#00ff00")[0]
    assert not r.found and "no pixels" in r.note


def test_render_a_pdf_page_region(tmp_path):
    """A region of a PDF page is rendered at a stated resolution for reading."""
    if shutil.which("pdftoppm") is None:
        pytest.skip("needs poppler")
    path, _ = draw(fmt="pdf", tmp=tmp_path)
    img = D.render(path, page=1, dpi=100)
    assert img.shape[2] == 3 and img.shape[1] == 500  # 5 in at 100 dpi
    crop = D.render(path, page=1, dpi=100, crop=(10, 20, 110, 70))
    assert crop.shape[:2] == (50, 100)


def test_overlay_shows_what_was_read(tmp_path):
    """The reading is drawn over the figure so a person can check it at a glance."""
    path, truth = draw(tmp=tmp_path)
    x, y = axes_from_truth(truth)
    img = D.load_image(path)
    rs = D.read_curve(img, x, y, [2.0, 5.0], color="#ff0000")
    out = tmp_path / "check.png"
    D.overlay(img, rs, x, y, out)
    over = D.load_image(out)
    assert over.shape == img.shape and not np.array_equal(over, img)


def test_ticks_are_the_evenly_spaced_candidates():
    """Labelled ticks are evenly spaced; candidates from curves touching the axis are set aside."""
    cands = [46.0, 54.5, 69.0, 72.5, 93.5, 107.5, 141.0, 188.0, 235.5]
    assert D.regular_ticks(cands) == [46.0, 93.5, 141.0, 188.0, 235.5]
    xs = [245.0, 249.0, 293.5, 338.0, 382.0, 426.0, 470.5]
    assert D.regular_ticks(xs) == [249.0, 293.5, 338.0, 382.0, 426.0, 470.5]
    assert D.regular_ticks([10.0, 50.0]) == [10.0, 50.0]


def test_candidates_are_numbered_on_an_overlay(tmp_path):
    """Every tick candidate is numbered on an image, so a reader can say which printed label each one carries."""
    path, _ = draw(tmp=tmp_path)
    img = D.load_image(path)
    found = D.find_axes(img)
    out = D.overlay_candidates(img, found, tmp_path / "cands.png")
    over = D.load_image(out)
    assert over.shape[0] > img.shape[0] and over.shape[1] > img.shape[1]
    assert found.x_candidates and found.y_candidates
    # the figure is not shifted: a pixel read off the overlay is the same pixel in the crop
    region = over[: img.shape[0], : img.shape[1]]
    dark = img.astype(float).mean(axis=2) < 100
    same = np.all(region == img, axis=2)
    assert same[dark].mean() > 0.9  # the figure's own dark pixels are where they were
    shifted = np.zeros_like(img)
    shifted[:, 40:] = img[:, :-40]
    assert np.all(shifted == img, axis=2)[dark].mean() < 0.5  # (a shifted figure would fail this test)


def test_follow_one_of_several_curves_of_the_same_colour(tmp_path):
    """With several curves of one colour, a seed point picks the curve and the reading follows it, even past a crossing."""
    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=DPI)
    xs = np.linspace(0, 10, 400)
    ax.plot(xs, 50 + 30 * np.sin(xs), "k", lw=1.2)
    ax.plot(xs, 50 + 30 * np.cos(xs), "k", lw=1.2)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 100)
    fig.canvas.draw()
    h = fig.canvas.get_width_height()[1]

    def to_px(x, y):
        X, Y = ax.transData.transform((x, y))
        return X, h - Y

    xa = D.Axis("linear", [(to_px(0, 0)[0], 0.0), (to_px(10, 0)[0], 10.0)])
    ya = D.Axis("linear", [(to_px(0, 0)[1], 0.0), (to_px(0, 100)[1], 100.0)])
    path = tmp_path / "two.png"
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    img = D.load_image(path)
    box = D.find_axes(img).box
    seed = to_px(1.5, 50 + 30 * math.sin(1.5))  # on the sine curve
    at = [0.5, 2.5, 4.0, 6.0, 8.5]  # sine and cosine cross near 3.9 and 7.1
    rs = D.read_curve(img, xa, ya, at, color="#000000", box=box, seed=seed)
    for r, xv in zip(rs, at):
        assert r.found, r.note
        assert r.lo <= 50 + 30 * math.sin(xv) <= r.hi, (xv, r)


def scanned(tmp_path, angle=0.6):
    """A figure degraded like an old scan: rasterised, rotated, blurred, noisy, grey."""
    import io

    from PIL import Image, ImageFilter

    fig, ax = plt.subplots(figsize=(6, 4), dpi=110)
    xs = np.linspace(0, 10, 500)
    ax.plot(xs, 50 + 30 * np.sin(xs / 1.5), color="black", lw=1.6)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 100)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110)
    plt.close(fig)
    im = Image.open(io.BytesIO(buf.getvalue())).convert("L").resize((1320, 880), Image.BICUBIC)
    im = im.rotate(angle, resample=Image.BICUBIC, fillcolor=255).filter(ImageFilter.GaussianBlur(1.8))
    rng = np.random.default_rng(7)
    arr = np.clip(np.asarray(im, dtype=float) * 0.92 + 18 + rng.normal(0, 9, (im.height, im.width)), 0, 255)
    path = tmp_path / "scan.png"
    Image.fromarray(arr.astype(np.uint8)).convert("RGB").save(path)
    return path


def test_the_tilt_of_a_scanned_figure_is_measured():
    """The tilt of a figure's axes is measured, so a rotated scan can be straightened."""
    import tempfile
    from pathlib import Path

    for angle in (0.0, 0.6, -1.0):
        img = D.load_image(scanned(Path(tempfile.mkdtemp()), angle))
        assert abs(D.find_skew(img) - angle) < 0.08, angle


def test_a_rotated_scan_is_read_honestly(tmp_path):
    """On a rotated, blurred, noisy scan, every true value lies inside the reading's interval after straightening."""
    img = D.deskew(D.load_image(scanned(tmp_path)))
    f = D.find_axes(img)
    assert len(f.x_ticks) == 6 and len(f.y_ticks) == 6
    xa = D.Axis("linear", list(zip(f.x_ticks, [0, 2, 4, 6, 8, 10])))
    ya = D.Axis("linear", list(zip(sorted(f.y_ticks, reverse=True), [0, 20, 40, 60, 80, 100])))
    at = [0.7, 2.3, 4.1, 5.5, 7.2, 9.4]
    rs = D.read_curve(img, xa, ya, at, "#000000", box=f.box)
    for r, x in zip(rs, at):
        truth = 50 + 30 * math.sin(x / 1.5)
        assert r.found and r.lo <= truth <= r.hi, (x, truth, r)
        assert r.hi - r.lo < 6  # honest, but still useful


def test_calibration_misfit_widens_every_interval():
    """A calibration whose marks disagree widens every reading by the misfit, never less than half a pixel."""
    img = np.full((200, 200, 3), 255, np.uint8)
    img[100:102, :, :] = 0  # a flat line at rows 100-101
    good = D.Axis("linear", [(190.0, 0.0), (10.0, 180.0)])
    bad = D.Axis("linear", [(190.0, 0.0), (101.0, 90.0), (10.0, 180.0)])  # one mark 1 px off
    xa = D.Axis("linear", [(0.0, 0.0), (200.0, 200.0)])
    r_good = D.read_curve(img, xa, good, [100.0], "#000000")[0]
    r_bad = D.read_curve(img, xa, bad, [100.0], "#000000")[0]
    assert (r_bad.hi - r_bad.lo) > (r_good.hi - r_good.lo)
