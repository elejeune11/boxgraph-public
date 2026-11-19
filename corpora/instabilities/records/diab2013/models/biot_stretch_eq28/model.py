# Helper for the relation to biot1963: the paper gives Biot's critical point as a nominal strain
# eps_B = 1 - lambda (p. 2, p. 5); Biot prints the stretch lambda. This returns the stretch at the
# divergence of Eq. 2.8, using the logic of biot_strain_eq28.
import importlib.util
import pathlib


def _strain_model():
    path = pathlib.Path(__file__).resolve().parent.parent / "biot_strain_eq28" / "model.py"
    spec = importlib.util.spec_from_file_location("diab2013_biot_strain_eq28", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(inputs, settings):
    return {"lam_B": 1.0 - _strain_model().run({}, {})["eps_B"]}
