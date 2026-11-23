# Cell spread area from the actin mass balance (Supplemental Eqs. 6-9), taken at its pseudo-steady state.
# v_edge = v_protrusion - v_retrograde = 0 (Eq. 6); v_protrusion = v_polymerization G/Actin_total (Eq. 9)
# gives G = Actin_total v_retrograde / v_polymerization; F-actin = Actin_total - G (Eq. 7);
# r_cell = F-actin + L_nucleus; A = pi r_cell^2. Applied point by point to a curve of the time-averaged
# retrograde flow against substrate modulus. Units: v in nm/s, lengths in nm, area in um^2.
import math


def area(v, Atot, vpoly, Lnuc):
    G = Atot * v / vpoly
    G = min(max(G, 0.0), Atot)          # the G-actin pool lies between empty and all the actin
    r = (Atot - G) + Lnuc
    return math.pi * r * r * 1e-6        # nm^2 -> um^2


def run(inputs, settings):
    c = inputs["v"]
    return {"A": {"x": list(c["x"]),
                  "y": [area(v, inputs["Atot"], inputs["vpoly"], inputs["Lnuc"]) for v in c["y"]]}}
