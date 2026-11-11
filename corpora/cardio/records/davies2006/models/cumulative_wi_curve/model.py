# Cumulative wave intensity of each of the six waves (area under its WI curve) and its share of the total,
# from one subject's WI+ and WI- curves (p. 4, "Quantification of Waves"). Units: WI in W m^-2 s^-2,
# time in ms; cumulative intensity in W m^-2 s^-1 (positive, as Table 2 prints it); shares in percent.
#
# What the paper does not give is a setting:
#   t1..t6       where each wave is: a time near its extremum (wave 1, 3, 5 on WI-; 2, 4, 6 on WI+), taken
#                from the circled labels of the figure
#   search_ms    the extremum is searched within this many ms of t_k
#   total        "six": the sum of the six waves' areas; "cycle": the area of |WI+| + |WI-| over the trace
# A wave's area runs from its extremum outwards to the nearest local minimum of |WI| (or to the end of the
# trace) on each side, by the trapezoid rule on the curve's own points. WI+ is clipped at 0 from below and
# WI- at 0 from above (a digitized trace can sit a pixel on the wrong side of zero).


def _lobe(x, a, t, search):
    cand = [i for i, xi in enumerate(x) if abs(xi - t) <= search + 1e-9]
    if not cand:
        return 0.0
    k = max(cand, key=lambda i: a[i])
    lo = k
    while lo > 0 and a[lo - 1] <= a[lo] and a[lo] > 0:
        lo -= 1
    hi = k
    while hi < len(a) - 1 and a[hi + 1] <= a[hi] and a[hi] > 0:
        hi += 1
    return sum((x[i + 1] - x[i]) * (a[i] + a[i + 1]) / 2 for i in range(lo, hi)) / 1000.0


def _area(x, a):
    return sum((x[i + 1] - x[i]) * (a[i] + a[i + 1]) / 2 for i in range(len(x) - 1)) / 1000.0


def run(inputs, settings):
    xp, ap = inputs["WIp"]["x"], [max(v, 0.0) for v in inputs["WIp"]["y"]]
    xm, am = inputs["WIm"]["x"], [max(-v, 0.0) for v in inputs["WIm"]["y"]]
    s = float(settings["search_ms"])
    curves = {1: (xm, am), 2: (xp, ap), 3: (xm, am), 4: (xp, ap), 5: (xm, am), 6: (xp, ap)}
    I = {k: _lobe(*curves[k], float(settings[f"t{k}"]), s) for k in range(1, 7)}
    if settings["total"] == "six":
        total = sum(I.values())
    elif settings["total"] == "cycle":
        total = _area(xp, ap) + _area(xm, am)
    else:
        raise ValueError(f"total must be 'six' or 'cycle', got {settings['total']!r}")
    out = {f"I{k}": I[k] for k in I}
    out.update({f"p{k}": 100.0 * I[k] / total for k in I})
    return out
