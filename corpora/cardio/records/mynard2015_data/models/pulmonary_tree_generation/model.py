# Adapter (software: true): regrows the pulmonary arterial and venous trees by the paper's rules (p. 5) from the
# four released lobar artery/vein pairs, and counts the segments. Only the root radii come from the released
# Supplemental File 1 (MOESM1_1D_segments.xlsx, inlet A0 of the segments named in settings.artery_roots and
# settings.vein_roots, read from $BOXGRAPH_SOURCE); the rest is our own code of the paper's words:
#   a daughter pair of a parent of radius r has radii r f1 and r f2, from Eq. 2 with exponent xi and asymmetry
#   gamma = r_d2^2 / r_d1^2: f1 = (1 + gamma^(xi/2))^(-1/xi), f2 = f1 sqrt(gamma); arteries and veins branch
#   together ('the same number of segments and the same connectivity');
#   termination ('the 1D network was terminated after a parent radius of 5 mm was reached in both the artery
#   and vein at a particular topological location'), read as: a segment branches unless both its arterial and
#   its venous radius are below r_term. This is the reading the released network follows: every released
#   pulmonary segment with a radius of at least 5 mm in its artery or its vein has daughters, and no other.
# Output: the number of segments in one of the two trees (arterial and venous are the same).
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("mynard2015_data_sheets", os.path.join(_HERE, "..", "network_counts", "_sheets.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def run(inputs, settings):
    xi, gamma, r_term = inputs["xi"], inputs["gamma"], inputs["r_term"] / 10.0  # mm -> cm
    by = {s["C"]: s for s in S.segments()}
    f1 = (1.0 + gamma ** (xi / 2.0)) ** (-1.0 / xi)
    f2 = f1 * math.sqrt(gamma)
    stack = [(math.sqrt(by[a]["E"] / math.pi), math.sqrt(by[v]["E"] / math.pi))
             for a, v in zip(settings["artery_roots"], settings["vein_roots"])]
    n = 0
    while stack:
        ra, rv = stack.pop()
        n += 1
        if n > settings["max_segments"]:
            raise ValueError("tree does not terminate")
        if ra >= r_term or rv >= r_term:
            stack += [(ra * f1, rv * f1), (ra * f2, rv * f2)]
    return {"n_segments": float(n)}
