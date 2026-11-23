# Eq. 1: eps0 = (l' - l)/l, solved for the undeformed length l.


def run(inputs, settings):
    return {"l": inputs["l_def"] / (1.0 + inputs["eps0"])}


def symbolic():
    import sympy as sp
    l_def, eps0 = sp.symbols("l_def eps0", positive=True)
    return {"l": l_def / (1 + eps0)}
