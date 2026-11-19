# As printed (SI p. 17). Note: integrating d(eps)/dt = sigma/(2 eta) from eps(0) = 0 gives an extra
# constant -tau inside the bracket; the printed form is kept (question q_strain_constants).
import math


def run(inputs, settings):
    s0, eta, tau, t = inputs["sigma0"], inputs["eta"], inputs["tau"], inputs["t"]
    return {"eps": s0 / (2.0 * eta) * (tau * math.exp(t / tau) - t)}


def symbolic():
    import sympy as sp
    s0, eta, tau, t = sp.symbols("sigma0 eta tau t", positive=True)
    return {"eps": s0 / (2 * eta) * (tau * sp.exp(t / tau) - t)}
