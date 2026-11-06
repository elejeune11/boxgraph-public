import math


def _coefficients(b1, b2):
    # right-hand operator of Eq. 19, without the factor pi/8: a2 p'' + a1 p' + p
    a2 = (1 / (b1**2 * b2**2)) * (1 - 32 * (1 / b1**4 + 1 / b2**4))
    a1 = (1 / b1**2 + 1 / b2**2) - 32 * (1 / b1**6 + 1 / b2**6)
    return a2, a1


def run(inputs, settings):
    b1, b2 = inputs["beta1"], inputs["beta2"]
    a2, a1 = _coefficients(b1, b2)
    # (1 + lp1 D)(1 + lp2 D) = a2 D^2 + a1 D + 1  ->  lp1 lp2 = a2, lp1 + lp2 = a1
    disc = math.sqrt(a1**2 - 4 * a2)
    lp1 = (a1 + disc) / 2
    lp2 = (a1 - disc) / 2
    lq1 = 1 / b1**2
    lq2 = 1 / b2**2
    return {"lambda_q1": lq1, "lambda_q2": lq2, "lambda_p1": lp1, "lambda_p2": lp2,
            "lambda_q_sum": lq1 + lq2, "lambda_p_sum": lp1 + lp2}


def symbolic():
    import sympy as sp
    b1, b2 = sp.symbols("beta1 beta2", positive=True)
    a2, a1 = _coefficients(b1, b2)
    disc = sp.sqrt(a1**2 - 4 * a2)
    return {"lambda_q1": 1 / b1**2, "lambda_q2": 1 / b2**2,
            "lambda_p1": (a1 + disc) / 2, "lambda_p2": (a1 - disc) / 2,
            "lambda_q_sum": 1 / b1**2 + 1 / b2**2, "lambda_p_sum": a1}
