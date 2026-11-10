"""Runs the released svZeroDSolver (module svzerod, built from the code at commit 87bbadc) on one
configuration read from stdin, and writes back plain numbers as JSON.

Request: {"config": <svZeroDSolver configuration>, "columns": [[vessel name, column], ...]}
Reply:   {"time": [...], "<vessel>:<column>": [...], ...} for the rows the solver outputs.
Run with the separate simulation interpreter (python -I); it imports nothing from the record.
"""
import json
import sys

import svzerod


def main():
    req = json.load(sys.stdin)
    df = svzerod.simulate(req["config"])
    out = {}
    for name, col in req["columns"]:
        rows = df[df["name"] == name]
        out["time"] = [float(x) for x in rows["time"]]
        out[f"{name}:{col}"] = [float(x) for x in rows[col]]
    sys.stdout.write(json.dumps(out))


if __name__ == "__main__":
    main()
