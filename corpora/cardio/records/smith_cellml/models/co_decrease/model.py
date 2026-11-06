# Relative decrease of cardiac output between two runs, in percent.


def run(inputs, settings):
    return {"decrease": 100.0 * (1.0 - inputs["CO_test"] / inputs["CO_ref"])}


def symbolic():
    import sympy as sp
    CO_ref, CO_test = sp.symbols("CO_ref CO_test", positive=True)
    return {"decrease": 100 * (1 - CO_test / CO_ref)}
