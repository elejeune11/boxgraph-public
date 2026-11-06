# Left ventricular and left atrial elastance over time (Eqs. 2-2, 2-3, 2-5, 2-6 as printed),
# as plotted in Figs. 2-6 and 2-13. Port units: mmHg/ml, s. No I/O.
import math


def run(inputs, settings):
    T, Ts1, Ts2 = inputs["T"], inputs["Ts1"], inputs["Ts2"]
    Tpb, Tpw = inputs["Tpwb"], inputs["Tpww"]
    tc = inputs["t"] % T
    # Eq. 2-3
    if tc < Ts1:
        ev = 1.0 - math.cos(tc / Ts1 * math.pi)
    elif tc < Ts2:
        ev = 1.0 + math.cos((tc - Ts1) / (Ts2 - Ts1) * math.pi)
    else:
        ev = 0.0
    # Eq. 2-6
    if tc < Tpb + Tpw - T:
        ea = 1.0 - math.cos((tc - Tpb + T) / Tpw * 2.0 * math.pi)
    elif tc < Tpb:
        ea = 0.0
    else:
        ea = 1.0 - math.cos((tc - Tpb) / Tpw * 2.0 * math.pi)
    elv = inputs["Elvd"] + (inputs["Elvs"] - inputs["Elvd"]) / 2.0 * ev        # Eq. 2-2
    ela = inputs["Ela_min"] + (inputs["Ela_max"] - inputs["Ela_min"]) / 2.0 * ea  # Eq. 2-5
    return {"elv": elv, "ela": ela}
