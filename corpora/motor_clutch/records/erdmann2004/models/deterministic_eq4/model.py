import math

from scipy.integrate import solve_ivp


def run(inputs, settings):
    # Integrated in u = ln N, which stays smooth until N collapses to 0 in finite time.
    n0, g = inputs["N0"], inputs["gamma"]
    f = inputs["f_over_N0"] * n0

    def rhs(_, u):
        n = math.exp(u[0])
        return [-math.exp(f / n) + g * (n0 - n) / n]

    rtol = settings.get("rtol", 1e-10)
    sol = solve_ivp(rhs, (0.0, inputs["tau"]), [math.log(n0)], method="LSODA", rtol=rtol, atol=rtol)
    if sol.status != 0:
        return {"N": 0.0}
    return {"N": math.exp(sol.y[0, -1])}
