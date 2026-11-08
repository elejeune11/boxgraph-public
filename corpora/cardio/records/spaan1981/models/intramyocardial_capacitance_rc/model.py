def run(inputs, settings):
    return {"Cim": inputs["tau"] / inputs["Rv"]}


def symbolic():
    import sympy as sp
    tau, Rv = sp.symbols("tau Rv", positive=True)
    return {"Cim": tau / Rv}
