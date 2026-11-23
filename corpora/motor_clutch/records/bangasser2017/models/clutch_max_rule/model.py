# n*c = Nc/10: the rule the Supplementary Fig. 5 legend states for its adhesivity simulations
# ("at 1/10 of the total clutches"); the factor 1/10 is part of the stated rule.


def run(inputs, settings):
    return {"nc_max": inputs["Nc"] / 10.0}


def symbolic():
    import sympy as sp
    Nc = sp.symbols("Nc", positive=True)
    return {"nc_max": Nc / 10}
