"""Four-element windkessel input impedance: (R_c || L) + (R_p || C). Units mmHg*s/ml, ml/mmHg, mmHg*s^2/ml, Hz."""
import cmath
import math


def run(inputs, settings):
    w = 2 * math.pi * inputs["f"]
    zl = 1j * w * inputs["L"]
    z = zl * inputs["Rc"] / (inputs["Rc"] + zl) + inputs["Rp"] / (1 + 1j * w * inputs["Rp"] * inputs["C"])
    return {"mod": abs(z), "phase": math.degrees(cmath.phase(z))}
