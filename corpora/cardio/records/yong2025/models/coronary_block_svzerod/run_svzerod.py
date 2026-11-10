# Runs the released svZeroDSolver (module svzerod) on a configuration read from stdin and
# prints, as JSON on stdout, each vessel's time, inlet flow and inlet pressure over the output
# cycle. Run with the separate simulation environment's interpreter, in isolated mode (-I).
import json
import sys

import svzerod


def main():
    config = json.load(sys.stdin)
    df = svzerod.simulate(config)
    out = {}
    for name, g in df.groupby("name"):
        g = g.sort_values("time")
        out[str(name)] = {
            "time": [float(v) for v in g["time"]],
            "flow_in": [float(v) for v in g["flow_in"]],
            "pressure_in": [float(v) for v in g["pressure_in"]],
        }
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
