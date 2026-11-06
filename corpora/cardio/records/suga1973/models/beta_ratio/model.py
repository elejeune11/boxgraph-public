# beta = Tmax(control) / Tmax(enhanced). Port units are those of the table; the ratio is of like quantities.

def run(inputs, settings):
    return {"beta": inputs["Tmax_ctrl"] / inputs["Tmax_enh"]}


def symbolic():
    import sympy as sp
    Tmax_ctrl, Tmax_enh = sp.symbols("Tmax_ctrl Tmax_enh", positive=True)
    return {"beta": Tmax_ctrl / Tmax_enh}
