# Fig. 8B from Fig. 8A: at each strain of the Fig. 8B reading, the slope of the secant from that
# point of the normalised curve to the next one (forward difference between consecutive strains).
# A strain missing from the normalised curve, or its last point, gives no value.
def run(inputs, settings):
    pts = sorted(zip(inputs["r"]["x"], inputs["r"]["y"]))
    xs = [p[0] for p in pts]
    out = []
    for g in inputs["grid"]["x"]:
        k = next((i for i, x in enumerate(xs) if abs(x - g) <= 1e-9 * max(1.0, abs(g))), None)
        if k is None or k + 1 >= len(pts):
            out.append(None)
            continue
        (x0, y0), (x1, y1) = pts[k], pts[k + 1]
        out.append((y1 - y0) / (x1 - x0))
    return {"s": {"x": list(inputs["grid"]["x"]), "y": out}}
