"""ModelAtlas: relations between models, tested; families computed.

Every relation is tested the same way whether a paper states it or it was
proposed (03-modelatlas.md). A mapping gives each of b's inputs as an
expression in a's inputs, with numbers in each model's own port units.
Outputs are converted between units automatically.

Tests by kind:
  same_as          symbolic identity if both models give symbolic(); else
                   numeric agreement over the regime
  reduces_to       a approaches b as the stated limit is taken
  derived_from     the paper's steps, applied to a symbolically, reach b;
                   steps that cannot be applied make it unverifiable
  scales_as        equal log-slopes of the outputs in the shared (mapped) variables
  approximated_by  the error over the regime is measured (it is a datum)
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import networkx as nx
import sympy as sp

from . import units as U
from .engine import BuildError, execute, symbolic
from .schema import Relation, RelationKind
from .store import LoadedRecord, model_by_id

N_SAMPLES = 40
PLAIN_OPS = 2


@dataclass
class RelationResult:
    id: str
    kind: str
    a: str
    b: str
    provenance: str
    status: str
    method: str = ""
    detail: str = ""
    holds_instead: str | None = None
    error: float | None = None  # approximated_by: the measured max relative error
    too_plain: bool = False
    source: str | None = None  # the record the relation was entered in
    samples: int = 0

    def to_json(self) -> dict:
        return dict(vars(self))


class _Unverifiable(Exception):
    pass


@dataclass
class _Side:
    gid: str
    lr: LoadedRecord
    model: object
    path: object
    expr: dict | None = field(default=None)
    cache_dir: object = None


def _side(gid: str, records: dict[str, LoadedRecord], cache_dir=None) -> _Side:
    if "/" not in gid:
        raise _Unverifiable(f"model id {gid!r} is not '<source>/<model>'")
    sid, mid = gid.split("/", 1)
    lr = records.get(sid)
    if lr is None:
        raise _Unverifiable(f"source {sid!r} is not in the record")
    m = model_by_id(lr, mid)
    if m is None:
        raise _Unverifiable(f"model {gid!r} is not in the record")
    if not m.runnable:
        raise _Unverifiable(f"model {gid!r} cannot be run: {m.not_runnable_reason}")
    path = lr.model_code.get(mid)
    if path is None:
        raise _Unverifiable(f"model {gid!r} has no code")
    return _Side(gid, lr, m, path, cache_dir=cache_dir)


def _symbols(names) -> dict[str, sp.Symbol]:
    return {n: sp.Symbol(n, positive=True) for n in names}


def _sym_expr(side: _Side) -> dict[str, sp.Expr] | None:
    if side.expr is None:
        raw = symbolic(side.path, cache_dir=side.cache_dir)
        if raw is None:
            side.expr = {}
        else:
            loc = _symbols(side.model.inputs)
            try:
                side.expr = {k: sp.sympify(v, locals=loc) for k, v in raw.items()}
            except (sp.SympifyError, TypeError):
                side.expr = {}
    return side.expr or None


def _output_pair(rel: Relation, a: _Side, b: _Side) -> tuple[str, str]:
    if rel.output_map:
        if len(rel.output_map) != 1:
            raise _Unverifiable("only one output pair per relation is supported")
        (bo, ao), = rel.output_map.items()
    else:
        if len(a.model.outputs) != 1 or len(b.model.outputs) != 1:
            raise _Unverifiable("models have several outputs; output_map must say which correspond")
        ao, bo = next(iter(a.model.outputs)), next(iter(b.model.outputs))
    if ao not in a.model.outputs or bo not in b.model.outputs:
        raise _Unverifiable(f"output_map names unknown outputs {bo!r} -> {ao!r}")
    return ao, bo


def _mapping(rel: Relation, a: _Side, b: _Side, exclude: set[str] = frozenset()):
    loc = _symbols(a.model.inputs)
    exprs = {}
    for bs in b.model.inputs:
        if bs not in rel.mapping:
            raise _Unverifiable(f"mapping does not give b's input {bs!r}")
        try:
            exprs[bs] = sp.sympify(rel.mapping[bs], locals=loc)
        except (sp.SympifyError, TypeError) as e:
            raise _Unverifiable(f"mapping for {bs!r} cannot be read: {e}") from None
        stray = {s.name for s in exprs[bs].free_symbols} - set(a.model.inputs)
        if stray:
            raise _Unverifiable(f"mapping for {bs!r} uses symbols that are not a's inputs: {sorted(stray)}")
    funcs = {bs: sp.lambdify([loc[n] for n in a.model.inputs], e, "math") for bs, e in exprs.items()}
    return exprs, funcs


def _samples(rel: Relation, a: _Side, n: int = N_SAMPLES) -> list[dict[str, float]]:
    missing = set(a.model.inputs) - set(rel.regime)
    if missing:
        raise _Unverifiable(f"the regime does not give a range for a's inputs {sorted(missing)}")
    rng = random.Random(f"{rel.id}:{rel.a}:{rel.b}")  # deterministic
    out = []
    for _ in range(n):
        pt = {}
        for s in a.model.inputs:
            lo, hi = rel.regime[s]
            if lo > 0 and hi / lo >= 10:
                pt[s] = math.exp(rng.uniform(math.log(lo), math.log(hi)))
            else:
                pt[s] = rng.uniform(lo, hi)
        out.append(pt)
    return out


def _eval(rel, a: _Side, b: _Side, points: list[dict[str, float]]) -> tuple[list[float], list[float]]:
    ao, bo = _output_pair(rel, a, b)
    _, funcs = _mapping(rel, a, b)
    order = list(a.model.inputs)
    b_points = [{bs: f(*[p[n] for n in order]) for bs, f in funcs.items()} for p in points]
    try:
        ra = execute(a.path, [{"inputs": p, "settings": dict(a.model.settings)} for p in points], cache_dir=a.cache_dir)
        rb = execute(b.path, [{"inputs": p, "settings": dict(b.model.settings)} for p in b_points], cache_dir=b.cache_dir)
    except BuildError as e:
        raise _Unverifiable(f"a model failed to run: {e}") from None
    ua, ub = a.model.outputs[ao], b.model.outputs[bo]
    ya = [r.get(ao) for r in ra]
    yb = [None if r.get(bo) is None else U.convert(r[bo], ub.unit, ua.unit, ub.scale, ua.scale) for r in rb]
    return ya, yb


def _relerr(x, y) -> float:
    if x is None or y is None:
        return math.inf
    return abs(x - y) / max(abs(x), abs(y), 1e-300)


def _gaps(rel, points, ya, yb) -> list[int]:
    """The points where either model gives no value. None of them is evidence for or against the
    relation: if every point is one, the relation cannot be tested."""
    gaps = [i for i, (x, y) in enumerate(zip(ya, yb)) if x is None or y is None]
    if points and len(gaps) == len(points):
        who = [s for s, ys in ((rel.a, ya), (rel.b, yb)) if all(v is None for v in ys)]
        raise _Unverifiable(f"{' and '.join(who) or 'one model or the other'} gives no value at any of the "
                            f"{len(points)} points tested across the regime")
    return gaps


def _gap_note(rel, points, ya, yb, gaps) -> str:
    if not gaps:
        return ""
    who = sorted({s for i in gaps for s, ys in ((rel.a, ya), (rel.b, yb)) if ys[i] is None})
    at = ", ".join(f"{k} = {v:.3g}" for k, v in sorted(points[gaps[0]].items()))
    return f"; no value from {' and '.join(who)} at {len(gaps)} of {len(points)} points (first at {at}), left out"


def _numeric_same(rel, a, b, res: RelationResult):
    pts = _samples(rel, a)
    ya_all, yb_all = _eval(rel, a, b, pts)
    gaps = _gaps(rel, pts, ya_all, yb_all)
    note = _gap_note(rel, pts, ya_all, yb_all, gaps)
    ya = [x for i, x in enumerate(ya_all) if i not in gaps]
    yb = [y for i, y in enumerate(yb_all) if i not in gaps]
    errs = [_relerr(x, y) for x, y in zip(ya, yb)]
    res.samples = len(pts)
    res.method = "numeric"
    ok = [e <= rel.tolerance for e in errs]
    _same_verdict(rel, res, ya, yb, errs, ok)
    if gaps:  # agreement on part of the regime is not agreement across it
        if res.status == "verified":
            res.status = "ambiguous"
            res.detail = f"agree at all {len(errs)} points where both give a value"
        res.detail += note


def _same_verdict(rel, res: RelationResult, ya, yb, errs, ok) -> None:
    n = len(errs)
    if all(ok):
        res.status = "verified"
        res.detail = f"agree at {n} points across the regime (max relative difference {max(errs):.2e})"
        return
    if any(ok):
        res.status = "ambiguous"
        res.detail = f"agree at {sum(ok)} of {n} points"
        return
    ratios = [x / y for x, y in zip(ya, yb) if y != 0]
    if ratios and max(ratios) - min(ratios) <= rel.tolerance * max(abs(r) for r in ratios) * 10:
        c = sum(ratios) / len(ratios)
        res.status = "not_verified"
        res.holds_instead = f"a = {c:.6g} × b: they agree up to a constant factor"
        res.detail = f"differ everywhere by a constant factor {c:.6g}"
        return
    diffs = [x - y for x, y in zip(ya, yb)]
    if diffs and max(diffs) - min(diffs) <= rel.tolerance * max(max(abs(x) for x in ya), 1e-300) * 10:
        c = sum(diffs) / len(diffs)
        res.status = "not_verified"
        res.holds_instead = f"a = b + {c:.6g}: they agree up to a constant offset"
        res.detail = "differ everywhere by a constant offset"
        return
    res.status = "refuted"
    res.detail = f"disagree at all {n} points (median relative difference {sorted(errs)[n // 2]:.2e})"


def _evaluate(expr: sp.Expr, values: dict) -> float:
    """A symbolic form's value at a point, as a real number. Exact evaluation (sympy) is used, so special
    functions (Lambert W, error functions, Bessel functions) work; a complex result is not a value."""
    v = complex(expr.evalf(subs=values, n=30))
    if abs(v.imag) > 1e-12 * max(1.0, abs(v.real)):
        raise ValueError(f"the value is complex ({v})")
    return v.real


def _symbolic_disagrees(rel, a: _Side, b: _Side, ao: str, bo: str) -> str | None:
    """Why the two models' symbolic forms cannot stand for their code, or None. A symbolic form is a
    second copy of the model: it is trusted only where it gives what run() gives, at the regime's samples."""
    ea, eb = _sym_expr(a), _sym_expr(b)
    if set(a.model.inputs) <= set(rel.regime):
        pts = _samples(rel, a, n=8)
    else:  # agreement with the code is a property of the model: probe ordinary positive values
        rng = random.Random(f"symbolic:{rel.id}:{rel.a}:{rel.b}")
        pts = [{s: (rng.uniform(*rel.regime[s]) if s in rel.regime else rng.uniform(0.5, 3.0))
                for s in a.model.inputs} for _ in range(8)]
    _, funcs = _mapping(rel, a, b)
    order = list(a.model.inputs)
    b_pts = [{bs: f(*[p[n] for n in order]) for bs, f in funcs.items()} for p in pts]
    for side, ex, out, points in ((a, ea, ao, pts), (b, eb, bo, b_pts)):
        if not ex or out not in ex:
            continue
        names = list(side.model.inputs)
        syms = _symbols(names)
        try:
            ran = execute(side.path, [{"inputs": q, "settings": dict(side.model.settings)} for q in points],
                          cache_dir=side.cache_dir)
        except BuildError as e:
            raise _Unverifiable(f"a model failed to run: {e}") from None
        for q, r in zip(points, ran):
            try:
                want = _evaluate(ex[out], {syms[n]: q[n] for n in names})
            except (ValueError, TypeError, ZeroDivisionError, OverflowError) as e:
                return f"{side.gid}: its symbolic form cannot be evaluated at {q} ({e})"
            if _relerr(want, r.get(out)) > 1e-6:
                return f"{side.gid}: its symbolic form gives {want:.6g} where its code gives {r.get(out)} at {q}"
    return None


