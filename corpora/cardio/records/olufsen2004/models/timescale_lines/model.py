import math


def run(inputs, settings):
    # the same arithmetic as timescales_first_order and timescales_second_order; R does not enter
    b1, b2 = inputs["beta1"], inputs["beta2"]
    a2 = (1 / (b1**2 * b2**2)) * (1 - 32 * (1 / b1**4 + 1 / b2**4))
    a1 = (1 / b1**2 + 1 / b2**2) - 32 * (1 / b1**6 + 1 / b2**6)
    disc = math.sqrt(a1**2 - 4 * a2)
    return {"lambda_q1": 1 / b1**2, "lambda_q2": 1 / b2**2,
            "lambda_p": (1 - 32 / b1**4) / b1**2,
            "lambda_p1": (a1 + disc) / 2, "lambda_p2": (a1 - disc) / 2}
