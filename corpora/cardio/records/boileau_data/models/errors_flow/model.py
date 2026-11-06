# Relative errors of a released 1D waveform against a released reference waveform, in the form
# boileau2015 gives for the flow rate (Eqs. 10-13, right-hand forms): every difference is
# normalised by the maximum of the reference over the cycle, max_j(Q_j). The paper uses the same
# form for the pressure difference and the radius change (p. 12); this model is that form for the
# flow rate. Results in per cent.
#
# Reads the supporting data files from the folder $BOXGRAPH_SOURCE. The reference sample i at its
# own time t_i is matched with the 1D solution at t_ini + t_lag + t_i, linearly interpolated in the
# 1D file's time column; a time past the end of the last cycle (t_ini + period) is taken one period
# earlier.
import os
import pathlib

import numpy as np


def _load(rel):
    a = np.loadtxt(pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / rel)
    return a[~np.isnan(a).any(axis=1)]  # a row with a NaN (the first row of the B4 LCG files) is left out


def aligned(inputs, settings):
    ref = _load(settings["reference_file"])
    sol = _load(settings["solution_file"])
    t = ref[:, 0]
    t1 = inputs["t_ini"] + inputs["t_lag"] + t
    t1 = np.where(t1 > inputs["t_ini"] + inputs["period"] + 1e-9, t1 - inputs["period"], t1)
    y = np.interp(t1, sol[:, 0], sol[:, int(settings["solution_column"]) - 1])
    return y, ref[:, int(settings["reference_column"]) - 1]


def run(inputs, settings):
    y, r = aligned(inputs, settings)
    m = r.max()
    e = (y - r) / m
    return {
        "rms": 100.0 * float(np.sqrt(np.mean(e ** 2))),
        "max": 100.0 * float(np.max(np.abs(e))),
        "sys": 100.0 * float((y.max() - r.max()) / m),
        "dias": 100.0 * float((y.min() - r.min()) / m),
    }