def _symbolic_same(rel, a, b) -> tuple[bool, str | None]:
    """Whether a and b are one form under the mapping, symbolically; and a note when the symbolic forms
    were not used. Symbols are taken positive, so a regime reaching zero or below is tested numerically."""
    ea, eb = _sym_expr(a), _sym_expr(b)
    if not ea or not eb:
        return False, None
    ao, bo = _output_pair(rel, a, b)
    if ao not in ea or bo not in eb:
        return False, None
    if any(rel.regime.get(s, (1, 1))[0] <= 0 for s in a.model.inputs):
        return False, None
    exprs, _ = _mapping(rel, a, b)
    ua, ub = a.model.outputs[ao], b.model.outputs[bo]
    if ua.scale != "linear" or ub.scale != "linear":
        return False, None
    why = _symbolic_disagrees(rel, a, b, ao, bo)
    if why:
        return False, f"symbolic forms not used: {why}"
    factor = sp.nsimplify(U.convert(1.0, ub.unit, ua.unit))
    bsub = eb[bo].subs({sp.Symbol(k, positive=True): v for k, v in exprs.items()}, simultaneous=True)
    try:
        return sp.simplify(ea[ao] - factor * bsub) == 0, None
    except Exception:  # noqa: BLE001
        return False, None


def _too_plain(a: _Side, b: _Side) -> bool:
    for s in (a, b):
        e = _sym_expr(s)
        if e and all(sp.count_ops(x) <= PLAIN_OPS for x in e.values()):
            return True
    return False


