"""Runs the released svZeroDSolver (module svzerod, built from the code at commit 87bbadc) on one of the
release's test-case files, unchanged, and writes back the requested output columns as JSON.

Request (stdin): {"case": <path to the .json case file>, "columns": [[row name, column], ...]}
Reply: {"<row name>:<column>": [values at that name's output rows, in order], ...}
Run with the separate simulation interpreter (python -I); it imports nothing from the record.
"""
import json
import sys

import svzerod


def main():
    req = json.load(sys.stdin)
    with open(req["case"]) as fh:
        config = json.load(fh)
    df = svzerod.simulate(config)
    out = {}
    for name, col in req["columns"]:
        rows = df[df["name"] == name]
        out[f"{name}:{col}"] = [float(x) for x in rows[col]]
    sys.stdout.write(json.dumps(out))


if __name__ == "__main__":
    main()
