def run(inputs, settings):
    return {"nmotor_module": inputs["f"] * inputs["nmotor"]}


def symbolic():
    import sympy as sp
    f, nmotor = sp.symbols("f nmotor", positive=True)
    return {"nmotor_module": f * nmotor}
