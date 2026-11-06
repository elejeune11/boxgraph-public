# p. 27: wavelengths "can be approximated by multiplying the period of the systolic part of the inflow
# wave (Ts) with the pulse wave speed at mean pressure (cm)"; p. 15 does the same with c0 T.


def run(inputs, settings):
    return {"lam": inputs["c"] * inputs["T"]}


def symbolic():
    import sympy as sp
    c, T = sp.symbols("c T", positive=True)
    return {"lam": c * T}
