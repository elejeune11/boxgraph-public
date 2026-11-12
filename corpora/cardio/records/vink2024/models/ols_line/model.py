# Ordinary least squares of observer-1 MBV (y) on observer-2 MBV (x), both mL/mL, over the pooled points,
# evaluated at the x positions of the read line.


def run(inputs, settings):
    x = list(inputs["A"]["x"]) + list(inputs["B"]["x"])
    y = list(inputs["A"]["y"]) + list(inputs["B"]["y"])
    mx, my = sum(x) / len(x), sum(y) / len(y)
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    a0 = my - b * mx
    xs = list(inputs["L"]["x"])
    return {"y": {"x": xs, "y": [a0 + b * v for v in xs]}}
