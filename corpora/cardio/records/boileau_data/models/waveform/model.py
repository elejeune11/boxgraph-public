# One column of a released waveform file, read at the times asked for: the value of column
# `column` (1-based, as the READMEs number them) at time t + t_offset, linearly interpolated in the
# file's first (time) column. Reads the supporting data files from the folder $BOXGRAPH_SOURCE;
# nothing of the data is copied into the record. The output is in the unit the README gives for
# that column; the model.yaml of each quantity's copy says which.
import os
import pathlib

import numpy as np


def run(inputs, settings):
    a = np.loadtxt(pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / settings["file"])
    a = a[~np.isnan(a).any(axis=1)]
    t = inputs["t"] + float(settings.get("t_offset", 0.0))
    if t < a[0, 0] - 1e-9 or t > a[-1, 0] + 1e-9:
        raise ValueError(f"t = {t} s is outside the file's times {a[0, 0]}-{a[-1, 0]} s")
    return {"y": float(np.interp(t, a[:, 0], a[:, int(settings["column"]) - 1]))}
