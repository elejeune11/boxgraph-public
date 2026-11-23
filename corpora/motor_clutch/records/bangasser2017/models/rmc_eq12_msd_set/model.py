# Eq. 12 applied to three averaged MSD curves (Supplementary Fig. 2E), one per substrate: for each,
# mu = slope / 4 of a line through the origin fitted to the first half of <r^2>(t) (the rule of
# rmc_eq12, repeated here so a run depends only on this file). The result is a curve of mu against
# the substrate modulus each MSD curve was measured on. Unweighted: a read curve carries no weights.


def _mu(curve, frac):
    pts = sorted((t, r) for t, r in zip(curve["x"], curve["y"]) if t is not None and r is not None)
    n = max(1, int(len(pts) * frac + 0.5))
    pts = pts[:n]
    return sum(t * r for t, r in pts) / sum(t * t for t, _ in pts) / 4.0


def run(inputs, settings):
    frac = float(settings.get("first_fraction", 0.5))
    pairs = sorted((inputs[f"E_{k}"], _mu(inputs[f"msd_{k}"], frac)) for k in ("a", "b", "c"))
    return {"mu": {"x": [e for e, _ in pairs], "y": [m for _, m in pairs]}}
