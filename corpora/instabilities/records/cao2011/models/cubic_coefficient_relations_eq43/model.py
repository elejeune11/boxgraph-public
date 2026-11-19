# Eq. 3.7 with the Biot modes (2.9)-(2.10), for the three coefficients of Eq. 4.3 that the paper prints
# only through relations: b224/4, b336/9 (both printed equal to b112) and b246/4 (printed equal to b123).
# Uses the integrand of cubic_coefficients_eq37 and A of quadratic_coefficient_eq38.
import importlib.util
import itertools
import pathlib

_here = pathlib.Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location("cao2011_" + name, _here / name / "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_cubic = _load("cubic_coefficients_eq37")
_base = _cubic._base

TRIPLES = {"b224_4": ((2, 2, 4), 4.0), "b336_9": ((3, 3, 6), 9.0), "b246_4": ((2, 4, 6), 4.0)}


def run(inputs, settings):
    r = inputs["r"]
    x1 = _base.grid(int(settings.get("n_x1", 64)))
    depth = float(settings.get("depth", 12.0))
    A = _base.coefficient_A(r, settings)
    out = {}
    for name, (t, divisor) in sorted(TRIPLES.items()):
        total = sum(_cubic.term(r, *p, x1, depth) for p in sorted(set(itertools.permutations(t))))
        out[name] = total / A / divisor
    return out
