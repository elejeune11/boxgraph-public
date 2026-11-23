# Eq. 6 / (nc kc): nc Fb kon / (vu nc kc) = tau / omega and kon nc Fb / (koff nm Fm) = tau / F.


def run(inputs, settings):
    i = inputs
    return {"Kopt": i["C2"] * i["tau"] / i["omega"] / (1 - i["C3"] * i["tau"] / i["F"])}


def symbolic():
    import sympy as sp
    C2, C3, tau, omega, F = sp.symbols("C2 C3 tau omega F", positive=True)
    return {"Kopt": C2 * tau / omega / (1 - C3 * tau / F)}
