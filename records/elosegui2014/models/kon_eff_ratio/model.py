# kon = kont * dint for each integrin type; the ratio is taken so that the density's own unit cancels.
def run(inputs, settings):
    return {"kon_ratio": (inputs["kont2"] / inputs["kont1"]) * inputs["d_ratio"]}


def symbolic():
    import sympy as sp
    kont1, kont2, d_ratio = sp.symbols("kont1 kont2 d_ratio", positive=True)
    return {"kon_ratio": kont2 / kont1 * d_ratio}
