# P_D = 2 r / I_vessel * dI_gel/dt; r in um, rate in 1/s, P_D in cm/s (1 um = 1e-4 cm).


def run(inputs, settings):
    return {"PD": 2.0 * inputs["r"] * 1e-4 / inputs["I_vessel"] * inputs["dIgel_dt"]}


def symbolic():
    import sympy as sp
    r, I_vessel, dIgel_dt = sp.symbols("r I_vessel dIgel_dt", positive=True)
    return {"PD": 2 * r * sp.Rational(1, 10000) / I_vessel * dIgel_dt}
