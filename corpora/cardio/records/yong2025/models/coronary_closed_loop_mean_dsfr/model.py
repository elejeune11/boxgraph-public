# Variant of coronary_closed_loop: the same circulation, with Eq. 14 read as the ratio of the
# mean diastolic to the mean systolic flow (as Table 1's own rows give it) instead of the
# printed ratio of integrals. Loads the printed model's code; changes only that statistic.
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "yong2025_coronary_closed_loop_base",
    Path(__file__).resolve().parent.parent / "coronary_closed_loop" / "model.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    return _base.run(inputs, dict(settings, dsfr="mean"))
