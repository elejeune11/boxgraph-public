# Relative errors of a released 1D pressure waveform against a released reference waveform
# (the 3D solution or the in vitro measurement), as boileau2015 defines them for pressure:
# Eq. 10 (RMS), Eq. 11 (MAX), Eq. 12 (SYS), Eq. 13 (DIAS), each normalised point by point by the
# reference pressure (SYS by its maximum, DIAS by its minimum). Results in per cent.
#
# Reads the supporting data files from the folder $BOXGRAPH_SOURCE (the data are not copied into
# the record). The reference sample i at its own time t_i is matched with the 1D solution at
# t_ini + t_lag + t_i, linearly interpolated in the 1D file's time column; a time past the end of the
# last cycle (t_ini + period) is taken one period earlier (the solution is periodic there).
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
    e = (y - r) / r
    return {
        "rms": 100.0 * float(np.sqrt(np.mean(e ** 2))),
        "max": 100.0 * float(np.max(np.abs(e))),
        "sys": 100.0 * float((y.max() - r.max()) / r.max()),
        "dias": 100.0 * float((y.min() - r.min()) / r.min()),
    }
