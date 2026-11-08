# In periodic steady state the capacitors Ca and Cim carry no mean current, so the mean flow of each
# coronary bed model is (mean outlet pressure - mean venous pressure) / q0, q0 = Ra + Ra-micro + (Rv + Rv-micro).
# With the same mean outlet and venous pressures at every outlet, the flows split as the conductances 1/q0.
LAD, LCX, RCA = "abcd", "efgh", "ijk"


def _g(inputs, o):
    return 1.0 / (inputs["Ra_" + o] + inputs["Ram_" + o] + inputs["Rv_" + o])


def run(inputs, settings):
    g = {o: _g(inputs, o) for o in LAD + LCX + RCA}
    gt = sum(g.values())
    q = inputs["Q_total"]
    return {"Q_LAD": q * sum(g[o] for o in LAD) / gt,
            "Q_LCX": q * sum(g[o] for o in LCX) / gt,
            "Q_RCA": q * sum(g[o] for o in RCA) / gt}
