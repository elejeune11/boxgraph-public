# The wrinkling-creasing phase boundary of the initial modes: the modulus ratio mu_f/mu_s at
# which the wrinkling onset strain (linear stability analysis, built_from
# wrinkle_linear_stability) equals the constant crease onset strain. The paper states this in
# words: the initial mode is the one with the lowest critical strain, and the intersections of
# the curves of Fig. 6(a) give the phase boundaries. The root finding (Brent on log mu) is the
# reader's.
import importlib.util
import math
import pathlib

from scipy.optimize import brentq

_path = pathlib.Path(__file__).resolve().parent.parent / "wrinkle_linear_stability" / "model.py"
_spec = importlib.util.spec_from_file_location("wang2014_wrinkle_linear_stability", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    s = _base.settings_of({k: v for k, v in settings.items() if k in _base.DEFAULTS})
    eps_c, lam_p = inputs["eps_crease"], inputs["lam_p"]

    def g(log_mu):
        return _base.solve(math.exp(log_mu), lam_p, s)[0] - eps_c

    x = brentq(g, math.log(settings["mu_lo"]), math.log(settings["mu_hi"]),
               xtol=settings["xtol"], maxiter=int(settings["max_iter"]))
    return {"mu_boundary": math.exp(x)}
