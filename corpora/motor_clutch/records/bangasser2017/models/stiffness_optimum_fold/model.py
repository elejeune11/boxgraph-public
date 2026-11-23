# Fold shift between the fitted composite optima of the high and low motor-clutch sets (Fig. 1g).


def run(inputs, settings):
    return {"fold": inputs["K_high"] / inputs["K_low"]}


def symbolic():
    import sympy as sp
    K_high, K_low = sp.symbols("K_high K_low", positive=True)
    return {"fold": K_high / K_low}