def _approach(value: str, lo: float, hi: float, k: int) -> float:
    v = value.strip().lower()
    if v in ("0", "0.0"):
        return max(abs(hi), abs(lo), 1.0) * 10.0 ** (-k)
    if v in ("oo", "inf", "infinity"):
        return max(abs(hi), 1.0) * 10.0**k
    c = float(v)
    return c + (hi - lo) * 10.0 ** (-k)


def _reduces(rel, a, b, res):
    if not rel.limit:
        raise _Unverifiable("reduces_to needs a stated limit")
    pts = _samples(rel, a, n=20)
    errs_by_k = []
    note = ""
    for k in (2, 4, 6, 8):
        moved = []
        for p in pts:
            q = dict(p)
            for s, val in rel.limit.items():
                if s not in q:
                    raise _Unverifiable(f"limit names {s!r}, not an input of a")
                lo, hi = rel.regime[s]
                q[s] = _approach(val, lo, hi, k)
            moved.append(q)
        ya, yb = _eval(rel, a, b, moved)
        gaps = _gaps(rel, moved, ya, yb)
        note = note or _gap_note(rel, moved, ya, yb, gaps)
        errs_by_k.append(max(_relerr(x, y) for i, (x, y) in enumerate(zip(ya, yb)) if i not in gaps))
    res.samples = len(pts)
    res.method = "numeric limit"
    if errs_by_k[-1] <= max(rel.tolerance, 1e-6) and note:  # it holds only where both give a value
        res.status = "ambiguous"
        res.detail = f"difference falls to {errs_by_k[-1]:.1e} as {rel.limit} is approached, where both give a value"
    elif errs_by_k[-1] <= max(rel.tolerance, 1e-6):
        res.status = "verified"
        res.detail = f"difference falls to {errs_by_k[-1]:.1e} as {rel.limit} is approached"
    elif errs_by_k[-1] < errs_by_k[0]:
        res.status = "ambiguous"
        res.detail = f"difference falls ({errs_by_k[0]:.1e} → {errs_by_k[-1]:.1e}) but not within tolerance"
    else:
        res.status = "not_verified"
        res.detail = f"difference does not fall as the limit is approached ({errs_by_k})"
    res.detail += note


