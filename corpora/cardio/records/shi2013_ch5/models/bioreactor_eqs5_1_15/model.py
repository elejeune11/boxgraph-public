# The pulsatile bioreactor lumped-parameter model of Chapter 5 (Eqs. 5-1 to 5-15), as printed,
# integrated with the classical Runge-Kutta method (the chapter's own solver, p. 11).
#
# State: Pcl, Qcl (lower media chamber, Eqs. 5-1, 5-2), Pct (tissue construct, Eq. 5-5),
# Pcu, Qcu (upper media chamber, Eqs. 5-3, 5-4), Pco (outlet valve tubing, Eq. 5-7),
# l, dl/dt (silicon diaphragm, Eq. 5-13). Algebraic: Qct (Eq. 5-6), Qci with tau_ci (Eqs. 5-8, 5-9),
# Qco with tau_co (Eqs. 5-10, 5-11), Ps (Eq. 5-12), Qs (Eq. 5-14), Pa (Eq. 5-15).
#
# Units: pressures in mmHg, flows in ml/s, R in mmHg*s/ml, C in ml/mmHg, L in mmHg*s^2/ml,
# heights in m, rho in kg/m^3, g in m/s^2 (rho*g*h is converted from Pa to mmHg). Eq. 5-13 is a
# force balance; it is evaluated in newtons: (Ps - Pcl)*As in mmHg*m^2 times 133.322 Pa/mmHg,
# ms in kg, kf in N*s/m, ke in N/m. Qs = As*dl/dt in m^3/s is converted to ml/s.
#
# Numerical choices the chapter does not give (settings): the step dt, the number of 1-period
# cycles simulated from rest (n_cycles; the chapter says the solution converges after about ten
# cycles), and the initial state (all zero: diaphragm at rest at l = 0, all pressures and flows 0).
# Results are taken from the last simulated cycle.
import math

MMHG = 133.322387415  # Pa per mmHg

_MEMO = {}

NAMES = ("Pcl", "Qcl", "Pct", "Pcu", "Qcu", "Pco", "l", "u", "Ps", "Qci", "Qco", "Qs", "Qct")


def simulate(p, settings):
    """Integrate from rest over n_cycles periods; return (t0, record step, rows) for the last
    cycle, rows holding NAMES at every `record_stride`-th step from t0 = (n_cycles - 1) * T."""
    dt = float(settings["dt"])
    T = p["T"]
    n_cyc = int(settings["n_cycles"])
    stride = int(settings.get("record_stride", 1))
    Rcu, Ccu, Lcu, hcu = p["Rcu"], p["Ccu"], p["Lcu"], p["hcu"]
    Rct, Cct = p["Rct"], p["Cct"]
    Rcl, Ccl, Lcl, hcl = p["Rcl"], p["Ccl"], p["Lcl"], p["hcl"]
    ms, As, kf, ke, hs = p["ms"], p["As"], p["kf"], p["ke"], p["hs"]
    Ps0, Psa = p["Ps0"], p["Psa"]
    CQci, CQco, Cco = p["CQci"], p["CQco"], p["Cco"]
    rg = p["rho"] * p["g"] / MMHG  # mmHg per m of media column
    Pa = p["Patm"] + rg * p["ha"]  # Eq. 5-15
    Pin = Pa - rg * hs  # reservoir pressure at the inlet valve, Eqs. 5-8, 5-9
    Pout = Pa - rg * (hcl + hcu + hs)  # reservoir pressure at the outlet valve, Eqs. 5-10, 5-11
    ghcl, ghcu = rg * hcl, rg * hcu
    AF = As * MMHG  # N per mmHg of pressure difference across the diaphragm
    AQ = As * 1e6  # ml per m of diaphragm travel
    w = 2.0 * math.pi / T

    def f(t, Pcl, Qcl, Pct, Pcu, Qcu, Pco, l, u):
        Ps = Ps0 + Psa * math.sin(w * t)  # Eq. 5-12
        d = Pin - Pcl
        Qci = CQci * math.sqrt(d) if d > 0.0 else 0.0  # Eqs. 5-8, 5-9 (tau = 0 below; Q = 0 at d = 0)
        d = Pco - Pout
        Qco = CQco * math.sqrt(d) if d > 0.0 else 0.0  # Eqs. 5-10, 5-11
        Qs = AQ * u  # Eq. 5-14
        Qct = (Pct - Pcu) / Rct  # Eq. 5-6
        return ((Qci + Qs - Qcl) / Ccl,  # Eq. 5-1
                (Pcl - Pct - ghcl - Rcl * Qcl) / Lcl,  # Eq. 5-2
                (Qcl - Qct) / Cct,  # Eq. 5-5
                (Qct - Qcu) / Ccu,  # Eq. 5-3
                (Pcu - Pco - ghcu - Rcu * Qcu) / Lcu,  # Eq. 5-4
                (Qcu - Qco) / Cco,  # Eq. 5-7
                u,
                ((Ps - Pcl) * AF - kf * u - ke * l) / ms,  # Eq. 5-13
                Ps, Qci, Qco, Qs, Qct)

    y = [0.0] * 8
    n_per = int(round(T / dt))
    n = n_per * n_cyc
    i0 = n_per * (n_cyc - 1)
    rows = []
    h2 = 0.5 * dt
    h6 = dt / 6.0
    for i in range(n + 1):
        t = i * dt
        k1 = f(t, *y)
        if i >= i0 and (i - i0) % stride == 0:
            rows.append((y[0], y[1], y[2], y[3], y[4], y[5], y[6], y[7]) + k1[8:])
        if i == n:
            break
        k2 = f(t + h2, *[a + h2 * b for a, b in zip(y, k1)])
        k3 = f(t + h2, *[a + h2 * b for a, b in zip(y, k2)])
        k4 = f(t + dt, *[a + dt * b for a, b in zip(y, k3)])
        y = [a + h6 * (b + 2.0 * c + 2.0 * e + q) for a, b, c, e, q in zip(y, k1, k2, k3, k4)]
        if not all(math.isfinite(v) and abs(v) < 1e9 for v in y):
            return None
    return i0 * dt, stride * dt, rows


def last_cycle(inputs, settings):
    key = (tuple(sorted((k, v) for k, v in inputs.items() if k != "t")),
           tuple(sorted((k, str(v)) for k, v in settings.items())))
    if key not in _MEMO:
        _MEMO.clear()
        _MEMO[key] = simulate(inputs, settings)
    return _MEMO[key]


def run(inputs, settings):
    res = last_cycle(inputs, settings)
    nan = float("nan")
    keys = ("Pct_max", "Pct_min", "Qct_max", "Qct_min", "l_amp", "l_offset_air")
    if res is None:
        return {k: nan for k in keys}
    _, _, rows = res
    j = {nm: k for k, nm in enumerate(NAMES)}
    pct = [r[j["Pct"]] for r in rows]
    qct = [r[j["Qct"]] for r in rows]
    ll = [r[j["l"]] for r in rows]
    return {"Pct_max": max(pct), "Pct_min": min(pct), "Qct_max": max(qct), "Qct_min": min(qct),
            # oscillation amplitude about the neutral position, and the neutral position's offset
            # towards the air chamber (negative l), as the chapter describes Fig. 5-5(a) (p. 12)
            "l_amp": (max(ll) - min(ll)) / 2.0, "l_offset_air": -(max(ll) + min(ll)) / 2.0}
