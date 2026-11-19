# sigma_a = chi_2D * epsilon_a, with epsilon_a = (A_i - A_0)/A_0 (main text, p. 4).
# theta only places the value on the cross-section (inside the midline band); it does not enter.


def run(inputs, settings):
    return {"sigma_a": inputs["chi"] * inputs["eps"]}


def symbolic():
    import sympy as sp
    chi, eps = sp.symbols("chi eps", positive=True)
    return {"sigma_a": chi * eps}
