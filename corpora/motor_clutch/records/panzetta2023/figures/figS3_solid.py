"""One reading, named by this file: see _specs.py (what is read) and _p23.py (how)."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load(name):
    s = spec_from_file_location(f"panzetta2023_{name}", Path(__file__).with_name(f"{name}.py"))
    m = module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _load("_p23").read_spec(image, at, _load("_specs").SPECS[Path(__file__).stem])
