# Extremes of |w_i| over the eight inputs (percent). Repeated inputs do not change the extremes.

NAMES = ("w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8")


def run(inputs, settings):
    mags = [abs(inputs[n]) for n in NAMES]
    return {"min_abs": min(mags), "max_abs": max(mags)}
