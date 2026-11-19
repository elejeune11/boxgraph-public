# Eq. 4.7 with xibar_2 = 0 (p. 105): D xi1 - b112^2 xi1^3/(4 D) = c s, s = lambda_W^2 xibar_1,
# xi2 = -b112 xi1^2/(4 D). For D above the limit point lambda* - lambda_W the cubic has two roots
# of the sign of s (the two arms of the fold in Fig. 2) and one of the other sign; the two arms
# are returned. Below the limit point the arms do not exist and the model raises.
import numpy as np


def run(inputs, settings):
    b, c, s, D = inputs["b112"], inputs["c"], inputs["s"], inputs["D"]
    sign = 1.0 if s >= 0 else -1.0
    roots = np.roots([-b * b / (4.0 * D), 0.0, D, -c * abs(s)])
    pos = sorted(float(r.real) for r in roots if abs(r.imag) < 1e-12 and r.real > 0)
    if len(pos) < 2:
        raise ValueError("lambda - lambda_W is below the limit point: the imperfect arms do not exist")
    inner, outer = sign * pos[0], sign * pos[-1]
    return {"xi1_outer": outer, "xi1_inner": inner,
            "xi2_outer": -b * outer ** 2 / (4.0 * D), "xi2_inner": -b * inner ** 2 / (4.0 * D)}
