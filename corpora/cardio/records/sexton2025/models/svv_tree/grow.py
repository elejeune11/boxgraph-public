# Run by model.py under the separate environment that holds svVascularize (svv 0.0.57, commit 5ca73e4),
# never in the project's environment. Reads one JSON request on stdin, grows one open-loop tree with
# svv's own Domain and Tree classes, and writes plain numbers (JSON) on stdout. Nothing of svv is copied
# here: this only calls its public API (Domain(...).create/solve/build, Tree().set_domain/set_root/n_add).
import os

os.environ["SVV_TELEMETRY_DISABLED"] = "1"

import contextlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402


def main():
    req = json.load(sys.stdin)
    seed = int(req["seed"])
    random.seed(seed)
    np.random.seed(seed)
    out_buf = io.StringIO()
    with contextlib.redirect_stdout(out_buf):
        import pyvista as pv
        from svv.domain.domain import Domain
        from svv.tree.tree import Tree

        t0 = time.time()
        edge = float(req["cube_edge"])
        dom = Domain(pv.Cube(x_length=edge, y_length=edge, z_length=edge))
        dom.create()
        dom.solve()
        dom.build()
        dom.set_random_seed(seed)
        t1 = time.time()
        tree = Tree()
        p = tree.parameters
        p.set("murray_exponent", float(req["gamma"]))
        p.set("radius_exponent", float(req["radius_exponent"]))
        p.set("length_exponent", float(req["length_exponent"]))
        p.set("kinematic_viscosity", float(req["kinematic_viscosity"]))   # cm^2/s (svv's cgs base units)
        p.set("fluid_density", float(req["density"]))                     # g/cm^3
        p.set("terminal_flow", float(req["terminal_flow"]))               # mL/s
        p.set("root_pressure", float(req["root_pressure"]), unit="mmHg")
        p.set("terminal_pressure", float(req["terminal_pressure"]), unit="mmHg")
        tree.set_domain(dom)
        tree.set_root()
        tree.n_add(int(req["n_terminals"]) - 1)    # set_root makes the first terminal
        t2 = time.time()
    d = np.asarray(tree.data, dtype=float)
    cols = {"left": 15, "right": 16, "parent": 17, "length": 20, "radius": 21, "flow": 22,
            "lbif": 23, "rbif": 24, "rstar": 25, "depth": 26, "scaling": 28}
    res = {k: [None if np.isnan(x) else float(x) for x in d[:, c]] for k, c in cols.items()}
    res["n_terminals"] = int(tree.n_terminals)
    res["params"] = {"murray_exponent": float(p.murray_exponent), "kinematic_viscosity": float(p.kinematic_viscosity),
                     "fluid_density": float(p.fluid_density), "terminal_flow": float(p.terminal_flow),
                     "root_pressure": float(p.root_pressure), "terminal_pressure": float(p.terminal_pressure)}
    res["t_domain"] = t1 - t0
    res["t_grow"] = t2 - t1
    json.dump(res, sys.stdout)


if __name__ == "__main__":
    main()
