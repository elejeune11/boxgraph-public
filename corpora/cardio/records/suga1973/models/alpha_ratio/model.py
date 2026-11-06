# alpha = Emax(enhanced) / Emax(control). Port units are those of the table; the ratio is of like quantities.

def run(inputs, settings):
    return {"alpha": inputs["Emax_enh"] / inputs["Emax_ctrl"]}


def symbolic():
    import sympy as sp
    Emax_enh, Emax_ctrl = sp.symbols("Emax_enh Emax_ctrl", positive=True)
    return {"alpha": Emax_enh / Emax_ctrl}
