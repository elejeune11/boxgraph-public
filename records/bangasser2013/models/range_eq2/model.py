# Eq. 2: R = log(pmax/pmin). The base of the log is not printed; it is read as 10 because the paper
# interprets R as "the maximum allowable order of magnitude change in the parameter" (p. 3).
# pmax/pmin = (cmax p0)/(cmin p0) = cmax/cmin.
import math


def run(inputs, settings):
    return {"R": math.log10(inputs["cmax"] / inputs["cmin"])}


def symbolic():
    import sympy as sp
    cmax, cmin = sp.symbols("cmax cmin", positive=True)
    return {"R": sp.log(cmax / cmin, 10)}
