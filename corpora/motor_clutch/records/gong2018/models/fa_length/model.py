# r = 2R.  Ports: R um -> r um.

def run(inputs, settings):
    return {"r": 2.0 * inputs["R"]}


def symbolic():
    import sympy as sp
    R = sp.symbols("R", positive=True)
    return {"r": 2 * R}
