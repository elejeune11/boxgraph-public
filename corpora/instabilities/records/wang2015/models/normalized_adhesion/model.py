def run(inputs, settings):
    return {"G": inputs["Gamma"] / (inputs["mu_s"] * inputs["Hf"])}


def symbolic():
    import sympy as sp
    Gamma, mu_s, Hf = sp.symbols("Gamma mu_s Hf", positive=True)
    return {"G": Gamma / (mu_s * Hf)}
