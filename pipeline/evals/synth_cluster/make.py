"""Make the synthetic cluster paper, a fourth paper for an end-to-end trial of
adding a paper to the corpus. It cites Bell 1978 and Erdmann & Schwarz 2004,
states the Bell off-rate (Eq. 1) and the lifetime of a cluster without
rebinding (Eq. 2), prints Eq. 2 in a table, and plots measured lifetimes with
SEM bars against Eq. 2. Planted: Table 1's N0 = 4 row is printed 1.150; Eq. 2
gives 1.105. Deterministic: the same PDF every time."""

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PAGE1 = """Lifetimes of Small Adhesion Clusters without Rebinding
R. Q. Sample and T. Placeholder, Journal of Synthetic Results 3, 12 (2026)

Abstract. We measure the lifetime of small clusters of adhesion bonds held
at constant force and compare it with the mean-field result for clusters
that cannot rebind.

1. Model. Each closed bond in a cluster of N0 bonds opens at the rate

        k(F) = k0 exp(F / Fb),                                         (1)

the form proposed by Bell [1], where F is the force on that bond, k0 the
zero-force off-rate and Fb = kB T / xb the force scale. The total force Ft
is shared equally by the i bonds still closed, and an open bond does not
close again. As in the treatment of Erdmann and Schwarz [2] with the
rebinding rate set to zero, the mean time until the last bond opens is

        T = sum_{i=1}^{N0} 1 / ( i k0 exp( Ft / (i Fb) ) ).            (2)

2. Results. Table 1 gives Eq. 2 in units of 1/k0 for a dimensionless total
force f = Ft/Fb = 1.

        Table 1. Mean cluster lifetime T k0 at f = 1 (Eq. 2).

            N0        1       2       3       4       5
            T k0    0.368   0.671   0.910   1.150   1.268

For our bonds k0 = 0.5 s^-1 and Fb = 4 pN. Fig. 1 shows lifetimes measured
at Ft = 4 pN for clusters of 1 to 5 bonds (mean +/- SEM, n = 40 clusters
each) with Eq. 2 for the same values. The measured lifetimes follow Eq. 2
within their error bars.

References
[1] G. I. Bell, Models for the specific adhesion of cells to cells,
    Science 200, 618 (1978).
[2] T. Erdmann, U. S. Schwarz, Stability of adhesion clusters under
    constant force, Phys. Rev. Lett. 92, 108102 (2004)."""

MEASURED = [(1, 0.70, 0.06), (2, 1.40, 0.09), (3, 1.78, 0.10), (4, 2.25, 0.12), (5, 2.49, 0.13)]


def T(N0: int, f: float, k0: float = 1.0) -> float:
    return sum(1 / (i * k0 * math.exp(f / i)) for i in range(1, N0 + 1))


def main(out: Path) -> None:
    from matplotlib.backends.backend_pdf import PdfPages

    with PdfPages(out, metadata={"CreationDate": None, "ModDate": None}) as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.08, 0.95, PAGE1, va="top", family="monospace", fontsize=9.5)
        pdf.savefig(fig)
        plt.close(fig)
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_axes([0.18, 0.5, 0.62, 0.36])
        Ns = [n for n, _, _ in MEASURED]
        ax.plot(Ns, [T(n, 1.0, 0.5) for n in Ns], color="#1f4fbf", lw=1.3, marker="", label="Eq. 2")
        ax.errorbar(Ns, [m for _, m, _ in MEASURED], yerr=[s for _, _, s in MEASURED], fmt="s", color="#c03030",
                    ms=6, capsize=4, lw=1.2, label="measured")
        ax.set_xlim(0.5, 5.5)
        ax.set_ylim(0, 3)
        ax.set_xticks(Ns)
        ax.set_xlabel("cluster size N0")
        ax.set_ylabel("mean lifetime T (s)")
        ax.legend(loc="lower right", frameon=False)
        fig.text(0.18, 0.44, "Fig. 1. Mean lifetime of clusters of N0 bonds at a total force Ft = 4 pN:\n"
                 "measured (squares, mean +/- SEM, n = 40 each) and Eq. 2 with k0 = 0.5 s^-1, Fb = 4 pN (line).",
                 fontsize=10, va="top")
        pdf.savefig(fig)
        plt.close(fig)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
