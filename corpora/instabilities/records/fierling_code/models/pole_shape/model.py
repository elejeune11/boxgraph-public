# Port of the script's constraint 'ellipsoide' (Surface_Evolver_script.txt lines 85-87), evaluated at the poles.


def run(inputs, settings):
    c, gaxe = inputs["c"], inputs["gaxe"]
    rayon = 1.0  # lengths in units of R_DV
    x = gaxe * rayon  # pole: x^2/gaxe^2 = rayon^2, so the squared z term must vanish
    z_pole = -c / gaxe / rayon * x**2 / 2
    return {"z_pole": z_pole / rayon, "Zp": -z_pole / rayon}


def symbolic():
    import sympy as sp
    c, g = sp.symbols("c gaxe", positive=True)
    return {"z_pole": -c * g / 2, "Zp": c * g / 2}
