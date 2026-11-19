"""The points of one plotted series at the x positions of another (nearest point within max_dx; None if none).

E_at is used only for its x values. No interpolation: each output value is a plotted point of E.
"""


def run(inputs, settings):
    xs, ys = inputs["E"]["x"], inputs["E"]["y"]
    out = []
    for x in inputs["E_at"]["x"]:
        j = min(range(len(xs)), key=lambda k: abs(xs[k] - x))
        out.append(ys[j] if abs(xs[j] - x) <= settings["max_dx"] else None)
    return {"E": {"x": list(inputs["E_at"]["x"]), "y": out}}
