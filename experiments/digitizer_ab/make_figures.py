"""Six test figures with exact ground truth, each a one-page PDF with a caption.

  python make_figures.py OUTDIR

Writes OUTDIR/<fig>.pdf and OUTDIR/truth.json. The truth is the plotted
function evaluated at the query x positions; axis spans are recorded so
errors can be expressed as a fraction of the axis.
"""

import io
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

META = {"CreationDate": None, "ModDate": None}


def page(caption: str):
    fig = plt.figure(figsize=(8.5, 6))
    ax = fig.add_axes([0.14, 0.24, 0.72, 0.66])
    fig.text(0.14, 0.08, caption, fontsize=10, wrap=True)
    return fig, ax


def f_single(x):
    return 50 + 30 * math.sin(x / 1.5)


def f_log(x):
    return 10 ** (x / 4)


def f_family(x, k):
    return 20 * k * (1 - math.exp(-x / 3))


def f_cross_a(x):
    return 80 - 6 * x + 0.15 * x * x


def f_cross_b(x):
    return 20 + 6 * x - 0.15 * x * x


def make(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    X = np.linspace(0, 10, 500)
    truth = {}

    # 1. one coloured curve, linear axes
    fig, ax = page("Fig. 1. The response y against the dose x.")
    ax.plot(X, [f_single(x) for x in X], color="#1f4fd8", lw=1.4)
    ax.set_xlim(0, 10), ax.set_ylim(0, 100), ax.set_xlabel("x"), ax.set_ylabel("y")
    fig.savefig(out / "single.pdf", metadata=META)
    plt.close(fig)
    at = [0.7, 2.3, 4.1, 5.5, 7.2, 9.4]
    truth["single"] = {"what": "the blue curve", "at": at, "y": [f_single(x) for x in at], "scale": "linear",
                       "span": [0, 100]}

    # 2. log axis with minor ticks
    fig, ax = page("Fig. 2. The rate y against time x, on a logarithmic axis.")
    ax.plot(X, [f_log(x) for x in X], color="black", lw=1.2)
    ax.set_yscale("log"), ax.set_xlim(0, 10), ax.set_ylim(1, 1000), ax.set_xlabel("x"), ax.set_ylabel("y")
    fig.savefig(out / "log.pdf", metadata=META)
    plt.close(fig)
    at = [0.5, 2.5, 5.0, 7.5, 9.5]
    truth["log"] = {"what": "the curve", "at": at, "y": [f_log(x) for x in at], "scale": "log10", "span": [1, 1000]}

    # 3. four curves of one colour
    fig, ax = page("Fig. 3. Growth y against time x for k = 1, 2, 3 and 4 (from the lowest curve to the highest).")
    for k in (1, 2, 3, 4):
        ax.plot(X, [f_family(x, k) for x in X], color="black", lw=1.1)
    ax.set_xlim(0, 10), ax.set_ylim(0, 100), ax.set_xlabel("x"), ax.set_ylabel("y")
    fig.savefig(out / "family.pdf", metadata=META)
    plt.close(fig)
    at = [1.0, 3.0, 5.0, 7.0, 9.0]
    truth["family"] = {"what": "the curve for k = 3 (the second from the top)", "at": at,
                       "y": [f_family(x, 3) for x in at], "scale": "linear", "span": [0, 100]}

    # 4. two crossing curves of one colour
    fig, ax = page("Fig. 4. Two quantities against x. Curve A starts at y = 80 at x = 0; curve B starts at y = 20.")
    ax.plot(X, [f_cross_a(x) for x in X], color="black", lw=1.2)
    ax.plot(X, [f_cross_b(x) for x in X], color="black", lw=1.2)
    ax.set_xlim(0, 10), ax.set_ylim(0, 100), ax.set_xlabel("x"), ax.set_ylabel("y")
    fig.savefig(out / "crossing.pdf", metadata=META)
    plt.close(fig)
    at = [1.0, 3.0, 4.6, 7.0, 9.0]
    truth["crossing"] = {"what": "curve A (the one starting at y = 80 at x = 0)", "at": at,
                         "y": [f_cross_a(x) for x in at], "scale": "linear", "span": [0, 100]}

    # 5. a degraded 'scan': rasterised, blurred, noisy, slightly rotated, grey
    from PIL import Image, ImageFilter

    f2, a2 = plt.subplots(figsize=(6, 4), dpi=110)
    a2.plot(X, [f_single(x) for x in X], color="black", lw=1.6)
    a2.set_xlim(0, 10), a2.set_ylim(0, 100), a2.set_xlabel("x"), a2.set_ylabel("y")
    buf = io.BytesIO()
    f2.savefig(buf, format="png", dpi=110)
    plt.close(f2)
    im = Image.open(io.BytesIO(buf.getvalue())).convert("L").rotate(0.6, resample=Image.BICUBIC, fillcolor=255)
    im = im.filter(ImageFilter.GaussianBlur(0.9))
    rng = np.random.default_rng(7)
    arr = np.clip(np.asarray(im, dtype=float) * 0.92 + 18 + rng.normal(0, 9, (im.height, im.width)), 0, 255)
    im = Image.fromarray(arr.astype(np.uint8))
    fig = plt.figure(figsize=(8.5, 6))
    axi = fig.add_axes([0.1, 0.2, 0.8, 0.75])
    axi.imshow(im, cmap="gray", vmin=0, vmax=255)
    axi.axis("off")
    fig.text(0.14, 0.08, "Fig. 5. The response y against the dose x (scanned from the original).", fontsize=10)
    fig.savefig(out / "scan.pdf", metadata=META, dpi=300)
    plt.close(fig)
    at = [0.7, 2.3, 4.1, 5.5, 7.2, 9.4]
    truth["scan"] = {"what": "the curve", "at": at, "y": [f_single(x) for x in at], "scale": "linear", "span": [0, 100]}

    # 6. points with error bars
    px = [0.8, 2.1, 3.4, 4.9, 6.3, 7.6, 9.1]
    py = [12.0, 27.5, 41.0, 55.5, 49.0, 66.0, 81.5]
    fig, ax = page("Fig. 6. Measured y against x (mean and standard deviation of three repeats).")
    ax.errorbar(px, py, yerr=[4, 6, 5, 7, 5, 6, 8], fmt="o", color="#d62728", ecolor="black", capsize=3, ms=5)
    ax.set_xlim(0, 10), ax.set_ylim(0, 100), ax.set_xlabel("x"), ax.set_ylabel("y")
    fig.savefig(out / "markers.pdf", metadata=META)
    plt.close(fig)
    truth["markers"] = {"what": "the red points (the centre of each marker, not the error bars)", "at": px, "y": py,
                        "scale": "linear", "span": [0, 100], "markers": True}

    (out / "truth.json").write_text(json.dumps(truth, indent=1))
    return truth


if __name__ == "__main__":
    make(Path(sys.argv[1]))
