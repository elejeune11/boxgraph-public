# The critical strain e_c for wrinkles of a given nominal wavelength L_wrinkle/Hf (Fig. 2):
# the smallest strain at which det A = 0 (Eqs. B7-B15) for K Hf = 2 pi/(L_wrinkle/Hf), under
# uniaxial compression lambda3 = 1/sqrt(lambda1). Uses the eigenvalue solver of the plane strain
# model (built_from: wrinkle_eigen_plane_strain); its strain scan and bisection are the reader's.
import importlib.util
import math
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "wrinkle_eigen_plane_strain" / "model.py"
_spec = importlib.util.spec_from_file_location("jin2015_wrinkle_eigen_plane_strain", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    s = _base.settings_of(settings)
    KHf = 2 * math.pi / inputs["L"]
    ec = _base.critical_strain_at(KHf, inputs["Gf_Gs"], inputs["Hs_Hf"], "uniaxial", s)
    if ec is None:
        raise ValueError(f"no root of det A below e = {s['e_max']} at L/Hf = {inputs['L']}")
    return {"ec": ec}
