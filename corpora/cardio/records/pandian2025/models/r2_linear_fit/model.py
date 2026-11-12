# R2 of the ordinary least-squares line through (manual diameter, algorithm diameter); equals Pearson r^2.
# The paper does not say whether its R2 is of a fitted line or of the identity line y = x; the fit lines drawn in
# Fig. 2a are fitted lines, so the fitted line is used. Units cancel.
def run(inputs, settings):
    x = list(inputs["P"]["x"])
    y = list(inputs["P"]["y"])
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return {"R2": sxy * sxy / (sxx * syy)}
