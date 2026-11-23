# Ratio of the bar at index 1 (soft) to the bar at index 2 (stiff).


def run(inputs, settings):
    c = inputs["y"]
    by = {round(x): y for x, y in zip(c["x"], c["y"]) if x is not None and y is not None}
    return {"ratio": by[1] / by[2]}
