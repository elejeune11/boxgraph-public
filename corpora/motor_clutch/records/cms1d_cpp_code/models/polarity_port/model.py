# Port of Cell1DPublish.cpp line 474.


def run(inputs, settings):
    return {"psi": (inputs["Polar"] + 1.0) / 2.0}


def symbolic():
    import sympy as sp
    Polar = sp.symbols("Polar")
    return {"psi": (Polar + 1) / 2}
