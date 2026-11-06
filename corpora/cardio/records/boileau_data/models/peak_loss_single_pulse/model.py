# Loss of the peak pressure of the single pulse between the first and the last time the released
# Benchmark 1 file holds: 100 (1 - max_x P(x, t_last) / max_x P(x, t_first)), in per cent.
# The README of Benchmark 1 gives the file's columns: distance [m], then the pressure along the
# vessel at t = 0.1, 0.3, ..., 1.5 s. Reads the file from the folder $BOXGRAPH_SOURCE.
import os
import pathlib

import numpy as np


def run(inputs, settings):
    a = np.loadtxt(pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / settings["file"])
    first = a[:, int(settings["first_column"]) - 1].max()
    last = a[:, int(settings["last_column"]) - 1].max()
    return {"loss": 100.0 * float(1.0 - last / first)}
