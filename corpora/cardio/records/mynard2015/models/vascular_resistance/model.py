# R [mmHg s/mL] = (P_in - P_out) [mmHg] / (CO [L/min] * 1000 / 60) [mL/s].


def run(inputs, settings):
    q_ml_s = inputs["CO"] * 1000.0 / 60.0
    return {"R": (inputs["P_in"] - inputs["P_out"]) / q_ml_s}


def symbolic():
    import sympy as sp
    P_in, P_out, CO = sp.symbols("P_in P_out CO", positive=True)
    return {"R": (P_in - P_out) / (CO * sp.Rational(1000, 60))}
