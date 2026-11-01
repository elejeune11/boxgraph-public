"""Figure readings by the reader's own code (05-building.md, Reading figures).

The reader writes code for a figure; the record keeps it, and every build runs it
on the rendered page in an isolated interpreter, like a model."""

import math
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
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


READER = '''import numpy as np

X = {x}   # (pixel, value) pairs found on this figure
Y = {y}


def _fit(marks):
    p = np.array([m[0] for m in marks]); v = np.array([m[1] for m in marks])
    a, b = np.polyfit(p, v, 1)
    return a, b


def read(image, at):
    ax, bx = _fit(X); ay, by = _fit(Y)
    blue = (image[..., 2] > 180) & (image[..., 0] < 120) & (image[..., 1] < 120)
    out = []
    for x in at:
        col = int(round((x - bx) / ax))
        rows = np.nonzero(blue[:, col])[0]
        if len(rows) == 0:
            out.append({{"x": x, "y": None, "found": False, "note": "no curve here"}})
            continue
        r = rows.mean() + 0.5
        h = (rows.max() - rows.min() + 1) / 2 + 1.0
        lo, hi = sorted((ay * (r + h) + by, ay * (r - h) + by))
        out.append({{"x": x, "y": ay * r + by, "lo": lo, "hi": hi, "px": [col + 0.5, r]}})
    return out
'''


def make(root: Path, reader: str | None = None):
    (root / "corpus").mkdir(parents=True)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    Fs = [i * 20 / 299 for i in range(300)]
    ax.plot(Fs, [t_true(f) for f in Fs], color="#0000ff", lw=1.2)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 10)
    xt = [t for t in ax.get_xticks() if 0 <= t <= 20]
    yt = [t for t in ax.get_yticks() if 0 <= t <= 10]
    fig.savefig(root / "corpus" / "fig.pdf")
    plt.close(fig)
    img = D.render(root / "corpus" / "fig.pdf", 1, dpi=300)
    found = D.find_axes(img)
    xm = [(float(p), float(v)) for p, v in zip(found.x_ticks, xt)]
    ym = [(float(p), float(v)) for p, v in zip(sorted(found.y_ticks, reverse=True), yt)]
    rec = root / "records" / "toy"
    shutil.copytree(FX / "toy", rec)
    src = yaml.safe_load((rec / "source.yaml").read_text())
    src["file"] = "corpus/fig.pdf"
    (rec / "source.yaml").write_text(yaml.safe_dump(src))
    (rec / "figures").mkdir()
    (rec / "figures" / "fig1_blue.py").write_text(reader if reader is not None else READER.format(x=xm, y=ym))
    H, W = img.shape[:2]
    fr = {"id": "fig1_blue", "page": 1, "where": "Fig. 1", "what": "the blue curve", "dpi": 300, "crop": [0, 0, W, H],
          "x": {"quantity": "force", "unit": "pN"}, "y": {"quantity": "lifetime", "unit": "s"},
          "mode": "code", "code": "figures/fig1_blue.py", "at": ["2", "5", "10", "15"]}
    (rec / "figures.yaml").write_text(yaml.safe_dump([fr], sort_keys=False))
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
    return rec


def _marks(rec: Path):
    """The (pixel, value) marks written into a record made by make()."""
    src = (rec / "figures" / "fig1_blue.py").read_text()
    ns: dict = {}
    exec(src.split("def _fit")[0].replace("import numpy as np", ""), ns)
    return ns["X"], ns["Y"]


@needs_poppler
def test_the_readers_own_code_is_run_by_every_build(tmp_path):
    """A reading by the reader's code is rebuilt from the page, compared, and drawn on an overlay."""
    rec = make(tmp_path / "p")
    r = validate(load_record(rec))
    assert r.sound, r.errors
    b = Builder(load_record(rec), cache_dir=tmp_path / "build" / "cache").build()
    c = b.comparisons["cmp_fig"]
    assert c.verdict == "reproduced", c
    assert all("read by the record's code" in t for t in c.printed_text)
    assert Path(b.figures["fig1_blue"]["overlay"]).exists()


@needs_poppler
def test_code_that_fails_is_reported_not_crashed(tmp_path):
    """Reading code that raises gives the reading an error naming it, and the record is not sound."""
    rec = make(tmp_path / "p", reader="def read(image, at):\n    raise ValueError('no axes')\n")
    r = validate(load_record(rec))
    assert not r.sound and any("fig1_blue" in e and "no axes" in e for e in r.errors), r.errors


@needs_poppler
def test_every_value_must_say_where_it_was_read(tmp_path):
    """A value without its pixel position cannot be checked on the overlay, and is an error."""
    rec = make(tmp_path / "p", reader="def read(image, at):\n    return [{'x': x, 'y': 1.0, 'lo': 0.9, 'hi': 1.1} for x in at]\n")
    r = validate(load_record(rec))
    assert any("fig1_blue" in e and "px" in e for e in r.errors), r.errors


def test_a_code_reading_needs_its_code(tmp_path):
    """A reading in code mode must name a code file in the record that exists."""
    rec = make(tmp_path / "p")
    (rec / "figures" / "fig1_blue.py").unlink()
    r = validate(load_record(rec), run=False)
    assert any("fig1_blue" in e and "code" in e for e in r.errors), r.errors


@needs_poppler
def test_a_standalone_spec_runs_its_code_from_the_command_line(tmp_path):
    """`boxgraph figure read` runs a code reading named in a standalone spec, as the build does."""
    import json
    import subprocess
    import sys

    rec = make(tmp_path / "p")
    fr = yaml.safe_load((rec / "figures.yaml").read_text())[0]
    fr["pdf"] = str(tmp_path / "p" / "corpus" / "fig.pdf")
    fr["code"] = str(rec / "figures" / "fig1_blue.py")
    (tmp_path / "spec.yaml").write_text(yaml.safe_dump(fr))
    r = subprocess.run([sys.executable, "-m", "boxgraph", "figure", "read", str(tmp_path / "spec.yaml"),
                        "--out", str(tmp_path / "a.json"), "--overlay", str(tmp_path / "o.png")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    got = json.loads((tmp_path / "a.json").read_text())["readings"]
    assert [round(g["x"]) for g in got] == [2, 5, 10, 15] and all(g["lo"] <= t_true(g["x"]) <= g["hi"] for g in got)
    assert (tmp_path / "o.png").exists()


@needs_poppler
def test_error_bars_read_by_code_give_the_values_interval_even_when_their_kind_is_unstated(tmp_path):
    """A code reading that returns bar ends (without widened outer ends, and with no bar kind recorded) gives each value the bar as its interval."""
    bars = READER.replace('out.append({{"x": x, "y": ay * r + by, "lo": lo, "hi": hi, "px": [col + 0.5, r]}})',
                          'y = ay * r + by\n        out.append({{"x": x, "y": y, "lo": lo, "hi": hi, "px": [col + 0.5, r], '
                          '"bar_lo": y - 1.0, "bar_hi": y + 1.0}})')
    assert bars != READER
    rec = make(tmp_path / "p")
    (rec / "figures" / "fig1_blue.py").write_text(bars.format(x=_marks(rec)[0], y=_marks(rec)[1]))
    b = Builder(load_record(rec), cache_dir=tmp_path / "build" / "cache").build()
    v = b.values["t_fig"]
    assert all(p is not None and math.isclose(p.hi - p.lo, 2.0, rel_tol=1e-6) for p in v.printed_values)
    assert "bar" in v.printed_values[0].text
