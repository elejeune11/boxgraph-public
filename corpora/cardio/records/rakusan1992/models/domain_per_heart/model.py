# Per-heart domain area from per-heart capillary density: A = 1/CD, CD in 1/mm^2, A in um^2
# (1 mm^2 = 1e6 um^2). The hearts of the density scatter (CD) are paired with those of the domain
# scatter (A) by the rank of their heart mass (the same hearts appear in both figures); the result is
# returned at the heart masses of A, so that it can be compared with A point by point. Both scatters
# must hold the same number of hearts.


def run(inputs, settings):
    cx, cy = inputs["CD"]["x"], inputs["CD"]["y"]
    ax = inputs["A"]["x"]
    if len(cx) != len(ax):
        raise ValueError(f"{len(cx)} hearts in the density scatter, {len(ax)} in the domain scatter")
    cd = [y for _, y in sorted(zip(cx, cy))]
    xs = sorted(ax)
    return {"A_pred": {"x": xs, "y": [1e6 / c for c in cd]}}
