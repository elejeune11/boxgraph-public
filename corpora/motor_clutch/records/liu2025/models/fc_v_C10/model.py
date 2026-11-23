"""Traction per site Fc/Nc for slip bonds and linear springs, Supplementary Eq. (C10):
Fc = Nc/(beta xt) * phi/(1 + phi) * a G^{3,0}_{2,3}(a | 0,0 ; -1,-1,-1) / E1(a),
a = k0off/(beta k v xt), phi = a e^{eps + a} E1(a), eps = ln(kon/k0off), beta = 1/kT.
The Meijer G-function as in Fig. S6: meijerG([], [0, 0], [-1, -1, -1], [], a)."""
import mpmath as mp


def run(inputs, settings):
    kT, xt, k, v = inputs["kT"], inputs["xt"], inputs["k"], inputs["v"]
    kon, k0 = inputs["kon"], inputs["k0off"]
    beta = 1.0 / kT
    a = mp.mpf(k0) / (beta * k * v * xt)
    E1 = mp.e1(a)
    phi = a * mp.e ** (mp.log(mp.mpf(kon) / k0) + a) * E1
    G = mp.meijerg([[], [0, 0]], [[-1, -1, -1], []], a)
    return {"fc": float(1.0 / (beta * xt) * phi / (1 + phi) * a * G / E1)}
