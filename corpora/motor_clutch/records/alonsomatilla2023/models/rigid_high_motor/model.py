# High-motor limit on a rigid substrate (S55, S57). With z = 1/omega:
#   Gamma(0, z) = E1(z);  G^{30}_{23}(z | 1,1; 0,0,0) = int_1^oo ln(u) e^{-z u}/u du
#                                                    = e^{-z} int_0^oo s exp(-(e^s - 1) z) ds.
# The Meijer G is evaluated by that integral (mpmath's meijerg agrees; quad is faster).
import math

from scipy.integrate import quad
from scipy.special import exp1


def run(inputs, settings):
    tau, om = inputs["tau"], inputs["omega"]
    z = 1.0 / om
    gam = float(exp1(z))
    smax = math.log(1.0 + 800.0 / z)
    G = math.exp(-z) * quad(lambda s: s * math.exp(-math.expm1(s) * z), 0.0, smax, limit=500)[0]
    q = tau * math.exp(z) * gam
    nb = q / (q + om)
    return {"T": G / gam * nb, "nb": nb}
