"""Adapter: reruns one of the release's own system test cases (Tests/SystemTests/cases/<case>.in, read
from the code folder $BOXGRAPH_SOURCE) with the released svOneDSolver, unchanged, and returns the
value the release's test reads from its output.

It does what Tests/SystemTests/test_integration.py does (run_oned, read_results_1d, get_result_value):
run the executable on the case file in an empty working directory, read the TEXT result files
results_<case>_seg*_<field>.dat (rows = finite-element nodes, columns = saved time steps after the
first column, the initial state, which the test drops), and select

  seg:  the segment number (the last number in the file name), as in the test
  node: the node index along the segment (0 = inlet, -1 = outlet)
  time: a saved-step index (-1 = the last), or [start, stop] for the steps start..stop-1
  fun:  point | mean | max | min over those steps

The outputs P, Q and S are that selection of the pressure, flow and area files. Nothing of the
release is copied: the case file is read from the code folder at run time.
"""
import glob
import os
import re
import subprocess
import tempfile


def _exe():
    src = os.environ.get("BOXGRAPH_SOURCE")
    if src:
        cand = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(src))), "envs", "oned", "build", "bin", "OneDSolver")
        if os.path.exists(cand):
            return cand
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, *[".."] * 6))
    return os.path.join(root, "corpus", "cardio", "envs", "oned", "build", "bin", "OneDSolver")


def _read(td, case):
    res = {}
    for field in ("flow", "pressure", "area"):
        res[field] = {}
        for f in sorted(glob.glob(os.path.join(td, "results_" + case + "_seg*_" + field + ".dat"))):
            seg = int(re.findall(r"\d+", os.path.basename(f))[-1])
            rows = []
            with open(f) as fh:
                for line in fh:
                    vals = [float(m) for m in line.split()]
                    if vals:
                        rows.append(vals[1:])
            res[field][seg] = rows
    return res


def _select(rows, node, time, fun):
    row = rows[node]
    if isinstance(time, (list, tuple)):
        vals = row[int(time[0]):int(time[1])]
    else:
        vals = [row[int(time)]]
    if fun == "point":
        return vals[0]
    if fun == "mean":
        return sum(vals) / len(vals)
    if fun == "max":
        return max(vals)
    if fun == "min":
        return min(vals)
    raise ValueError("unknown fun " + str(fun))


def run(inputs, settings):
    case = settings["case"]
    path = os.path.join(os.environ["BOXGRAPH_SOURCE"], "Tests", "SystemTests", "cases", case + ".in")
    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run([_exe(), path], cwd=td, capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            raise RuntimeError("OneDSolver failed: " + proc.stdout[-1500:] + proc.stderr[-500:])
        res = _read(td, case)
    seg, node, time, fun = int(settings["seg"]), int(settings["node"]), settings["time"], settings["fun"]
    return {"P": _select(res["pressure"][seg], node, time, fun),
            "Q": _select(res["flow"][seg], node, time, fun),
            "S": _select(res["area"][seg], node, time, fun)}
