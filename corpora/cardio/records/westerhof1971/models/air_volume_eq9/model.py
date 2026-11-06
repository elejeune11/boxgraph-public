MMHG_DYN_CM2 = 1333.22387415  # 1 mm Hg in dyne/cm^2


def run(inputs, settings):
    p_abs = (inputs["Patm"] + inputs["Pmean"]) * MMHG_DYN_CM2  # dyne/cm^2
    return {"V": inputs["C"] * p_abs}


def symbolic():
    import sympy as sp
    C, Patm, Pmean = sp.symbols("C Patm Pmean", positive=True)
    return {"V": C * (Patm + Pmean) * MMHG_DYN_CM2}
