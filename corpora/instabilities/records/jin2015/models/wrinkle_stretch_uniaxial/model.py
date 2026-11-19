# Stretch along the compression at the onset of wrinkles under the uniaxial compression condition,
# lambda_c = 1 - e_m^Uni (the paper defines e_c = 1 - lambda_c, Appendix B). Built from
# wrinkle_eigen_uniaxial. This helper puts the paper's minimal critical strain in Biot's variable, the
# critical stretch, so that "when Gf/Gs = 1 ... em reaches the Biot strain under the uniaxial
# compression condition 0.556 [26]" (p. 10) can be tested against Biot's Eq. 4.13.
import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "wrinkle_eigen_uniaxial" / "model.py"
_spec = importlib.util.spec_from_file_location("jin2015_wrinkle_eigen_uniaxial", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    out = _base.run(inputs, settings)
    return {"lam_c": 1.0 - out["em"]}
