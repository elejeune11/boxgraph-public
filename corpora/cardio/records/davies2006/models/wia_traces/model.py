# Wave intensity analysis of one digitized pressure and velocity trace, as the paper states it (p. 4):
# single-point wave speed c = (1/rho) sqrt(sum dP^2 / sum dU^2) (ref. 19), dP+- = (dP +- rho c dU)/2,
# WI+ = (1/(4 rho c)) (dP/dt + rho c dU/dt)^2, WI- = -(1/(4 rho c)) (dP/dt - rho c dU/dt)^2.
# Units: P in Pa, U in m/s, every curve axis in ms; WI in W m^-2 s^-2.
#
# Numerical steps the paper does not give are settings:
#   step_ms        the sampling interval the traces are taken at (the digitized grid is subsampled, or
#                  linearly interpolated, onto t0, t0 + step, ...); 10 ms is the reading grid of Figs. 3, 5
#   sg_window_ms   Savitzky-Golay window applied to P and U before differencing (0: no filtering)
#   sg_order       its polynomial order
#   peak_halfwidth_ms  half-width of the window around a digitized extremum in which the computed
#                  extremum is searched
# Derivatives are differences of successive samples divided by the step, placed at the mid-times; the
# computed WI curves are resampled linearly onto the x values of the digitized WI traces (curve inputs
# xp and xm, used for their x only).
import math


def _grid(x, y, step):
    t0, t1 = x[0], x[-1]
    n = int(math.floor((t1 - t0) / step + 1e-9))
    ts = [t0 + k * step for k in range(n + 1)]
    return ts, [_interp(t, x, y) for t in ts]


def _interp(t, x, y):
    if t <= x[0]:
        return y[0]
    if t >= x[-1]:
        return y[-1]
    lo, hi = 0, len(x) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if x[mid] <= t:
            lo = mid
        else:
            hi = mid
    if x[hi] == x[lo]:
        return y[lo]
    w = (t - x[lo]) / (x[hi] - x[lo])
    return y[lo] + w * (y[hi] - y[lo])


def _savgol(y, window, order):
    """Savitzky-Golay smoothing (least-squares polynomial of `order` over `window` samples, odd)."""
    if window <= order + 1 or window < 3:
        return list(y)
    import numpy as np
    from scipy.signal import savgol_filter

    return [float(v) for v in savgol_filter(np.asarray(y, float), window, order, mode="interp")]


def _extremum(tm, w, t, half, sign):
    best = None
    for a, b in zip(tm, w):
        if abs(a - t) <= half + 1e-9 and (best is None or sign * b > sign * best):
            best = b
    return best


def run(inputs, settings):
    step = float(settings["step_ms"])
    xP, yP = inputs["P"]["x"], inputs["P"]["y"]
    xU, yU = inputs["U"]["x"], inputs["U"]["y"]
    rho = inputs["rho"]
    t0, t1 = max(xP[0], xU[0]), min(xP[-1], xU[-1])
    tsP, P = _grid([t0] + [x for x in xP if t0 < x < t1] + [t1],
                   [_interp(t0, xP, yP)] + [y for x, y in zip(xP, yP) if t0 < x < t1] + [_interp(t1, xP, yP)], step)
    _, U = _grid([t0] + [x for x in xU if t0 < x < t1] + [t1],
                 [_interp(t0, xU, yU)] + [y for x, y in zip(xU, yU) if t0 < x < t1] + [_interp(t1, xU, yU)], step)
    win_ms = float(settings.get("sg_window_ms", 0))
    if win_ms > 0:
        n = int(round(win_ms / step))
        n = n if n % 2 == 1 else n + 1
        P = _savgol(P, n, int(settings["sg_order"]))
        U = _savgol(U, n, int(settings["sg_order"]))
    dP = [P[i + 1] - P[i] for i in range(len(P) - 1)]
    dU = [U[i + 1] - U[i] for i in range(len(U) - 1)]
    tm = [(tsP[i] + tsP[i + 1]) / 2 for i in range(len(P) - 1)]
    sdP2, sdU2 = sum(d * d for d in dP), sum(d * d for d in dU)
    c = math.sqrt(sdP2 / sdU2) / rho
    dt = step / 1000.0
    wp = [(a / dt + rho * c * b / dt) ** 2 / (4 * rho * c) for a, b in zip(dP, dU)]
    wm = [-((a / dt - rho * c * b / dt) ** 2) / (4 * rho * c) for a, b in zip(dP, dU)]
    # separated pressures and velocities, accumulated from the first sample (P+- and U+- start at 0)
    Pp, Pm, Up, Um = [0.0], [0.0], [0.0], [0.0]
    for a, b in zip(dP, dU):
        dpp, dpm = (a + rho * c * b) / 2, (a - rho * c * b) / 2
        Pp.append(Pp[-1] + dpp)
        Pm.append(Pm[-1] + dpm)
        Up.append(Up[-1] + dpp / (rho * c))
        Um.append(Um[-1] - dpm / (rho * c))
    xp, xm = inputs["xp"]["x"], inputs["xm"]["x"]
    half = float(settings["peak_halfwidth_ms"])
    pp, pm = inputs["pp"]["x"], inputs["pm"]["x"]
    return {
        "c": c,
        "sum_dP2": sdP2,
        "sum_dU2": sdU2,
        "WIp": {"x": list(xp), "y": [_interp(t, tm, wp) for t in xp]},
        "WIm": {"x": list(xm), "y": [_interp(t, tm, wm) for t in xm]},
        "WIp_peaks": {"x": list(pp), "y": [_extremum(tm, wp, t, half, +1) for t in pp]},
        "WIm_peaks": {"x": list(pm), "y": [_extremum(tm, wm, t, half, -1) for t in pm]},
        "WIp_max": max(wp),
        "WIm_min": min(wm),
        "Pp": {"x": tsP, "y": Pp},
        "Pm": {"x": tsP, "y": Pm},
        "Up": {"x": tsP, "y": Up},
        "Um": {"x": tsP, "y": Um},
    }
