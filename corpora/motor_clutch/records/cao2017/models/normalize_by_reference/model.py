# Divide every bar of a series by the bar at the reference condition (4 = stiff fibrous ECM).


def run(inputs, settings):
    xs, ys = inputs["A"]["x"], inputs["A"]["y"]
    ref = settings["reference_condition"]
    a_ref = next(y for x, y in zip(xs, ys) if abs(x - ref) < 1e-9)
    return {"ratio": {"x": list(xs), "y": [y / a_ref for y in ys]}}
