"""Adapter: runs the released code's own lifetime() from the source's folder."""
import importlib.util
import os


def _code():
    path = os.path.join(os.environ["BOXGRAPH_SOURCE"], "clutch.py")
    spec = importlib.util.spec_from_file_location("toycode_clutch", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(inputs, settings):
    return {"t": _code().lifetime(inputs["F"], inputs["kT"])}
