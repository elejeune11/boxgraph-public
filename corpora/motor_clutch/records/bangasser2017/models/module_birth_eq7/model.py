# Eq. 7: kmod = k*mod (AG/AT)^4.


def run(inputs, settings):
    return {"kmod": inputs["kmod_max"] * (inputs["AG"] / inputs["AT"]) ** 4}


def symbolic():
    import sympy as sp
    kmod_max, AG, AT = sp.symbols("kmod_max AG AT", positive=True)
    return {"kmod": kmod_max * (AG / AT) ** 4}
