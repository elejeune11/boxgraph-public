# Poiseuille flow in one straight rigid tube. Ports: Pa, um, Pa s; outputs um/s and dyn/cm^2 (1 Pa = 10 dyn/cm^2).


def run(inputs, settings):
    dp = inputs["p_in"] - inputs["p_out"]
    r = inputs["r"] * 1e-6
    L = inputs["L"] * 1e-6
    v = dp * r**2 / (8.0 * inputs["mu"] * L)  # m/s
    tau = dp * r / (2.0 * L)  # Pa
    return {"v_mean": v * 1e6, "tau_w": tau * 10.0}


def symbolic():
    import sympy as sp
    p_in, p_out, r, mu, L = sp.symbols("p_in p_out r mu L", positive=True)
    dp = p_in - p_out
    return {"v_mean": dp * (r * sp.Rational(1, 10**6)) ** 2 / (8 * mu * L * sp.Rational(1, 10**6)) * 10**6,
            "tau_w": dp * r / (2 * L) * 10}
