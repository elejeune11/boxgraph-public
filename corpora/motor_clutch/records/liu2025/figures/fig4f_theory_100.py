"""Fig. 4(f) (PDF p. 10): force-loading rates predicted by the talin WT model with vinculin
(Theory, 100 molecular-clutch sites per um^2; bars 1 MEF WT, 2 MEF vinI997A, 3 MEF Vcl KO).
Method as fig4f_exp (loaded from it), without error bars.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_fig4fe", Path(__file__).with_name("fig4f_exp.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    return B.read_group(image, "100", False)
