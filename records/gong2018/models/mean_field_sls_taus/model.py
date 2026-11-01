"""Mean-field motor-clutch model on a standard linear solid, at a fixed initial
stiffness k0 = ka + kl, as a function of tau_s/tau_b (Fig. 3A): the logic of
mean_field_sls with ka = k0 - kl and eta = ka (tau_s/tau_b) / ron0, from
tau_s = eta/ka and tau_b = 1/ron (p. 5) taken at the unreinforced ron0."""
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("gong2018_mean_field_sls", os.path.join(_HERE, "..", "mean_field_sls", "model.py"))
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    p = {k: inputs[k] for k in _base.PARAMS}
    ka = inputs["k0"] - inputs["kl"]
    eta = ka * inputs["ratio"] / inputs["ron0"]
    out = _base.mean_speed(p, [ka], [eta], inputs["kl"], settings)
    return {"Vs": out["Vs"]}
