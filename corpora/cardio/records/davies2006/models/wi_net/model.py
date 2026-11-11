# WInet = (dP/dt)(dU/dt). Pa/s * m/s^2 = W m^-2 s^-2.


def run(inputs, settings):
    return {"WInet": inputs["dPdt"] * inputs["dUdt"]}


def symbolic():
    import sympy as sp
    dPdt, dUdt = sp.symbols("dPdt dUdt")
    return {"WInet": dPdt * dUdt}
