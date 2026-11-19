# Exact wrinkling bifurcation of the neo-Hookean bilayer (Appendix, Eqs. A1-A10) for
# uniaxial compressive stressing after a uniaxial-tension substrate prestretch (Sec. 3.3):
# lam2 = lam3 = 1/sqrt(lam1) in film and substrate, lam03s = 1/sqrt(lam01s).
# Uses the eigenvalue solver of the plane strain model (built_from: bilayer_plane_strain).
import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "bilayer_plane_strain" / "model.py"
_spec = importlib.util.spec_from_file_location("cao2012_bilayer_plane_strain", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    s = _base.settings_of(settings)
    ew, kh = _base.solve(inputs["mu_ratio"], inputs["lam01"], "uniaxial", s)
    return {"eW": ew, "kh": kh}
