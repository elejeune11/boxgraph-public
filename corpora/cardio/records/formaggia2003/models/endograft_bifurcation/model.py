# The bifurcated channel with an endograft (Section 3.2, Figs. 10-13): six domains as in
# Fig. 10, Omega_1 -> Omega_2 (interface (32)), Omega_2 -> Omega_3, Omega_5 (bifurcation,
# (35) and (38)), Omega_3 -> Omega_4 and Omega_5 -> Omega_6 (interfaces (32)); non-reflecting
# outlets at the ends of Omega_4 and Omega_6. Same solver as bifurcation_angles (built_from).
# Returns A, W1, W2 at the midpoints of Omega_1, Omega_2 and Omega_6 at time t. CGS units.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_bifurcation_angles", os.path.join(_here, "..", "bifurcation_angles", "model.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

_MEMO = {}
NAMES = ("A_1", "W1_1", "W2_1", "A_2", "W1_2", "W2_2", "A_6", "W1_6", "W2_6")
ENDOGRAFTED = (2, 3, 5)


def _simulate(inp, settings):
    _b.check_alpha(inp["alpha"])
    n = int(settings["n_elements"])
    vs = [dict(L=inp["L"], n=n, R0=inp[f"R0_{i}"],
               E=inp["E_endograft"] if i in ENDOGRAFTED else inp["E_vessel"]) for i in range(1, 7)]
    none1 = (0.0, [(0.0, 0.0)])
    none2 = (0.0, [(0.0, 0.0), (0.0, 0.0)])
    links = [(0, [1], none1), (1, [2, 4], none2), (2, [3], none1), (4, [5], none1)]
    net = _b.Network(vs, inp["h0"], inp["rho"], inp["nu"], 0, links, [3, 5],
                     _b.half_sine(inp["P_amp"], inp["T_pulse"]), float(settings["newton_tol"]),
                     str(settings["inlet"]))
    return _b.simulate(net, float(settings["dt"]), float(settings["t_end"]), [0, 1, 5])


def run(inputs, settings):
    base = {k: float(v) for k, v in inputs.items() if k != "t"}
    key = (tuple(sorted(base.items())), tuple(sorted((k, str(v)) for k, v in settings.items())))
    if key not in _MEMO:
        _MEMO.clear()
        _MEMO[key] = _simulate(base, settings)
    vals = _b.at_time(_MEMO[key], float(settings["dt"]), float(inputs["t"]))
    return dict(zip(NAMES, vals))
