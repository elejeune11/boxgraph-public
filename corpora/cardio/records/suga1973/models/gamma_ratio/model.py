# gamma = [(dP/dt)/P]max(enhanced) / [(dP/dt)/P]max(control). Port units are those of the table; the ratio is of like quantities.

def run(inputs, settings):
    return {"gamma": inputs["D_enh"] / inputs["D_ctrl"]}


def symbolic():
    import sympy as sp
    D_enh, D_ctrl = sp.symbols("D_enh D_ctrl", positive=True)
    return {"gamma": D_enh / D_ctrl}
