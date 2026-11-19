# Port of settings.plot line 9 (siga(x)=chi*(1-x)/x) and of the pre-strain 1/gamma - 1 of time_profile_stress.plot.


def run(inputs, settings):
    g, chi = inputs["gamma"], inputs["chi"]
    return {"eps": 1 / g - 1, "sigma_a": chi * (1 - g) / g}


def symbolic():
    import sympy as sp
    g, chi = sp.symbols("gamma chi", positive=True)
    return {"eps": 1 / g - 1, "sigma_a": chi * (1 - g) / g}
