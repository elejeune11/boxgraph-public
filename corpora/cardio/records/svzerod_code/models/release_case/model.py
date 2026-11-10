"""Adapter: reruns one of the release's own test cases (tests/cases/<case>.json, read from the code
folder $BOXGRAPH_SOURCE) with the released svZeroDSolver, unchanged, and returns one pressure and one
flow from its output.

Settings:
  case: the file name in tests/cases without .json
  P, Q: [row name, column] of the output to return. For vessel-based output the row name is the
        vessel (e.g. branch0_seg0) and the column pressure_in, pressure_out, flow_in or flow_out; for
        variable-based output (output_variable_based) the row name is the variable (e.g.
        pressure:INFLOW:branch0_seg0) and the column y.
  row:  which output row: an index into that name's rows (0 = the first output time; -1 = the last).
The solver runs in its own interpreter (simulate_case.py, beside this file). The case files state no
units; the record reads them as cgs (question q_case_units).
"""
import json
import os
import subprocess


def _sim_python():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.environ.get("BOXGRAPH_SOURCE")
    if src:
        cand = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(src))), "envs", "sim", "bin", "python")
        if os.path.exists(cand):
            return cand
    root = os.path.abspath(os.path.join(here, *[".."] * 6))
    return os.path.join(root, "corpus", "cardio", "envs", "sim", "bin", "python")


def run(inputs, settings):
    here = os.path.dirname(os.path.abspath(__file__))
    case = os.path.join(os.environ["BOXGRAPH_SOURCE"], "tests", "cases", settings["case"] + ".json")
    req = json.dumps({"case": case, "columns": [settings["P"], settings["Q"]]})
    out = subprocess.run([_sim_python(), "-I", os.path.join(here, "simulate_case.py")], input=req,
                         capture_output=True, text=True, timeout=600)
    if out.returncode != 0:
        raise RuntimeError(f"svZeroDSolver failed: {out.stderr[-2000:]}")
    res = json.loads(out.stdout)
    row = int(settings.get("row", 0))
    p = res["{}:{}".format(*settings["P"])]
    q = res["{}:{}".format(*settings["Q"])]
    return {"P": p[row], "Q": q[row]}
