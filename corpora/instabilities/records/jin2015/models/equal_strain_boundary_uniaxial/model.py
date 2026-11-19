# The boundary of equal critical strain (Sec. 2, Fig. 3(a)) under the uniaxial compression
# condition: Gf/Gs at which e_m^Uni (Eqs. B7-B15, lambda3 = 1/sqrt(lambda1)) equals the
# uniaxial crease strain. Uses the bisection of the plane strain boundary model.
import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "equal_strain_boundary_plane_strain" / "model.py"
_spec = importlib.util.spec_from_file_location("jin2015_equal_strain_boundary_plane_strain", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    return {"Gf_Gs": _base.boundary(inputs["Hs_Hf"], inputs["e_crease"], "uniaxial", settings)}
