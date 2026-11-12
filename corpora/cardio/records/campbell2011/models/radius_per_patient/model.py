# The diffusion radius of each patient from that patient's capillary length density, at the x
# positions (BSA) of the panel-B points, so the result can be compared point by point with B.
#
# Pairing. Panels B and C plot the same 45 men (or 11 women) against the same BSA. A point of B is
# paired with the point of C at the same BSA: points are grouped by BSA (neighbours closer than
# the tie setting, in m2, are one group; a group must hold as many points of B as of C). Within a
# group of k patients with the same BSA the panels do not say who is who; since the radius
# formula is decreasing, the highest length density is paired with the smallest radius, and so
# on (question q_fig2_pairing). Groups of one need no such choice.
#
# The formula is the diffusion_radius model's (sqrt(1/(pi Lv)), Lv in mm/mm^3, R in um).
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "campbell_diffusion_radius", Path(__file__).resolve().parent.parent / "diffusion_radius" / "model.py")
_dr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_dr)


def _groups(xs, tol):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out, cur = [], [order[0]]
    for a, b in zip(order, order[1:]):
        if xs[b] - xs[a] <= tol:
            cur.append(b)
        else:
            out.append(cur)
            cur = [b]
    out.append(cur)
    return out


def run(inputs, settings):
    tol = float(settings["bsa_tie_m2"])
    L, R = inputs["L"], inputs["R"]
    nb = len(R["x"])
    xs = list(R["x"]) + list(L["x"])  # indices < nb are panel B, the rest panel C
    y = [None] * nb
    for g in _groups(xs, tol):
        b = [i for i in g if i < nb]
        c = [i - nb for i in g if i >= nb]
        if len(b) != len(c):
            raise ValueError(f"BSA group near {xs[g[0]]:.3f} m2 has {len(b)} points in B and {len(c)} in C")
        b.sort(key=lambda i: R["y"][i])            # smallest radius first
        c.sort(key=lambda i: -L["y"][i])           # largest length density first
        for ib, ic in zip(b, c):
            y[ib] = _dr.run({"Lv": L["y"][ic]}, {})["R"]
    return {"R": {"x": list(R["x"]), "y": y}}
