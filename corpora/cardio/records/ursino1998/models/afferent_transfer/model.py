# Eq. 30 in the frequency domain: H(jw) = (1 + j w tau_z) / (1 + j w tau_p). Its static gain is 1,
# so the modulus needs no further normalization. Ports: s, Hz, degree.
import math


def run(inputs, settings):
    w = 2.0 * math.pi * inputs["f"]
    num = complex(1.0, w * inputs["tau_z"])
    den = complex(1.0, w * inputs["tau_p"])
    h = num / den
    return {"modulus": abs(h), "phase": math.degrees(math.atan2(h.imag, h.real))}


def symbolic():
    import sympy as sp
    tz, tp, f = sp.symbols("tau_z tau_p f", positive=True)
    w = 2 * sp.pi * f
    return {"modulus": sp.sqrt((1 + (w * tz) ** 2) / (1 + (w * tp) ** 2)),
            "phase": (sp.atan(w * tz) - sp.atan(w * tp)) * 180 / sp.pi}
