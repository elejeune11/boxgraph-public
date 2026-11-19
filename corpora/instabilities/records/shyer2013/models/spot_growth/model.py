"""Spot expansion field of the planar zigzag simulation (SM p. 15), in units of the stress-free
endoderm thickness he = 1.

s(r) = 1 + (exp(-(r/c)^2) - a) t with c = 3 (from eta = [r/(3 he)]^2) and a = 0.2, as printed.

The paper calls s the 'relative expansion' without saying whether it stretches lengths or areas;
the setting `expansion` takes either reading:
  linear: s stretches lengths in the plane (area element grows by s^2);
  areal:  s multiplies the area element (lengths grow by sqrt(s)).

Spot diameter: 2c (the disc inside which eta <= 1).
Diameter growth relative to material outside the spots, where s = 1 - a t:
  linear: int_0^c s dr / ((1 - a t) c)
  areal:  sqrt(int_0^c 2 r s dr / ((1 - a t) c^2))
Area change of the endoderm sheet A0 = (we/W)(le/L) W L, W = L = (W/(he+hm)) (1 + hm/he) he, with the
spots' fields superposed over a periodic domain (integrals of each Gaussian over the plane):
  areal:  t (n pi c^2 - a A0) / A0
  linear: [A0((1 - a t)^2 - 1) + 2 (1 - a t) t n pi c^2 + t^2 n pi c^2 / 2] / A0
          (the cross terms between different spots are left out: spots several c apart).
"""
import math

C = 3.0   # eta = [r/(3 he)]^2
A = 0.2   # the printed offset in (e^-eta - 0.2)


def run(inputs, settings):
    t = inputs["t"]
    n = inputs["n_spots"]
    mode = settings.get("expansion", "linear")
    out_s = 1.0 - A * t
    gauss_1d = C * math.sqrt(math.pi) / 2.0 * math.erf(1.0)   # int_0^c exp(-(r/c)^2) dr
    gauss_2d_disc = C * C * (1.0 - math.exp(-1.0))             # int_0^c 2 r exp(-(r/c)^2) dr
    if mode == "linear":
        growth = (out_s * C + t * gauss_1d) / (out_s * C)
    elif mode == "areal":
        growth = math.sqrt((out_s * C * C + t * gauss_2d_disc) / (out_s * C * C))
    else:
        raise ValueError(f"unknown expansion reading {mode!r}")
    side = inputs["W_over_hsum"] * (1.0 + inputs["hm_over_he"])
    a0 = inputs["we_over_W"] * side * inputs["le_over_L"] * side
    plane = math.pi * C * C   # int over the plane of exp(-(r/c)^2)
    if mode == "areal":
        d_area = t * (n * plane - A * a0)
    else:
        d_area = a0 * (out_s ** 2 - 1.0) + 2.0 * out_s * t * n * plane + t * t * n * plane / 2.0
    return {"diameter": 2.0 * C, "growth": growth, "area_change": d_area / a0}
