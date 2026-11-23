"""Average elasticity of talin rod + unstructured linker over 0-F (Table T3, 'estimated based on
the WLC model'). Reconstructed: linker extension x at force F from the Marko-Siggia WLC,
F Lp / kT = 1/(4 (1 - x/L)^2) - 1/4 + x/L; rod extension F / k_rod; k_avg = F / (sum of extensions).
Units: pN/nm, nm, pN, pN*nm."""
from scipy.optimize import brentq


def run(inputs, settings):
    F, L, Lp, kT = inputs["F"], inputs["L"], inputs["Lp"], inputs["kT"]
    g = lambda z: kT / Lp * (0.25 / (1 - z) ** 2 - 0.25 + z) - F
    z = brentq(g, 0.0, 1 - 1e-12, xtol=1e-14)
    return {"k_avg": F / (F / inputs["k_rod"] + L * z)}
