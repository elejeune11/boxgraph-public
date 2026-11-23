# Eq. 1: eps0 = (l' - l)/l, solved for the deformed length l'.


def run(inputs, settings):
    return {"l_def": inputs["l"] * (1.0 + inputs["eps0"])}


def symbolic():
    import sympy as sp
    l, eps0 = sp.symbols("l eps0", positive=True)
    return {"l_def": l * (1 + eps0)}
