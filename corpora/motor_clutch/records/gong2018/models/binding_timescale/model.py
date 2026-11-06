# tau_b = 1 / ron.  Ports: ron 1/s -> tau_b s.

def run(inputs, settings):
    return {"tau_b": 1.0 / inputs["ron"]}


def symbolic():
    import sympy as sp
    ron = sp.symbols("ron", positive=True)
    return {"tau_b": 1 / ron}
