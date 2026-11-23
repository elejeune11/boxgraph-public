"""Extended Data Fig. 5(a) (PDF p. 70): the dashed blue (unstable) branch, linear KD model with sigma_m = 26 um^-2.
Settings and method: _ed5.py and _fig.py. Read only in columns where the blue curve has exactly three runs; the dashed branch is the middle one (between dashes there is no value)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("liu2025_ed5", Path(__file__).with_name("_ed5.py"))
E5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E5)


def read(image, at):
    return E5.read(image, at, "a", "blue", pick=1, n_runs=3)


def debug(image):
    return E5.debug(image, "a")
