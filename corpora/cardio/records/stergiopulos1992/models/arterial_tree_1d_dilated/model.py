"""The 1D arterial tree of arterial_tree_1d with vasodilation at a fixed level (Fig. 3, elevated flow):
every terminal resistance distal to the stenosed segment is set to RT_fraction percent of its value
(p. 5: "reduced ... at 20% of the original value"), and the mean flow through the stenosed segment is
divided by its normal value Qn (0 % stenosis, original resistances). Uses arterial_tree_1d's code
unchanged."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "arterial_tree_1d_code", Path(__file__).resolve().parent.parent / "arterial_tree_1d" / "model.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    normal = _base._summary(inputs, settings, 0.0, 1.0)
    dilated = _base._summary(inputs, settings, inputs["stenosis"], inputs["RT_fraction"] / 100.0)
    return {"Q_ratio": dilated["q_seg"] / normal["q_seg"]}
