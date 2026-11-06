# The paper's claim in words (Abstract, p. 1; Results, p. 5): maximal traction and the switch from an
# inverse to a direct stress-speed relationship occur at one F-actin speed, Vc. Units: nm/s in and out.


def run(inputs, settings):
    return {"v_peak": inputs["v_c"]}


def symbolic():
    import sympy as sp
    v_c = sp.symbols("v_c", positive=True)
    return {"v_peak": v_c}
