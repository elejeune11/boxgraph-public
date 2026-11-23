# Mean-field motor-clutch model, Eqs. 3-4 (dimensionless):
#   dP/dt = tau (1 - n_b) delta(x) - e^{F|x|} P - v_e dP/dx
#   v_e   = [ (omega K / F)(1 - l_b) + int x e^{F|x|} P dx ] / (K + n_b)
#   n_b = int P dx,  l_b = int x P dx,  T* = F l_b.
# All bound clutches stretch at the same rate v_e, so the density is carried rigidly: a clutch
# bound when the actin had moved X(s) relative to the substrate has extension X(t) - X(s). The
# solver follows cohorts of clutches by their binding position (method of characteristics):
# binding adds weight tau (1 - n_b) dt to the newest cohort (a new cohort once X has moved h/F
# past the last one), each cohort decays exactly over a step by exp(-e^{F|x|} dt) at its
# mid-step extension, and X advances by v_e dt. The step is the smallest of dt_max,
# cfl/(F |v_e|) (extension changes by at most cfl/F; v_e of the previous step) and 0.1/lambda,
# lambda = n_b omega K/(F (K + n_b)) the relaxation rate of l_b, but at least dt_min: in a
# failure avalanche the remaining clutches break within one such step. The unbinding integral
# in v_e is averaged over the step (see below). `step` scales h, cfl and dt_max together;
# coarser settings than the defaults were found not converged (Fig. 1(B), F = 1). The paper solves the same equations by finite differences
# (SI p. 46-47); this is a different discretisation of the same model (see questions).
# T* and n_b are averaged over [avg_from t_end, t_end], t_end = max(t_end_min,
# load_times (1 + F/(K omega))), F/(K omega) being the time to load the substrate to stall at
# the free actin speed (S18 in these units).
import numpy as np


def _solve(F, tau, om, K, settings):
    step = float(settings.get("step", 1.0))      # scales h, cfl and dt_max together (refinement)
    h = float(settings.get("h", 0.00125)) * step
    cfl = float(settings.get("cfl", 0.003)) * step
    dt_max = float(settings.get("dt_max", 0.0006)) * step
    dt_min = float(settings.get("dt_min", 1e-6))
    w_min = float(settings.get("w_min", 1e-12))
    t_end = max(float(settings.get("t_end_min", 20.0)),
                float(settings.get("load_times", 20.0)) * (1.0 + F / (K * om)))
    t_avg = float(settings.get("avg_from", 0.25)) * t_end
    cap = 4096
    xb = np.zeros(cap)
    w = np.zeros(cap)
    n = 0
    X = t = 0.0
    accT = accN = tacc = 0.0
    hx = h / F
    steps = 0
    ve_prev = om / F
    while t < t_end:
        xs = X - xb[:n]
        ws = w[:n]
        nb = float(ws.sum())
        wx = ws * xs
        lb = float(wx.sum())
        lam = nb * om * K / (F * (K + nb))
        dt = max(min(dt_max, cfl / (F * abs(ve_prev) + 1e-300), 0.1 / (lam + 1e-300)), dt_min)
        dt = min(dt, t_end - t)
        # int x e^{F|x|} P dx, averaged over the step at fixed x: sum w x (1 - e^{-r dt}) / dt.
        # It equals the instantaneous integral for small r dt and stays bounded by l_b/dt when
        # clutches far out break within the step (the avalanche).
        r = np.exp(np.minimum(F * np.abs(xs), 700.0))
        J = float((wx * -np.expm1(-r * dt)).sum()) / dt
        ve = ((om * K / F) * (1.0 - lb) + J) / (K + nb)
        ve_prev = ve
        if t >= t_avg:
            accT += F * lb * dt
            accN += nb * dt
            tacc += dt
        Xn = X + ve * dt
        xm = Xn - 0.5 * ve * dt - xb[:n]
        ws *= np.exp(-np.exp(np.minimum(F * np.abs(xm), 700.0)) * dt)
        X = Xn
        bind = tau * (1.0 - nb) * dt
        if n and abs(X - xb[n - 1]) < hx:
            w[n - 1] += bind
        else:
            if n == cap:
                cap *= 2
                xb = np.resize(xb, cap)
                w = np.resize(w, cap)
            xb[n] = X
            w[n] = bind
            n += 1
        steps += 1
        if steps % 50 == 0:
            keep = w[:n] > w_min
            m = int(keep.sum())
            if m < n:
                xb[:m] = xb[:n][keep]
                w[:m] = w[:n][keep]
                n = m
        t += dt
    return accT / tacc, accN / tacc


def run(inputs, settings):
    T, nb = _solve(inputs["F"], inputs["tau"], inputs["omega"], inputs["K"], settings)
    return {"T": T, "nb": nb}
