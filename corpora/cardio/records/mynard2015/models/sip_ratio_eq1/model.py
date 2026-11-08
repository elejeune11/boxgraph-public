# Eq. 1 divided by pV: pSIP/pV = alpha_SIP / (vV - Vp=0,V); volumes in mL.


def run(inputs, settings):
    return {"ratio": inputs["alpha"] / (inputs["vV"] - inputs["Vp0"])}


def symbolic():
    import sympy as sp
    alpha, vV, Vp0 = sp.symbols("alpha vV Vp0", positive=True)
    return {"ratio": alpha / (vV - Vp0)}
