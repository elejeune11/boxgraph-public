# The paper's procedure for e_c (p. 3), in words: for each cross-linker content, fit a straight line
# to l/l0 against sodium acrylate content (Fig. 2(b)); take the sodium acrylate content mid-way
# between the highest content at which the surface-attached gels stay flat and the lowest at which
# they crease (Fig. 2(a)); read l/l0 off the line there; e_c = 1 - l0/l.


def _line(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    return my - b * mx, b


def run(inputs, settings):
    c = inputs["c"]
    series = [(inputs["c02"], inputs["L02"]), (inputs["c04"], inputs["L04"]),
              (inputs["c07"], inputs["L07"]), (inputs["c10"], inputs["L10"])]
    ck, L = min(series, key=lambda s: abs(s[0] - c))
    tol = settings["composition_tol"] * ck
    flat = [x for x, y in zip(inputs["flat"]["x"], inputs["flat"]["y"]) if abs(y - ck) <= tol]
    creased = [x for x, y in zip(inputs["creased"]["x"], inputs["creased"]["y"]) if abs(y - ck) <= tol]
    if not flat or not creased:
        return {"e_c": None}
    mid = 0.5 * (max(flat) + min(creased))
    a, b = _line(L["x"], L["y"])
    lr = a + b * mid
    return {"e_c": 1.0 - 1.0 / lr}
