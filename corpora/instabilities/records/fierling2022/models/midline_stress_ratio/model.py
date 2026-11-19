# The ratio of the two stress profiles at their point nearest the midline (smallest angle).


def _at_midline(curve):
    pts = sorted(zip(curve["x"], curve["y"]))
    return pts[0][1]


def run(inputs, settings):
    return {"ratio": _at_midline(inputs["s_ap"]) / _at_midline(inputs["s_dv"])}
