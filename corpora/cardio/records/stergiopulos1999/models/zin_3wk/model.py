"""Three-element windkessel input impedance: R_c + (R_p || C). Units mmHg*s/ml, ml/mmHg, Hz."""
import cmath
import math


def run(inputs, settings):
    w = 2 * math.pi * inputs["f"]
    z = inputs["Rc"] + inputs["Rp"] / (1 + 1j * w * inputs["Rp"] * inputs["C"])
    return {"mod": abs(z), "phase": math.degrees(cmath.phase(z))}
