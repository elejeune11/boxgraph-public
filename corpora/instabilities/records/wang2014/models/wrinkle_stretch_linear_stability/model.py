# Film stretch along the compression at the onset of wrinkling, 1 - e_c wrinkle, from the linear
# stability analysis (built_from wrinkle_linear_stability). The paper's strain is e = DL/L in plane
# strain, so the film stretch is 1 - e; this helper puts the result in Biot's variable, the critical
# stretch, so that the paper's statement "consistent with Biot's [51]" can be tested.
import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "wrinkle_linear_stability" / "model.py"
_spec = importlib.util.spec_from_file_location("wang2014_wrinkle_linear_stability", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    ew, _ = _base.solve(inputs["mu_ratio"], inputs["lam_p"], _base.settings_of(settings))
    return {"lam_c": 1.0 - ew}
