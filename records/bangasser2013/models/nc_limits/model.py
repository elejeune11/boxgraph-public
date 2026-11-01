# The stalled and free-flowing limits of the clutch number nc (p. 3): the stalled limit is the nc
# that first gives a minimum F-actin flow (over substrate stiffness) within `fraction` x vu of zero;
# the free-flowing limit is the nc that first gives a minimum flow within `fraction` x vu of vu.
# Built from motor_clutch_ssa; the limits are found by bisection over whole numbers of clutches.
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"bangasser2013_{name}", os.path.join(_HERE, "..", name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mc = _load("motor_clutch_ssa")


def _grid(settings):
    lo, hi = math.log10(settings["ksub_min"]), math.log10(settings["ksub_max"])
    n = int(round((hi - lo) * settings["per_decade"])) + 1
    return [10 ** (lo + (hi - lo) * j / (n - 1)) for j in range(n)]


def _min_flow(inputs, nc, settings):
    sim = {"t_total": settings["t_total"], "seed": settings["seed"]}
    return min(_mc.simulate({**inputs, "nc": nc, "ksub": k}, sim)["v_retro"] for k in _grid(settings))


def run(inputs, settings):
    vu, frac = inputs["vu"], settings["fraction"]
    n0 = int(round(inputs["nc"]))

    def stalled(n):
        return _min_flow(inputs, n, settings) <= frac * vu

    def free(n):
        return _min_flow(inputs, n, settings) >= (1 - frac) * vu

    # stalled limit: smallest n above the base with stalled(n); bracket by doubling, then bisect
    lo, hi = n0, 2 * n0
    while not stalled(hi):
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if stalled(mid):
            hi = mid
        else:
            lo = mid
    nc_stall = hi
    # free-flowing limit: largest n below the base with free(n) (first reached when decreasing)
    lo, hi = 1, n0
    if not free(lo):
        nc_free = 0
    else:
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if free(mid):
                lo = mid
            else:
                hi = mid
        nc_free = lo
    return {"nc_stall": nc_stall, "nc_free": nc_free}
