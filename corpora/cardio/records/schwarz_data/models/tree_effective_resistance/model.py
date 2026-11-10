# Our code (software: true only to read the released network from $BOXGRAPH_SOURCE): the weight-corrected
# effective resistance of the released left coronary tree, (P_in - P_cap) over the total inflow per 100 g of
# perfused tissue, from network_solution's solver (the same _solve as run_net_release). Built for comparisons
# with lumped coronary resistances given per 100 g, such as mynard2014's (pLM - pRA)/qLM.
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_PA_PER_MMHG = 133.322


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


NS = _load("schwarz_network_solution", os.path.join("..", "network_solution", "model.py"))


def run(inputs, settings):
    net = NS._network(settings["file"])
    sol = NS._solve(net, inputs["P_in"], inputs["P_cap"], inputs["Hd"], inputs["mu_p"])
    q_m3s = float(sol["q_se"][net["se_inlet"]].sum())
    Q_mlmin = q_m3s * 1e6 * 60.0
    mass_hg = inputs["W"] * inputs["f_tree"] * 10.0       # kg -> units of 100 g
    q = Q_mlmin / mass_hg
    dP_mmHg = (inputs["P_in"] - inputs["P_cap"]) / _PA_PER_MMHG
    return {"Q_in": Q_mlmin, "q_per_mass": q, "R_eff": dP_mmHg / q}
