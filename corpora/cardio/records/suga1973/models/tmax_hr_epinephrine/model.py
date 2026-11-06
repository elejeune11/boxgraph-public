# Percent shortening of Tmax per 100-beats/min increase in heart rate, per nonpaced dog, then mean ± SD.
# Per dog: 100 * (Tc - Te)/Tc / ((HRe - HRc)/100), Tc, Te in ms, HR in beats/min (made from the words of p. 7).
import math

DOGS = [1, 2, 4, 5, 6, 8]


def run(inputs, settings):
    r = []
    for k in DOGS:
        tc, te = inputs[f"Tc{k}"], inputs[f"Te{k}"]
        hc, he = inputs[f"HRc{k}"], inputs[f"HRe{k}"]
        r.append(100.0 * (tc - te) / tc / ((he - hc) / 100.0))
    n = len(r)
    m = sum(r) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in r) / (n - inputs["ddof"]))
    return {"mean": m, "sd": sd}
