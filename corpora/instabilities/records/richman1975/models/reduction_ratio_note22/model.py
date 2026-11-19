def run(inputs, settings):
    return {"t_ratio": inputs["t_new"] / inputs["t_old"], "l_ratio": inputs["l_new"] / inputs["l_old"]}


def symbolic():
    import sympy as sp
    tn, to, ln, lo = sp.symbols("t_new t_old l_new l_old", positive=True)
    return {"t_ratio": tn / to, "l_ratio": ln / lo}
