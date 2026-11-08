# Microvascular pressure as a percentage of the simultaneous aortic pressure, applied to the
# group means of Tables 4 and 5 (the paper averages per-vessel percentages; see questions).


def run(inputs, settings):
    return {
        "pct_s": 100.0 * inputs["Pm_s"] / inputs["Pa_s"],
        "pct_d": 100.0 * inputs["Pm_d"] / inputs["Pa_d"],
        "pct_m": 100.0 * inputs["Pm_m"] / inputs["Pa_m"],
    }


def symbolic():
    import sympy as sp
    Pa_s, Pa_d, Pa_m, Pm_s, Pm_d, Pm_m = sp.symbols("Pa_s Pa_d Pa_m Pm_s Pm_d Pm_m", positive=True)
    return {"pct_s": 100 * Pm_s / Pa_s, "pct_d": 100 * Pm_d / Pa_d, "pct_m": 100 * Pm_m / Pa_m}
