# The lesion is the territory of one capillary bundle: its axes equal the bundle's.


def run(inputs, settings):
    return {"n_major": inputs["a_major"], "n_minor": inputs["a_minor"]}


def symbolic():
    import sympy as sp

    a_major, a_minor = sp.symbols("a_major a_minor", positive=True)
    return {"n_major": a_major, "n_minor": a_minor}
