"""Ratio of two plotted curves at their common x values (stages)."""


def run(inputs, settings):
    e = dict(zip(inputs["mu_e"]["x"], inputs["mu_e"]["y"]))
    m = dict(zip(inputs["mu_m"]["x"], inputs["mu_m"]["y"]))
    xs = sorted(x for x in e if any(abs(x - k) < 1e-6 for k in m))
    ys = [e[x] / next(m[k] for k in m if abs(x - k) < 1e-6) for x in xs]
    return {"ratio": {"x": xs, "y": ys}}
