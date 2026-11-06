# The logit relation (p. 4) with Eqs. 4-6 (p. 5) as printed; diameters in um.
# X0 is "the minimal fractional blood flow required to draw red blood cells into the daughter
# branch": below X0 the branch gets no red cells (FQE = 0), above 1 - X0 it gets all (FQE = 1).
import math


def run(inputs, settings):
    FQB, DF, Da, Db, HD = inputs["FQB"], inputs["DF"], inputs["Dalpha"], inputs["Dbeta"], inputs["HD"]
    A = -6.96 * math.log(Da / Db) / DF
    B = 1 + 6.98 * (1 - HD) / DF
    X0 = 0.4 / DF
    if FQB <= X0:
        return {"FQE": 0.0}
    if FQB >= 1 - X0:
        return {"FQE": 1.0}
    x = (FQB - X0) / (1 - 2 * X0)
    z = A + B * math.log(x / (1 - x))
    return {"FQE": 1 / (1 + math.exp(-z))}
