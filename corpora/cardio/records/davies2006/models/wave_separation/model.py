# dP+- = (dP +- rho c dU)/2, SI units (kg m^-3 * m/s * m/s = Pa).


def run(inputs, settings):
    z = inputs["rho"] * inputs["c"]
    return {"dPp": 0.5 * (inputs["dP"] + z * inputs["dU"]),
            "dPm": 0.5 * (inputs["dP"] - z * inputs["dU"])}


def symbolic():
    import sympy as sp
    dP, dU = sp.symbols("dP dU")
    rho, c = sp.symbols("rho c", positive=True)
    return {"dPp": (dP + rho * c * dU) / 2, "dPm": (dP - rho * c * dU) / 2}
