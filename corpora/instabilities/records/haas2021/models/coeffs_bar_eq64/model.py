# The closed forms the paper prints for the barred coefficients (second equalities of Eqs. 64a-64d).
import mpmath as mp

OUT = ("ab_ss", "ab_sphi", "bb_ss", "bb_sphi")


def _forms(e):
    q = 1 - e**2
    return {
        "ab_ss": 4 / q**2,
        "ab_sphi": 2 / q**2,
        "bb_ss": -1 / (e * q**2) + mp.atanh(e) / e**2,
        "bb_sphi": -e * (2 - e**2) / (3 * q**2),
    }


def run(inputs, settings):
    eta = inputs["eta"]
    if not -1 < eta < 1:
        return {k: None for k in OUT}
    with mp.workdps(60):
        e = mp.mpf(eta)
        if e == 0:
            return {k: float(mp.limit(lambda x, k=k: _forms(x)[k], 0)) for k in OUT}
        return {k: float(v) for k, v in _forms(e).items()}


def symbolic():
    import sympy as sp
    eta = sp.Symbol("eta", positive=True)
    q = 1 - eta**2
    return {"ab_ss": 4 / q**2, "ab_sphi": 2 / q**2,
            "bb_ss": -1 / (eta * q**2) + sp.atanh(eta) / eta**2,
            "bb_sphi": -eta * (2 - eta**2) / (3 * q**2)}
