"""Fig. S3D (PDF p. 16): brown line (ka = 0.5 pN/nm), no reinforcement, kl = 0.1 pN/nm.
Read by _figs3d.py / _lines.py (see their docstrings)."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_figs3d", Path(__file__).with_name("_figs3d.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at, "ka05")