def _apply_step(expr: sp.Expr, step: str, loc: dict) -> sp.Expr:
    s = step.strip()
    low = s.lower()
    try:
        if low.startswith("subs:"):
            lhs, rhs = s[5:].split("=", 1)
            return expr.subs(sp.sympify(lhs.strip(), locals=loc), sp.sympify(rhs.strip(), locals=loc))
        if low.startswith("limit:"):
            lhs, rhs = s[6:].split("->", 1)
            return sp.limit(expr, sp.sympify(lhs.strip(), locals=loc), sp.sympify(rhs.strip(), locals=loc))
        if low.startswith("series:"):
            lhs, rhs = s[7:].split("->", 1)
            parts = [x.strip() for x in rhs.split(",")]
            n = int(parts[1]) if len(parts) > 1 else 2
            return sp.series(expr, sp.sympify(lhs.strip(), locals=loc), sp.sympify(parts[0], locals=loc), n).removeO()
        if low == "simplify":
            return sp.simplify(expr)
    except (ValueError, sp.SympifyError, TypeError) as e:
        raise _Unverifiable(f"step {step!r} cannot be applied: {e}") from None
    raise _Unverifiable(f"step {step!r} cannot be applied: it is not a substitution, limit, series or simplification")


def _derived(rel, a, b, res):
    if not rel.steps:
        raise _Unverifiable("derived_from needs the steps the paper gives")
    ea = _sym_expr(a)
    if not ea:
        raise _Unverifiable("the source model has no symbolic form, so its steps cannot be applied")
    ao, bo = _output_pair(rel, a, b)
    loc = _symbols(a.model.inputs)
    e = ea[ao]
    for st in rel.steps:
        e = _apply_step(e, st, loc)
    res.method = "symbolic steps"
    eb = _sym_expr(b)
    why = _symbolic_disagrees(rel, a, b, ao, bo)
    if why:
        raise _Unverifiable(f"the steps act on symbolic forms, and {why}")
    exprs, _ = _mapping(rel, a, b)
    if eb and bo in eb:
        ua, ub = a.model.outputs[ao], b.model.outputs[bo]
        factor = sp.nsimplify(U.convert(1.0, ub.unit, ua.unit))
        bsub = eb[bo].subs({sp.Symbol(k, positive=True): v for k, v in exprs.items()}, simultaneous=True)
        if sp.simplify(e - factor * bsub) == 0:
            res.status = "verified"
            res.detail = f"applying {rel.steps} to a gives b"
        else:
            res.status = "not_verified"
            res.holds_instead = f"the steps give {sp.sstr(e)}"
            res.detail = "the stated steps do not reach b"
    else:
        raise _Unverifiable("the derived model has no symbolic form to compare with")


