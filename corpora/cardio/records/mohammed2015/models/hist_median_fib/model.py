"""The median of a binned frequency distribution, interpolated linearly within the bin that holds it.

P: the bars (% of patients) against their bin labels; bins are equally wide (the label spacing w) and
each label sits at the fraction f of its bin from the bin's lower edge (f = 0.5: bins centred on their
labels). The bars are normalised by their own total, so a histogram whose bars do not add to 100 still
gives the value below which half of its patients lie."""


def run(inputs, settings):
    pts = sorted((x, max(y, 0.0)) for x, y in zip(inputs["P"]["x"], inputs["P"]["y"]))
    xs = [p[0] for p in pts]
    gaps = sorted(b - a for a, b in zip(xs, xs[1:]))
    w = gaps[(len(gaps) - 1) // 2]
    f = inputs["f"]
    total = sum(y for _, y in pts)
    half, cum = total / 2, 0.0
    for x, y in pts:
        if y > 0 and cum + y >= half:
            return {"m": x - f * w + (half - cum) / y * w}
        cum += y
    return {"m": float("nan")}
