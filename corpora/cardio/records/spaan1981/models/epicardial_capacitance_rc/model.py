def run(inputs, settings):
    return {"Cep": inputs["tau"] / inputs["Ra"]}


def symbolic():
    import sympy as sp
    tau, Ra = sp.symbols("tau Ra", positive=True)
    return {"Cep": tau / Ra}
