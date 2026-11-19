# Wrinkling of the neo-Hookean bilayer (Eqs. B7-B15) under the uniaxial compression
# condition lambda3 = 1/sqrt(lambda1) (Sec. 2, Appendix B). Uses the eigenvalue solver
# of the plane strain model (built_from: wrinkle_eigen_plane_strain).
import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "wrinkle_eigen_plane_strain" / "model.py"
_spec = importlib.util.spec_from_file_location("jin2015_wrinkle_eigen_plane_strain", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    return _base.solve(inputs["Gf_Gs"], inputs["Hs_Hf"], "uniaxial", settings)
