"""Share of patients with at least one stenosed vessel: the bars at 1 or more vessels over all bars,
in percent (normalised by the bars' own total)."""


def run(inputs, settings):
    xs, ys = inputs["P"]["x"], inputs["P"]["y"]
    total = sum(max(y, 0.0) for y in ys)
    some = sum(max(y, 0.0) for x, y in zip(xs, ys) if x >= 0.5)
    return {"s": 100.0 * some / total}
