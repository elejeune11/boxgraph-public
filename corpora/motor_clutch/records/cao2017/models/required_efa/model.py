# Invert Eq. S2: sigma = c / (1/Keff + d) with c = beta rho0/(K beta - 1), d = (beta - alpha)/(K beta - 1),
# so 1/Keff = c/sigma - d, then 1/E*FA = 1/Keff - 1/En. Stresses in kPa, alpha and beta per Pa (x 1000 per kPa).
# A required modulus that is not positive (sigma* out of reach) is returned as NaN.


def run(inputs, settings):
    a, b = inputs["alpha"] * 1e3, inputs["beta"] * 1e3
    K, rho0, En, s = inputs["K"], inputs["rho0"], inputs["En"], inputs["sigma_star"]
    g = K * b - 1.0
    c, d = b * rho0 / g, (b - a) / g
    inv_efa = c / s - d - 1.0 / En
    return {"Efa_req": 1.0 / inv_efa if inv_efa > 0 else float("nan")}


def symbolic():
    import sympy as sp
    sigma_star, En, K, rho0, alpha, beta = sp.symbols("sigma_star En K rho0 alpha beta", positive=True)
    a, b = alpha * 1000, beta * 1000
    g = K * b - 1
    return {"Efa_req": 1 / (b * rho0 / g / sigma_star - (b - a) / g - 1 / En)}
