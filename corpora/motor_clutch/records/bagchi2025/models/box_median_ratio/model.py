def run(inputs, settings):
    pts = dict(zip(inputs["v"]["x"], inputs["v"]["y"]))
    rf = [y for x, y in pts.items() if round(x) == 1][0]
    af = [y for x, y in pts.items() if round(x) == 2][0]
    return {"ratio": af / rf}
