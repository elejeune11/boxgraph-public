"""Stress-free dimensions of the chick simulation (SM p. 14), as printed, in units of D, pi D and L.

The paper maps t = 0 to E7 and t = 1 to E14; t is taken linear in embryonic day between them
(the paper says D grows linearly in t but not how t maps to days in between)."""


def run(inputs, settings):
    t = (inputs["day"] - inputs["day_start"]) / (inputs["day_end"] - inputs["day_start"])
    he = 0.13 - 0.1 * t
    we = 0.35 + 2.8 * t - 1.4 * t ** 2
    le = 1 + 0.5 * t ** 2
    hm = 0.39 - 0.3 * t
    wm = 1.5
    lm = 1 + 0.333 * t ** 2
    return {"thickness_ratio": (he + hm) / he, "r_circ_m": 1 / wm, "r_long_m": 1 / lm,
            "r_circ_e": 1 / we, "r_long_e": 1 / le}
