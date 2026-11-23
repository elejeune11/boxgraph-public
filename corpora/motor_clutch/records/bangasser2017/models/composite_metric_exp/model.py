# Composite metric (Methods, "Composite metrics", p. 9) for the measured U251 data (Fig. 4f): the
# same rule as composite_metric_sim, over five metrics (random motility coefficient, cell area,
# aspect ratio, actin flow rate reflected, traction strain energy). At a modulus where a metric has
# no value, the average is over the metrics that have one. The rule is repeated here (not imported)
# so that a run depends only on this file.


def _scale(points):
    ys = [y for _, y in points]
    lo, hi = min(ys), max(ys)
    if hi == lo:
        return {x: 0.0 for x, _ in points}
    return {x: (y - lo) / (hi - lo) for x, y in points}


def run(inputs, settings):
    scaled = []
    for name in ("area", "aspect", "flow", "rmc", "strain"):
        c = inputs[name]
        pts = [(x, -y if name == "flow" else y) for x, y in zip(c["x"], c["y"]) if x is not None and y is not None]
        if pts:
            scaled.append(_scale(pts))
    xs = sorted({x for s in scaled for x in s})
    avg = [sum(s[x] for s in scaled if x in s) / sum(1 for s in scaled if x in s) for x in xs]
    lo, hi = min(avg), max(avg)
    return {"C": {"x": xs, "y": [(a - lo) / (hi - lo) if hi > lo else 0.0 for a in avg]}}
