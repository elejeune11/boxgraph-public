"""Make the synthetic figure paper: one page, the lifetime law, its inputs, and
a figure whose 'Eq. 1' curve is drawn with x_b = 0.7 nm instead of the stated
0.5 nm. Deterministic: the same PDF every time."""

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

TEXT = """Bond Lifetimes under Force: a Short Note
B. N. Example, Journal of Synthetic Results 2, 1 (2026)

The mean lifetime of a bond under a constant force F follows the law

        t = (1 / k0) exp(-F xb / kT)                                  (1)

with the zero-force off-rate k0 = 0.2 s^-1, the distance to the transition
state xb = 0.5 nm, and the thermal energy kT = 4.1 pN nm. Fig. 1 shows the
lifetime predicted by Eq. 1 for forces from 0 to 20 pN."""


def t_eq1(F, xb):
    return (1 / 0.2) * math.exp(-F * xb / 4.1)


def main(out: Path) -> None:
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.1, 0.93, TEXT, va="top", family="monospace", fontsize=10)
    ax = fig.add_axes([0.18, 0.18, 0.62, 0.36])
    F = np.linspace(0, 20, 300)
    ax.plot(F, [t_eq1(f, 0.7) for f in F], color="#000000", lw=1.3)  # planted: 0.7, not 0.5
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 6)
    ax.set_xlabel("force F (pN)")
    ax.set_ylabel("lifetime t (s)")
    fig.text(0.18, 0.12, "Fig. 1. Mean bond lifetime against force, from Eq. 1.", fontsize=10)
    fig.savefig(out, metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
