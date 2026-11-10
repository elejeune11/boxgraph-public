# Run by model.py under the separate environment that holds svVascularize's dependencies
# (corpus/cardio/envs/sim, `python -I`, SVV_TELEMETRY_DISABLED=1). Imports svv from the code folder given
# as the first argument (BOXGRAPH_SOURCE) and prints, as JSON, the constants a default TreeParameters()
# carries (svv/tree/data/data.py lines 259-284), in svv's own base units (cm, g, s; pressures in dyn/cm^2),
# with the factor svv itself uses to turn mmHg into its pressure unit.
import os
import sys

os.environ["SVV_TELEMETRY_DISABLED"] = "1"
sys.path.insert(0, os.path.abspath(sys.argv[1]))

import contextlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    import svv
    from svv.tree.data.data import TreeParameters

    p = TreeParameters()
    q = TreeParameters()
    q.set("root_pressure", 1.0, unit="mmHg")
json.dump({"file": os.path.abspath(svv.__file__),
           "murray_exponent": float(p.murray_exponent), "radius_exponent": float(p.radius_exponent),
           "length_exponent": float(p.length_exponent), "kinematic_viscosity": float(p.kinematic_viscosity),
           "fluid_density": float(p.fluid_density), "terminal_flow": float(p.terminal_flow),
           "root_pressure": float(p.root_pressure), "terminal_pressure": float(p.terminal_pressure),
           "max_nonconvex_count": float(p.max_nonconvex_count), "mmhg": float(q.root_pressure)}, sys.stdout)