def _scales(rel, a, b, res):
    """Compare log-slopes in the variables both models share through the mapping. A slope is taken
    at every sample where the variable is not zero; with no slope compared, nothing is verified."""
    pts = _samples(rel, a, n=12)
    exprs, _ = _mapping(rel, a, b)
    shared = sorted({sym.name for e in exprs.values() for sym in e.free_symbols})
    ya0, yb0 = _eval(rel, a, b, pts)
    worst, compared = 0.0, 0
    for s in shared:
        up = [dict(p, **{s: p[s] * 1.001}) for p in pts]
        ya1, yb1 = _eval(rel, a, b, up)
        for p, y0, y1, z0, z1 in zip(pts, ya0, ya1, yb0, yb1):
            vals = (y0, y1, z0, z1)
            if p[s] == 0 or any(v is None or not math.isfinite(v) or v == 0 for v in vals):
                continue
            sa = math.log(abs(y1 / y0)) / math.log(1.001)
            sb = math.log(abs(z1 / z0)) / math.log(1.001)
            worst = max(worst, abs(sa - sb))
            compared += 1
    res.method = "numeric log-slopes"
    res.samples = len(pts)
    if not compared:
        raise _Unverifiable(f"no log-slope could be compared: the mapping shares {shared or 'no variable'} "
                            "and every sample gave zero, a missing value or a variable at zero")
    if worst <= 1e-2:
        res.status = "verified"
        res.detail = f"log-slopes in {shared} agree at {compared} points across the regime (max difference {worst:.1e})"
    else:
        res.status = "not_verified"
        res.detail = f"log-slopes in {shared} differ by up to {worst:.2g}"


