# The critical plane strain mode of the exact bilayer analysis (built_from: bilayer_plane_strain),
# given as the wavelength over the film thickness, lambda/h = 2 pi / kh (both referenced to the
# undeformed film).
import importlib.util
import math
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "bilayer_plane_strain" / "model.py"
_spec = importlib.util.spec_from_file_location("cao2012_bilayer_plane_strain", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    s = _base.settings_of(settings)
    _ew, kh = _base.solve(inputs["mu_ratio"], inputs["lam01"], "plane_strain", s)
    return {"lam_over_h": 2 * math.pi / kh}
