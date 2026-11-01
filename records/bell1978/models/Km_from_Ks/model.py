def run(inputs, settings):
    # Ks in nm^3 per molecule; 3Ks/4RAB in nm^2 per molecule; nm^2 -> um^2 is 1e-6
    return {"Km": 3 * inputs["Ks"] / (4 * inputs["RAB"]) * 1e-6}


def symbolic():
    import sympy as sp
    Ks, RAB = sp.symbols("Ks RAB", positive=True)
    return {"Km": 3 * Ks / (4 * RAB) * sp.Rational(1, 10**6)}
