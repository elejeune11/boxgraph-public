"""Adapter: grows the same tree twice with the released svVascularize, with the same seed, in two separate
processes (tree_growth's grow.py), and reports how far the two trees differ. The setting seed_order says
when the seed is given to svv's Domain: "before" (before Domain.create, so that the generator svv builds
from it is seeded) or "after_build" (after Domain.build, as a user calling set_random_seed on a finished
domain would; svv then keeps the unseeded generator it already made, domain.py lines 179-190, 460-461)."""
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def _tree_growth():
    path = os.path.join(os.path.dirname(_HERE), "tree_growth", "model.py")
    spec = importlib.util.spec_from_file_location("svv_code_tree_growth_r", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(inputs, settings):
    tg = _tree_growth()
    req = {"seed": int(settings["seed"]), "n_terminals": int(round(inputs["n_terminals"])), "domain": "cube",
           "cube_edge": float(inputs["cube_edge"]), "params": {}, "export_0d": False,
           "seed_order": settings["seed_order"]}
    a, b = tg.grow(req), tg.grow(req)
    ends_a = np.array([a[k][0] for k in ("x1", "y1", "z1")])
    ends_b = np.array([b[k][0] for k in ("x1", "y1", "z1")])
    ra, rb = tg._arr(a, "radius"), tg._arr(b, "radius")
    same = len(ra) == len(rb)
    return {"root_end_distance": float(np.linalg.norm(ends_a - ends_b)),
            "radius_diff_max": float(np.max(np.abs(ra / rb - 1.0))) if same else float("nan"),
            "root_diameter_diff": float(abs(ra[0] / rb[0] - 1.0))}
