# Locus of the saddle-node points of Fig. 12 over the external load (Eqs. 16-17, Sec. III A).
# With u = (nm0 f~s - F~)/(nc0 F~b), the condition g'(nc0) = 0 reads 1 + (k~off0/k~on) e^u (1 - u) = 0, which
# does not involve the load: its root u* > 1 is the same for every load. Then Nc,min = g(nc0) = nc0 (1 + r e^u*),
# r = k~off0/k~on, so the saddle-node point lies on the line nc0 = Nc,min / (1 + r e^u*) whatever the load.
import math

from scipy.optimize import brentq


def run(inputs, settings):
    r = inputs["koff"] / inputs["kon"]
    u = brentq(lambda u: 1.0 + r * math.exp(u) * (1.0 - u), 1.0 + 1e-12, 700.0, xtol=1e-14)
    return {"nc_bif": inputs["Nc"] / (1.0 + r * math.exp(u))}
