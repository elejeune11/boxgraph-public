def run(inputs, settings):
    v_region = inputs["W"] ** 2 * inputs["H"]  # um^3
    return {"length_density": inputs["L"] / v_region * 1e6,  # 1/um^2 -> 1/mm^2
            "volume_fraction": inputs["V"] / v_region}


def symbolic():
    import sympy as sp
    L, V, W, H = sp.symbols("L V W H", positive=True)
    return {"length_density": L / (W**2 * H) * 10**6, "volume_fraction": V / (W**2 * H)}
