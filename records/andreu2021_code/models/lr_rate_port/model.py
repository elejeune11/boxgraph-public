# Port to Python of Supplementary Software 1 of Andreu et al. 2021, 'loading rate script.m' (lines 10-67)
# with koffcb.m (cases 'mn' and 'cm'). Our code, not the authors': it follows their lines one by one.
# Units as in the MATLAB code: N, N/s, s. No I/O.
import math

import numpy as np


def koffcb(f, ion, c):
    """koffcb.m: integrin off-rate as a function of force (N), in 1/s. Cases 'mn' (lines 25-37) and
    'cm' (lines 39-51); the coefficients come in through `c`."""
    f = np.abs(np.asarray(f, dtype=float))
    with np.errstate(over="ignore"):
        k = c["a"] * np.exp(c["b"] * f) + c["c"] * np.exp(c["d"] * f)
        if ion == "cm":
            g, fend = c["g"], c["fend"]
            h = -math.log(0.1 / g) / fend
            k = k + g * np.exp(-h * f)
    return k


def kunf_slip(f, ln_k0, b, pt):
    """'loading rate script.m' line 28 / cmstretchg.m line 104: exp(-7.573) exp(1.786e12 |F| pt)."""
    with np.errstate(over="ignore"):
        return np.exp(ln_k0) * np.exp(b * np.abs(np.asarray(f, dtype=float)) * pt)


def _cumtrapz(y):
    return np.concatenate([[0.0], np.cumsum((y[1:] + y[:-1]) * 0.5)])


def _tail_trapz(y):
    """trapz(y(i:end)) for every i (unit spacing), 0 for the last element."""
    seg = (y[1:] + y[:-1]) * 0.5
    return np.concatenate([np.cumsum(seg[::-1])[::-1], [0.0]])


def corrected_row(koff, f, Lj, fstart, step, steps, p_floor):
    """Lines 31-57 for one loading rate L(j): the rate ku(j, :) over the starting forces."""
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        pm = np.exp((-1.0 / Lj) * _cumtrapz(koff) * step) * koff / Lj  # line 36
        tail_p = _tail_trapz(pm)
        tail_fp = _tail_trapz(f * pm)
    out = np.empty(len(fstart))
    for i in range(len(fstart)):
        ind = int(round(1 + i * steps / step)) - 1  # line 43, 0-based
        if not pm[ind] >= p_floor:  # line 44 (a NaN density, from inf*0, also takes this branch)
            out[i] = koff[ind]  # line 47
        else:
            # lines 49-53: pi = pm/(trapz(pm) step); fu = trapz(fi pi) step; tu = (fu - fstart)/L
            fu = tail_fp[ind] / tail_p[ind]
            tu = (fu - fstart[i]) / Lj
            out[i] = 1.0 / tu
    return out


def grids(settings):
    step, steps = float(settings["step"]), float(settings["steps"])
    f = np.arange(0, int(round(float(settings["f_max"]) / step)) + 1) * step  # line 15
    fstart = np.arange(0, int(round(float(settings["fstart_max"]) / steps)) + 1) * steps  # line 16
    L = float(settings["L_min"]) * 2.0 ** np.arange(0.0, float(settings["L_octaves"]) + 1e-9, 0.5)  # line 14
    return f, fstart, L, step, steps


def rate_on_grid(event, inputs, f):
    if event == "koff":
        return koffcb(f, "mn", {"a": inputs["koff_a"], "b": inputs["koff_b"], "c": inputs["koff_c"],
                                "d": inputs["koff_d"]})  # line 29
    return kunf_slip(f, inputs["ln_kunf0"], inputs["kunf_b"], inputs["pt"])  # line 28


def run(inputs, settings):
    """The corrected rates ku of integrin unbinding (line 29) and talin unfolding (line 28) at one loading
    rate L and one starting force Fb: L need not lie on the script's grid (the row is computed at L
    itself), and Fb is taken at its grid index (line 43)."""
    f, fstart, _, step, steps = grids(settings)
    i = int(round(inputs["Fb"] / steps))
    out = {}
    for name, event in (("k_off", "koff"), ("k_unf", "kunf")):
        k = rate_on_grid(event, inputs, f)
        row = corrected_row(k, f, float(inputs["L"]), fstart[: i + 1], step, steps, float(settings["p_floor"]))
        out[name] = float(row[i])
    return out
