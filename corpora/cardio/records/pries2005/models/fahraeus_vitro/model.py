# Eq. 12 of the paper, as printed. D in micrometres, HD as a fraction.
import math


def ratio(D, HD):
    return HD + (1.0 - HD) * (1.0 + 1.7 * math.exp(-0.415 * D) - 0.6 * math.exp(-0.011 * D))


def run(inputs, settings):
    return {"ratio": ratio(inputs["D"], inputs["HD"])}
