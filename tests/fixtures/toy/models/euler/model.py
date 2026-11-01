def run(inputs, settings):
    k, dt, T = inputs["k0"], settings["dt"], settings["t_max"]
    s, t, mean = 1.0, 0.0, 0.0
    while t < T:
        mean += s * dt
        s -= k * s * dt
        t += dt
    return {"t": mean}
