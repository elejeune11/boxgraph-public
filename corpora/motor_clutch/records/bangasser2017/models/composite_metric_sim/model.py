# Composite metric (Methods, "Composite metrics", p. 9), for the simulator's four metrics (Fig. 1g):
# each data set is min-max scaled to [0, 1] (actin flow reflected first: its optimum is a minimum),
# the scaled sets are averaged at each stiffness (over the metrics that have a value there), and the
# averages are scaled again to span [0, 1]. Min-max scaling makes the result independent of each
# metric's unit, so the ports' units only label the inputs.


def _scale(points):
    ys = [y for _, y in points]
    lo, hi = min(ys), max(ys)
    if hi == lo:
        return {x: 0.0 for x, _ in points}
    return {x: (y - lo) / (hi - lo) for x, y in points}


def composite(curves, inverted):
    scaled = []
    for name, c in sorted(curves.items()):
        pts = [(x, -y if name in inverted else y) for x, y in zip(c["x"], c["y"]) if x is not None and y is not None]
        if pts:
            scaled.append(_scale(pts))
    xs = sorted({x for s in scaled for x in s})
    avg = [sum(s[x] for s in scaled if x in s) / sum(1 for s in scaled if x in s) for x in xs]
    lo, hi = min(avg), max(avg)
    return {"x": xs, "y": [(a - lo) / (hi - lo) if hi > lo else 0.0 for a in avg]}


def run(inputs, settings):
    return {"C": composite({k: inputs[k] for k in ("flow", "traction", "aspect", "rmc")}, inverted={"flow"})}
