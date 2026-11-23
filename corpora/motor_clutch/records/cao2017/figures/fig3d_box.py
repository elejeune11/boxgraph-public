"""Fig. 3D (PDF p. 3, adapted from ref. 16): fibre recruitment (a.u.), the three box plots
(x = 1 soft, 2 stiff, 3 soft-weld): median, with the whisker ends as the error bar.

Read by the shared code in _fig3d.py (see its docstring). The hash pins _fig3d.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig3d.py")
SHARED_SHA256 = "04b1fa253e927e77bbf7caf7ee99808b30e547e5a1aaade5ad96264803ee44c1"


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig3d.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_fig3d", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at)
