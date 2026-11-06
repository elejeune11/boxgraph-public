# Table I footnote (p. 6): CFL = lambda dt / Omega_e with lambda = max |U + c|. SI units.


def run(inputs, settings):
    lam = abs(inputs["U"] + inputs["c"])
    return {"CFL": lam * inputs["dt"] / inputs["dx"]}


def symbolic():
    import sympy as sp
    c, U, dt, dx = sp.symbols("c U dt dx", positive=True)
    return {"CFL": (U + c) * dt / dx}
