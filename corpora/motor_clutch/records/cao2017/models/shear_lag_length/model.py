# Lc = (1/phi) * S with S = sqrt((1/kc)/(1/ks + 1/kp)) fixed; S = Lc_ref * phi_ref.


def run(inputs, settings):
    return {"Lc": inputs["Lc_ref"] * inputs["phi_ref"] / inputs["phi"]}


def symbolic():
    import sympy as sp
    Lc_ref, phi_ref, phi = sp.symbols("Lc_ref phi_ref phi", positive=True)
    return {"Lc": Lc_ref * phi_ref / phi}
