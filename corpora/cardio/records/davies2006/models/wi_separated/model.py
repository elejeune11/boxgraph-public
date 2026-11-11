# WI+ = (1/(4 rho c)) (dP/dt + rho c dU/dt)^2, WI- = -(1/(4 rho c)) (dP/dt - rho c dU/dt)^2, in SI units:
# (Pa/s)^2 / (kg m^-3 * m/s) = kg s^-5 = W m^-2 s^-2. WInet is their sum, as the paper defines it.


def run(inputs, settings):
    dPdt, dUdt, rho, c = inputs["dPdt"], inputs["dUdt"], inputs["rho"], inputs["c"]
    z = rho * c
    wip = (dPdt + z * dUdt) ** 2 / (4.0 * z)
    wim = -((dPdt - z * dUdt) ** 2) / (4.0 * z)
    return {"WIp": wip, "WIm": wim, "WInet": wip + wim}


def symbolic():
    import sympy as sp
    dPdt, dUdt = sp.symbols("dPdt dUdt")
    rho, c = sp.symbols("rho c", positive=True)
    z = rho * c
    wip = (dPdt + z * dUdt) ** 2 / (4 * z)
    wim = -((dPdt - z * dUdt) ** 2) / (4 * z)
    return {"WIp": wip, "WIm": wim, "WInet": wip + wim}