def _approx(rel, a, b, res):
    pts = _samples(rel, a)
    ya, yb = _eval(rel, a, b, pts)
    gaps = _gaps(rel, pts, ya, yb)
    err = max(_relerr(x, y) for i, (x, y) in enumerate(zip(ya, yb)) if i not in gaps)
    res.error = err
    res.method = "numeric error"
    res.samples = len(pts)
    if gaps:  # the error is measured only where both give a value
        res.status = "ambiguous" if err <= rel.tolerance else "not_verified"
        res.holds_instead = None if err <= rel.tolerance else f"max relative error is {err:.2e}"
        res.detail = (f"max relative error {err:.2e} where both give a value"
                      + _gap_note(rel, pts, ya, yb, gaps))
    elif err <= rel.tolerance:
        res.status = "verified"
        res.detail = f"max relative error {err:.2e} across the regime, within the stated {rel.tolerance:g}"
    else:
        res.status = "not_verified"
        res.holds_instead = f"max relative error is {err:.2e}"
        res.detail = f"max relative error {err:.2e} exceeds the stated {rel.tolerance:g}"


def test_relation(rel: Relation, records: dict[str, LoadedRecord], source: str | None = None,
                  cache_dir=None) -> RelationResult:
    """Test one relation. With a cache_dir, model calls are cached by code and inputs, as in a build."""
    res = RelationResult(id=rel.id, kind=rel.kind.value, a=rel.a, b=rel.b, provenance=rel.provenance.value,
                         status="pending", source=source)
    try:
        a, b = _side(rel.a, records, cache_dir), _side(rel.b, records, cache_dir)
        for side in (a, b):
            if any(p.curve for p in (*side.model.inputs.values(), *side.model.outputs.values())):
                raise _Unverifiable(f"{side.gid} takes or gives a whole curve; relations are tested on single values")
        if rel.kind == RelationKind.same_as:
            same, note = _symbolic_same(rel, a, b)
            if same:
                res.status, res.method, res.detail = "verified", "symbolic", "identical after substituting the mapping"
            else:
                _numeric_same(rel, a, b, res)
                if note:
                    res.detail = f"{res.detail}; {note}" if res.detail else note
            res.too_plain = _too_plain(a, b)
            if res.too_plain:
                res.detail += "; flagged: a form too plain to mean anything"
        elif rel.kind == RelationKind.reduces_to:
            _reduces(rel, a, b, res)
        elif rel.kind == RelationKind.derived_from:
            _derived(rel, a, b, res)
        elif rel.kind == RelationKind.scales_as:
            _scales(rel, a, b, res)
        elif rel.kind == RelationKind.approximated_by:
            _approx(rel, a, b, res)
    except _Unverifiable as e:
        res.status = "unverifiable"
        res.detail = str(e)
    except Exception as e:  # noqa: BLE001 - any failure of the test is reported on the relation, never raised
        res.status = "unverifiable"
        res.detail = f"the test could not be carried out: {type(e).__name__}: {e}"
    return res


test_relation.__test__ = False  # not a pytest test, despite the name


def families(relations, results: dict[str, RelationResult]) -> list[list[str]]:
    """What verified same-as relations join, recomputed from the whole atlas."""
    g = nx.Graph()
    for rel in relations:
        r = results.get(rel.id)
        if r and r.kind == "same_as" and r.status == "verified" and not r.too_plain:
            g.add_edge(rel.a, rel.b)
    return sorted(sorted(c) for c in nx.connected_components(g) if len(c) > 1)
