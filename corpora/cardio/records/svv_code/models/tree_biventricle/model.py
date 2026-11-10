"""Adapter: as tree_growth, with the tree grown in the biventricle surface shipped with the code
(biventricle_tissue.stl, read by svv's Domain from the code folder) instead of a cube. It loads
tree_growth's adapter, which runs svv; nothing else differs."""
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _tree_growth():
    path = os.path.join(os.path.dirname(_HERE), "tree_growth", "model.py")
    spec = importlib.util.spec_from_file_location("svv_code_tree_growth", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(inputs, settings):
    tg = _tree_growth()
    req = {"seed": int(settings["seed"]), "n_terminals": int(round(inputs["n_terminals"])),
           "domain": settings["domain_file"], "params": {}, "export_0d": True,
           "seed_order": settings.get("seed_order", "before")}
    return tg.statistics(tg.grow(req), settings)
