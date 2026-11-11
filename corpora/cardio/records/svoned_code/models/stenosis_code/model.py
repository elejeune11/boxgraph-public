# Port of the release's stenosis loss (Code/Source/cvOneDMthSegmentModel.cxx, lines 160-185, case
# MinorLossScope::STENOSIS), line by line, for steady flow Q through an upstream segment of area S0 into
# a stenosed segment of area S1 and length L. The code writes the loss as a friction coefficient N over
# the stenosed segment (lines 183-184); for steady flow the pressure loss it imposes is its "func"
# (line 182) times rho U0^2, U0 = Q/S0. Our code.
import math


def run(inputs, settings):
    S = [inputs["S0"], inputs["S1"]]
    Q = [inputs["Q"], inputs["Q"]]
    kinViscosity0 = inputs["nu"]
    L = inputs["L"]
    q = Q[1] / Q[0]                                          # line 161
    a = S[1] / S[0]                                          # line 163
    Kt = 1.52                                                # line 174
    D = [math.sqrt(4 * S[0] / 3.14159265358979323846),       # line 176
         math.sqrt(4 * S[1] / 3.14159265358979323846)]       # line 177
    La = 0.83 * L + 1.64 * D[1]                              # line 178 (line 179, "La = L", is commented out)
    Kv = 32. * La / D[0] * 1.0 / a * 1.0 / a                 # line 180
    Re0 = D[0] * Q[0] / (S[0] * kinViscosity0)               # line 181
    func = Kv / Re0 + Kt / 2. * (1.0 / a - 1.) * (1.0 / a - 1.)   # line 182
    U0 = Q[0] / S[0]
    assert q == 1.0  # steady flow: the same flow in both segments
    return {"dp": func * inputs["rho"] * U0 * U0, "Kv": Kv, "La": La}
