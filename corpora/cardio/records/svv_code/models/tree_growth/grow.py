# Run by model.py under the separate environment that holds svVascularize's dependencies
# (corpus/cardio/envs/sim, `python -I`, SVV_TELEMETRY_DISABLED=1), never in the project's environment.
# It imports svv from the code folder named in the request (BOXGRAPH_SOURCE: the released code at commit
# 5ca73e4, the same Python files as svv 0.0.57), grows one open-loop tree with svv's own Domain and Tree
# classes, optionally writes svv's own 0D export of it and runs that with svZeroDSolver, and writes plain
# numbers (JSON) on stdout. Nothing of svv is copied here: this only calls its API.
#
# Request (JSON on stdin):
#   source        the code folder (put first on sys.path, so `import svv` loads the released code)
#   seed          seeds Python's random, numpy's global generator and the domain's generator
#   n_terminals   terminals of the grown tree (set_root makes the first)
#   domain        "cube" (pyvista Cube of edge `cube_edge`, cm) or a surface file inside the code folder
#   params        {name: value} set on tree.parameters (svv's own names, cgs units; pressures in mmHg),
#                 or {} to keep svv's defaults
#   export_0d     true: write svv's 0D model of the tree (export_0d_simulation, its defaults) and run it
import os

os.environ["SVV_TELEMETRY_DISABLED"] = "1"

import contextlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

COLS = {"x0": 0, "y0": 1, "z0": 2, "x1": 3, "y1": 4, "z1": 5, "left": 15, "right": 16, "parent": 17,
        "length": 20, "radius": 21, "flow": 22, "lbif": 23, "rbif": 24, "rstar": 25, "depth": 26,
        "scaling": 28}


def _list(col):
    return [None if np.isnan(x) else float(x) for x in col]


def main():
    req = json.load(sys.stdin)
    sys.path.insert(0, os.path.abspath(req["source"]))
    seed = int(req["seed"])
    random.seed(seed)
    np.random.seed(seed)
    log = io.StringIO()
    res = {}
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        import pyvista as pv
        import svv
        from svv.domain.domain import Domain
        from svv.tree.tree import Tree

        res["svv_file"] = os.path.abspath(svv.__file__)
        res["svv_version"] = svv.__version__
        t0 = time.time()
        if req["domain"] == "cube":
            edge = float(req["cube_edge"])
            surf = pv.Cube(x_length=edge, y_length=edge, z_length=edge)
        else:
            surf = pv.read(os.path.join(req["source"], req["domain"]))
        res["domain_bounds"] = [float(b) for b in surf.bounds]
        dom = Domain(surf)
        # Domain.set_random_seed only stores the seed (domain.py lines 179-184); the generator that set_root
        # and get_points draw from is made from it when the domain is created or built (lines 186-190,
        # 374, 404, 460-461). The seed is therefore set first ("before"); "after_build" sets it after
        # build, which leaves the generator unseeded.
        if req.get("seed_order", "before") == "before":
            dom.set_random_seed(seed)
        dom.create()
        dom.solve()
        dom.build()
        if req.get("seed_order", "before") != "before":
            dom.set_random_seed(seed)
        res["domain_volume"] = float(dom.volume)
        t1 = time.time()
        tree = Tree()
        p = tree.parameters
        for name, value in sorted(req.get("params", {}).items()):
            if name in ("root_pressure", "terminal_pressure"):
                p.set(name, float(value), unit="mmHg")
            else:
                p.set(name, float(value))
        tree.set_domain(dom)
        tree.set_root()
        tree.n_add(int(req["n_terminals"]) - 1)
        t2 = time.time()
        res["params"] = {k: float(getattr(p, k)) for k in (
            "murray_exponent", "radius_exponent", "length_exponent", "kinematic_viscosity", "fluid_density",
            "terminal_flow", "root_pressure", "terminal_pressure")}
        from svv.tree.data.data import TreeParameters

        one = TreeParameters()
        one.set("root_pressure", 1.0, unit="mmHg")
        res["params"]["mmhg"] = float(one.root_pressure)            # svv's own pressure unit per mmHg
        d = np.asarray(tree.data, dtype=float)
        # svv's own check functions (bifurcation.py lines 2158-2205, "used to check the values assigned
        # in the current tree"), on a copy: naive() recomputes lengths, R* and the ratios bottom-up from the
        # geometry and flows; the root radius then follows from Eq. S8 as update_radii writes it
        # (c_update.py line 49), and naive_radius() propagates it down by the recomputed ratios.
        from svv.tree.branch.bifurcation import naive, naive_radius

        sys.setrecursionlimit(100000)
        chk = d.copy()
        naive(tree, chk, 0)
        chk[0, 21] = ((chk[0, 25] * chk[0, 22]) / (p.root_pressure - p.terminal_pressure)) ** 0.25
        naive_radius(chk)
        res["check_rstar"] = _list(chk[:, 25])
        res["check_radius"] = _list(chk[:, 21])
        res["check_lbif"] = _list(chk[:, 23])
        res["check_rbif"] = _list(chk[:, 24])
        if req.get("export_0d"):
            from svv.simulation.fluid.rom.zero_d.zerod_tree import export_0d_simulation
            import svzerod

            with tempfile.TemporaryDirectory() as tmp:
                export_0d_simulation(tree, outdir=tmp)
                with open(os.path.join(tmp, "0d_tmp", "solver_0d.in")) as f:
                    config = json.load(f)
            df = svzerod.simulate(config)
            last = df["time"].max()
            df = df[df["time"] == last]
            byname = {str(r["name"]): r for _, r in df.iterrows()}
            bcs = {b["bc_name"]: b for b in config["boundary_conditions"]}
            outlets = []
            for v in config["vessels"]:
                bc = v.get("boundary_conditions", {})
                if "outlet" in bc:
                    r = byname[v["vessel_name"]]
                    outlets.append({"vessel": int(v["vessel_id"]), "R": float(bcs[bc["outlet"]]["bc_values"]["R"]),
                                    "Pd": float(bcs[bc["outlet"]]["bc_values"]["Pd"]),
                                    "P_out": float(r["pressure_out"]), "Q_out": float(r["flow_out"])})
            root = byname[config["vessels"][0]["vessel_name"]]
            res["zerod"] = {"P_in": float(root["pressure_in"]), "Q_in": float(root["flow_in"]),
                            "R_poiseuille": [float(v["zero_d_element_values"]["R_poiseuille"]) for v in config["vessels"]],
                            "outlets": outlets}
    res.update({k: _list(d[:, c]) for k, c in COLS.items()})
    res["n_terminals"] = int(tree.n_terminals)
    res["t_domain"] = t1 - t0
    res["t_grow"] = t2 - t1
    json.dump(res, sys.stdout)


if __name__ == "__main__":
    main()
