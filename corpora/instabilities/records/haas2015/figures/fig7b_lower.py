"""Fig. 7(b) (PDF p. 7): the lower black branch, labelled lambda < lambda*, kappa/(G R) against kR.
The reading code is in fig7b_branches.py (see its docstring); this file only picks the lower branch.
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("haas2015_fig7b", Path(__file__).with_name("fig7b_branches.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.read_lower(image, at)
