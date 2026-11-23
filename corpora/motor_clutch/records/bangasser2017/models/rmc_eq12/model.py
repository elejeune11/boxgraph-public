# Eq. 12: mu = <r^2>/(4 t). The slope of a line through the origin fitted to the first half of the
# <r^2>(t) points (by time order); mu = slope/4. The paper weights each point by its uncertainty;
# a curve input carries none, so the fit here is unweighted.


def run(inputs, settings):
    pts = sorted(zip(inputs["msd"]["x"], inputs["msd"]["y"]))
    n = max(1, int(len(pts) * float(settings.get("first_fraction", 0.5)) + 0.5))
    pts = pts[:n]
    sxx = sum(t * t for t, _ in pts)
    sxy = sum(t * r for t, r in pts)
    return {"mu": (sxy / sxx) / 4.0}
