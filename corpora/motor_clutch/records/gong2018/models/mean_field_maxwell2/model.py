"""Mean-field motor-clutch model on a generalized Maxwell substrate with two
Maxwell elements (Eqs. S11-S12; SI Fig. S8D): the logic of mean_field_sls with
elements (ka1, eta1) and (ka2, eta2 = ka2 tau_s2), tau_s,i = eta_i / ka,i."""
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("gong2018_mean_field_sls", os.path.join(_HERE, "..", "mean_field_sls", "model.py"))
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    p = {k: inputs[k] for k in _base.PARAMS}
    ka = [inputs["ka1"], inputs["ka2"]]
    eta = [inputs["eta1"], inputs["ka2"] * inputs["tau_s2"]]
    out = _base.mean_speed(p, ka, eta, inputs["kl"], settings)
    return {"Vs": out["Vs"]}
