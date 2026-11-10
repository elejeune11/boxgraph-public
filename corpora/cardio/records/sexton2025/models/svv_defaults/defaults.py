# Run by model.py under the separate environment that holds svVascularize (svv 0.0.57). Prints, as JSON,
# the constants a default svv TreeParameters() carries (svv/tree/data/data.py lines 259-284), in svv's
# own base units (cm, g, s; pressures in dyn/cm^2).
import os

os.environ["SVV_TELEMETRY_DISABLED"] = "1"

import contextlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    from svv.tree.data.data import TreeParameters

    p = TreeParameters()
json.dump({"murray_exponent": float(p.murray_exponent), "radius_exponent": float(p.radius_exponent),
           "length_exponent": float(p.length_exponent), "kinematic_viscosity": float(p.kinematic_viscosity),
           "fluid_density": float(p.fluid_density), "terminal_flow": float(p.terminal_flow),
           "root_pressure": float(p.root_pressure), "terminal_pressure": float(p.terminal_pressure)}, sys.stdout)
