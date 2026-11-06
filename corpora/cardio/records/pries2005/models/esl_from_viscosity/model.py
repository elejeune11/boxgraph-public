# The layer thickness W for which eta_vitro (D/(D - 2W))^4 equals eta_vivo (the paper's
# eta_vivo = eta_vitro (D/Deff)^4, with Deff = D - 2W, applied to one vessel).


def run(inputs, settings):
    D = inputs["D"]
    d_eff = D * (inputs["eta_vitro"] / inputs["eta_vivo"]) ** 0.25
    return {"W": (D - d_eff) / 2.0}


def symbolic():
    import sympy as sp
    D, ev, et = sp.symbols("D eta_vivo eta_vitro", positive=True)
    return {"W": (D - D * (et / ev) ** sp.Rational(1, 4)) / 2}
