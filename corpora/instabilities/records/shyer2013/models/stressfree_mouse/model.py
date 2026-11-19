"""Stress-free dimensions of the mouse simulation (SM p. 14), as printed, in units of D, pi D and L.

The paper maps t = 0 to E12.5 and t = 1 to E15.5; t is taken linear in embryonic day between them."""


def run(inputs, settings):
    t = (inputs["day"] - inputs["day_start"]) / (inputs["day_end"] - inputs["day_start"])
    he = 0.2 - 0.1 * t
    we = 0.5 + 2 * t - t ** 2
    le = 1.6 + 1.2 * t - 0.6 * t ** 2
    hm = 0.2666 - 0.0666 * t
    wm = 1.5
    lm = 1.4 + 0.8 * t - 0.4 * t ** 2
    return {"thickness_ratio": (he + hm) / he, "r_circ_m": 1 / wm, "r_long_m": 1 / lm,
            "r_circ_e": 1 / we, "r_long_e": 1 / le}
