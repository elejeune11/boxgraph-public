# Percent comparisons of women's against men's group medians.
def run(inputs, settings):
    def r(k):
        return inputs[k + "_f"] / inputs[k + "_m"]

    return {
        "awc_excess": 100.0 * (r("awc") - 1.0),
        "bsa_pct": 100.0 * r("bsa"),
        "lbm_pct": 100.0 * r("lbm"),
        "vegfa_excess": 100.0 * (r("vegfa") - 1.0),
        "vegfr1_deficit": 100.0 * (1.0 - r("vegfr1")),
        "vratio_deficit": 100.0 * (1.0 - r("vratio")),
    }


def symbolic():
    import sympy as sp
    names = ["awc", "bsa", "lbm", "vegfa", "vegfr1", "vratio"]
    s = {f"{n}_{g}": sp.Symbol(f"{n}_{g}", positive=True) for n in names for g in "mf"}

    def r(k):
        return s[k + "_f"] / s[k + "_m"]

    return {
        "awc_excess": 100 * (r("awc") - 1),
        "bsa_pct": 100 * r("bsa"),
        "lbm_pct": 100 * r("lbm"),
        "vegfa_excess": 100 * (r("vegfa") - 1),
        "vegfr1_deficit": 100 * (1 - r("vegfr1")),
        "vratio_deficit": 100 * (1 - r("vratio")),
    }
