# The function k(eta) of Eq. (71). Removable singularities at eta = 0 and eta = +-1 (where
# (1 - eta^2)^2 tanh^-1(eta) -> 0): there the value is the limit. 60-digit arithmetic.
import mpmath as mp


def _k(e):
    return -(e * (4 * e**6 - 11 * e**4 + 10 * e**2 - 6) + 6 * (1 - e**2) ** 2 * mp.atanh(e)) / (
        e**5 * (3 - 2 * e**2))


def k_of(eta):
    with mp.workdps(60):
        e = mp.mpf(eta)
        if e == 0:
            return mp.limit(_k, 0)
        if abs(e) == 1:  # (1 - eta^2)^2 tanh^-1(eta) -> 0 as |eta| -> 1: only the polynomial part is left
            return -(e * (4 * e**6 - 11 * e**4 + 10 * e**2 - 6)) / (e**5 * (3 - 2 * e**2))
        return _k(e)


def run(inputs, settings):
    eta = inputs["eta"]
    if not -1 <= eta <= 1:
        return {"k": None}
    return {"k": float(k_of(eta))}
