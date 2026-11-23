def _tops(curve):
    pts = dict(zip(curve["x"], curve["y"]))
    red = [y for x, y in pts.items() if round(x) == 1]
    blue = [y for x, y in pts.items() if round(x) == 2]
    return red[0], blue[0]


def run(inputs, settings):
    red, blue = _tops(inputs["v"])
    return {"ratio_stacked": red / (blue - red), "ratio_overlaid": red / blue}
