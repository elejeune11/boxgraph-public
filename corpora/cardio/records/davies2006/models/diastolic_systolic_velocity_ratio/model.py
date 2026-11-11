# Diastolic-to-systolic ratio of one subject's Doppler velocity trace, split at an end-systole time ts.
# Systole is the trace from its first point to ts, diastole from ts to its last point (time in ms, U in m/s).
# mean ratio: (time-mean of U over diastole) / (time-mean of U over systole)
# integral ratio: (integral of U over diastole) / (integral of U over systole)
# Trapezoid rule on the trace's own points, with U interpolated linearly at ts.


def _interp(t, x, y):
    for i in range(len(x) - 1):
        if x[i] <= t <= x[i + 1]:
            w = 0.0 if x[i + 1] == x[i] else (t - x[i]) / (x[i + 1] - x[i])
            return y[i] + w * (y[i + 1] - y[i])
    raise ValueError(f"end-systole time {t} ms is outside the trace ({x[0]} to {x[-1]} ms)")


def _integral(x, y):
    return sum((x[i + 1] - x[i]) * (y[i] + y[i + 1]) / 2 for i in range(len(x) - 1))


def run(inputs, settings):
    x, y = inputs["U"]["x"], inputs["U"]["y"]
    ts = inputs["ts"]
    us = _interp(ts, x, y)
    xs = [v for v in x if v < ts] + [ts]
    ys = [b for a, b in zip(x, y) if a < ts] + [us]
    xd = [ts] + [v for v in x if v > ts]
    yd = [us] + [b for a, b in zip(x, y) if a > ts]
    i_s, i_d = _integral(xs, ys), _integral(xd, yd)
    return {"ratio_mean": (i_d / (xd[-1] - xd[0])) / (i_s / (xs[-1] - xs[0])), "ratio_integral": i_d / i_s}
