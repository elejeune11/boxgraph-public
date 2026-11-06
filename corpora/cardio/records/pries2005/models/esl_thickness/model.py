# Eqs. 8-11 of the paper, as printed. Lengths in micrometres.
import math


def components(p):
    D, Doff, Dcrit = p["D"], p["Doff"], p["Dcrit"]
    if D <= Doff:
        return 0.0, 0.0
    was = (D - Doff) / (D + p["D50"] - 2.0 * Doff) * p["Wmax"]
    if D <= Dcrit:
        wpeak = p["Eamp"] * (D - Doff) / (Dcrit - Doff)
    else:
        wpeak = p["Eamp"] * math.exp(-p["Ewidth"] * (D - Dcrit))
    return was, wpeak


def thickness(p):
    was, wpeak = components(p)
    return {"Weff": was + wpeak * (1.0 + p["HD"] * p["EHD"]), "Wph": was + wpeak * p["Epeak"]}


def run(inputs, settings):
    return thickness(inputs)
