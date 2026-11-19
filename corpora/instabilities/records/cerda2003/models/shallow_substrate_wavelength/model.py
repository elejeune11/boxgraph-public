# lambda ~ (t Hs)^(1/2) (E/Es)^(1/6), printed with "~" and no prefactor; evaluated with prefactor 1,
# as the paper does (lambda ≈ Hs for E/Es ~ 10^3, Hs/t ~ 10). The paper gives Hs as half the pinched
# fold 2Hs and t through Hs/t, so those are the inputs. Lengths in mm.


def run(inputs, settings):
    Hs = inputs["two_Hs"] / 2.0
    t = Hs / inputs["Hs_over_t"]
    lam = (t * Hs) ** 0.5 * inputs["E_over_Es"] ** (1.0 / 6.0)
    return {"lam": lam, "lam_over_Hs": lam / Hs}


def symbolic():
    import sympy as sp
    two_Hs, Hs_over_t, E_over_Es = sp.symbols("two_Hs Hs_over_t E_over_Es", positive=True)
    Hs = two_Hs / 2
    lam = sp.sqrt(Hs / Hs_over_t * Hs) * E_over_Es ** sp.Rational(1, 6)
    return {"lam": lam, "lam_over_Hs": lam / Hs}
