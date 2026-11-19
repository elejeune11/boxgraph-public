# As printed (SI p. 17). Integrating d(eps)/dt = sigma'/(2G) + sigma/(2 eta_ve) with G = eta_ve/tau_r
# from eps(0) = 0 gives an extra constant -(tau + tau_r) in the bracket; the printed form is kept.
import math


def run(inputs, settings):
    s0, eta, tau, tr, t = inputs["sigma0"], inputs["eta_ve"], inputs["tau"], inputs["tau_r"], inputs["t"]
    return {"eps": s0 / (2.0 * eta) * ((tau + tr) * math.exp(t / tau) - t)}


def symbolic():
    import sympy as sp
    s0, eta, tau, tr, t = sp.symbols("sigma0 eta_ve tau tau_r t", positive=True)
    return {"eps": s0 / (2 * eta) * ((tau + tr) * sp.exp(t / tau) - t)}
