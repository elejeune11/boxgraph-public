# Eq. 3: vp = v*p AG/AT. AG and AT in the same unit (um).


def run(inputs, settings):
    return {"vp": inputs["vp_max"] * inputs["AG"] / inputs["AT"]}


def symbolic():
    import sympy as sp
    vp_max, AG, AT = sp.symbols("vp_max AG AT", positive=True)
    return {"vp": vp_max * AG / AT}
