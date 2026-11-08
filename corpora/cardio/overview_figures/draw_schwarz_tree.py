"""Draw the human left coronary arterial tree of Schwarz et al. (2020) from its released network, three ways.

The overview's case study "A coronary tree solved again" shows these images. They are our own rendering of the
released data (DataverseNL, doi 10.34894/XYF65X), which is not in git:

    .venv/bin/python corpora/cardio/overview_figures/draw_schwarz_tree.py \\
        "corpus/cardio/code/schwarz_data/Human Left Coronary graph.mat"

Every segment (internal and terminal elements) is drawn from its start to its end point, projected onto the plane of
the tree's two principal directions, with line width following diameter. The colours are the released solution:
pressure, wall shear stress, and diameter.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np
import scipy.io as sio

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402

HERE = Path(__file__).parent
PAPER = "#f7f8f6"


def main(mat: str) -> None:
    tree = sio.loadmat(mat, squeeze_me=True, struct_as_record=False)["TreeQ"]
    segs = list(tree.IE) + list(tree.SE)
    a = np.array([s.startPntXYZ for s in segs], float)
    b = np.array([s.endPntXYZ for s in segs], float)
    d = np.array([float(s.d) for s in segs])
    p = np.array([float(np.nanmean(np.atleast_1d(s.P))) for s in segs]) / 133.322    # Pa -> mmHg
    w = np.array([abs(float(np.nanmean(np.atleast_1d(s.WSS)))) for s in segs])     # Pa
    pts = np.vstack([a, b])
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    a2, b2 = (a - c) @ vt[:2].T * 1e3, (b - c) @ vt[:2].T * 1e3                     # m -> mm
    order = np.argsort(d)                                                            # large vessels drawn last
    lines = np.stack([a2, b2], 1)[order]
    widths = np.clip(d[order] * 1e3 * 1.9, 0.18, 7.5)
    views = (
        ("pressure", p[order], "viridis", matplotlib.colors.Normalize(20, 90), "pressure (mmHg)"),
        ("wss", np.clip(w[order], 0.05, None), "magma", matplotlib.colors.LogNorm(0.3, 30), "wall shear stress (Pa)"),
        ("diameter", d[order] * 1e6, "plasma", matplotlib.colors.LogNorm(30, 4000), "diameter (µm)"),
    )
    for name, vals, cmap, norm, label in views:
        fig, ax = plt.subplots(figsize=(12, 7.2), facecolor=PAPER)
        lc = LineCollection(lines, linewidths=widths, cmap=cmap, norm=norm, capstyle="round")
        lc.set_array(vals)
        ax.add_collection(lc)
        ax.autoscale()
        ax.set_aspect("equal")
        ax.axis("off")
        cb = fig.colorbar(lc, ax=ax, shrink=0.7, pad=0.01)
        cb.set_label(label)
        ax.plot([a2[:, 0].min(), a2[:, 0].min() + 10], [a2[:, 1].min() - 3] * 2, color="#1d2733", lw=2)
        ax.text(a2[:, 0].min() + 5, a2[:, 1].min() - 5.5, "10 mm", ha="center", va="top", fontsize=9, color="#1d2733")
        fig.savefig(HERE / f"schwarz_tree_{name}.png", dpi=120, bbox_inches="tight", facecolor=PAPER)
        plt.close(fig)
    print(f"{len(segs)} segments drawn")


if __name__ == "__main__":
    main(sys.argv[1])
