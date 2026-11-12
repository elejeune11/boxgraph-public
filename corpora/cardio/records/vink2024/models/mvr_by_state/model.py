# MVR(state) = MBV(state) / MBV(state 1, baseline) for the states after baseline (the logic of mvr_ratio).
# MBV in mL/mL, MVR dimensionless; x is the study state index (1 baseline, 2 hyperinsulinemia, 3 stress).


def run(inputs, settings):
    c = inputs["MBV"]
    pts = {round(x): y for x, y in zip(c["x"], c["y"])}
    base = pts[1]
    xs = sorted(k for k in pts if k > 1)
    return {"MVR": {"x": [float(k) for k in xs], "y": [pts[k] / base for k in xs]}}
