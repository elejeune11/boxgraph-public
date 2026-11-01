"""The build of one record: runs, comparisons, refinement, alternatives.

Everything here is a deterministic function of the authored record
(principles 5 and 11). Model code runs in a separate interpreter with a
timeout. Results are cached by the hash of (code, inputs, settings).
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from . import precision as P
from . import units as U
from .schema import ROLE_OUTPUT_ORIGIN, Added, Datum, Origin
from .store import LoadedRecord, model_by_id

RUNNER = Path(__file__).with_name("_runner.py")
DEFAULT_TIMEOUT = 900



ERROR_BARS = {"sem": "SEM", "sd": "SD", "ci95": "95% CI", "range": "range", "unstated": "unstated error"}

class BuildError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Values: what a node holds once the record is loaded or a run has produced it
# --------------------------------------------------------------------------


@dataclass
class Value:
    id: str
    quantity: str
    unit: str
    scale: str
    origin: str
    kind: str  # 'printed' | 'added' | 'output'
    value: float | None = None  # scalar
    printed: P.Printed | None = None
    index: list[float] | None = None  # table / curve
    index_quantity: str | None = None
    index_unit: str | None = None
    values: list[float | None] | None = None
    printed_values: list[P.Printed | None] | None = None
    conditions: dict[str, str] = field(default_factory=dict)
    run: str | None = None  # for outputs: which run made it
    se: float | None = None  # sampling error of a scalar from repeated runs of a model with randomness
    ses: list[float | None] | None = None  # the same, value by value, for a curve

    @property
    def is_table(self) -> bool:
        return self.values is not None

    def to_json(self) -> dict:
        d = {
            "id": self.id,
            "quantity": self.quantity,
            "unit": self.unit,
            "scale": self.scale,
            "origin": self.origin,
            "kind": self.kind,
        }
        if self.is_table:
            d["index"] = self.index
            d["index_unit"] = self.index_unit
            d["values"] = self.values
        else:
            d["value"] = self.value
        if self.printed is not None:
            d["printed"] = self.printed.text
        if self.run:
            d["run"] = self.run
        if self.se:
            d["se"] = self.se
        if self.ses:
            d["ses"] = self.ses
        if self.conditions:
            d["conditions"] = self.conditions
        return d


def _safe_parse(text: str) -> P.Printed | None:
    try:
        return P.parse(text)
    except P.PrintedError:
        return None


def value_from_datum(d: Datum) -> Value:
    if d.table is not None:
        idx = [_safe_parse(x) for x in d.table.index]
        vals = [_safe_parse(x) for x in d.table.values]
        return Value(
            id=d.id, quantity=d.quantity, unit=d.unit, scale=d.scale, origin=d.origin.value, kind="printed",
            index=[p.value if p else None for p in idx], index_quantity=d.table.index_quantity,
            index_unit=d.table.index_unit, values=[p.value if p else None for p in vals], printed_values=vals,
            conditions=dict(d.conditions),
        )
    p = _safe_parse(d.printed)
    return Value(id=d.id, quantity=d.quantity, unit=d.unit, scale=d.scale, origin=d.origin.value, kind="printed",
                 value=p.value if p else None, printed=p, conditions=dict(d.conditions))


def value_from_added(a: Added, override: str | None = None) -> Value:
    text = override if override is not None else a.printed
    p = _safe_parse(text)
    return Value(id=a.id, quantity=a.quantity, unit=a.unit, scale=a.scale, origin=Origin.assumed.value, kind="added",
                 value=p.value if p else None, printed=p, conditions=dict(a.conditions))


# --------------------------------------------------------------------------
# Executing model code
# --------------------------------------------------------------------------


_CACHE: dict[str, Any] = {}


def _code_bytes(path: Path) -> bytes:
    """Everything a piece of record code can load, for its cache key: the file itself, the shared
    helpers beside it (files whose names start with '_'), any other code in a model's own folder, and,
    through the models it is declared to be built from (model.yaml `built_from`), their code too."""
    out: list[bytes] = []
    seen: set[Path] = set()

    def add(p: Path) -> None:
        p = p.resolve()
        if p in seen or not p.is_file():
            return
        seen.add(p)
        out.append(p.name.encode() + b"\0" + p.read_bytes())

    def add_model_dir(d: Path) -> None:
        for f in sorted(d.glob("*.py")):
            add(f)
        spec = d / "model.yaml"
        if spec.is_file():
            try:
                built = (yaml.safe_load(spec.read_text()) or {}).get("built_from") or []
            except yaml.YAMLError:
                built = []
            for mid in sorted(built):
                if (d.parent / mid).resolve() not in seen:
                    add_model_dir(d.parent / mid)

    path = Path(path)
    add(path)
    if (path.parent / "model.yaml").is_file():
        add_model_dir(path.parent)
    else:
        for f in sorted(path.parent.glob("_*.py")):
            add(f)
    return b"\0\0".join(out)


def _cache_key(code: bytes, calls: list[dict]) -> str:
    h = hashlib.sha256(code)
    h.update(json.dumps(calls, sort_keys=True, default=str).encode())
    return h.hexdigest()


def _cache_read(cf: Path):
    """A cached result, or None when there is none or the file is cut short."""
    try:
        return json.loads(cf.read_text())
    except (OSError, ValueError):
        return None


def _cache_write(cf: Path, res) -> None:
    """Write whole or not at all: concurrent builds share the cache."""
    import os
    import tempfile

    cf.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=cf.parent, prefix=cf.name + ".tmp")
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps(res))
    os.replace(tmp, cf)


_SANDBOX: bool | None = None


def sandbox_available() -> bool:
    """Whether record code can be run without network access here: a Linux user and network
    namespace (`unshare -rn`). Checked once."""
    global _SANDBOX
    if _SANDBOX is None:
        import shutil

        try:
            _SANDBOX = bool(shutil.which("unshare")) and subprocess.run(
                ["unshare", "-rn", "true"], capture_output=True, timeout=10).returncode == 0
        except (OSError, subprocess.SubprocessError):
            _SANDBOX = False
    return _SANDBOX


def _runner_argv() -> list[str]:
    """The isolated runner: a fresh interpreter ignoring the environment and user site, and, where the
    system allows it, with no network (record code is written by agents and may come from papers)."""
    base = [sys.executable, "-I", str(RUNNER)]
    return ["unshare", "-rn", *base] if sandbox_available() else base


def execute(model_path: Path, calls: list[dict], timeout: int = DEFAULT_TIMEOUT, cache_dir: Path | None = None,
            source: Path | None = None, source_version: str | None = None) -> list[dict]:
    """Run a model's code on each call, in the isolated runner. `source` is the folder of the source's
    own code (a software record), given to the code as $BOXGRAPH_SOURCE; its version is part of the key."""
    key = _cache_key(_code_bytes(model_path) + (f"\0source:{source_version}".encode() if source else b""), calls)
    if key in _CACHE:
        if cache_dir is not None and not (cache_dir / f"{key}.json").exists():
            _cache_write(cache_dir / f"{key}.json", _CACHE[key])  # so the next process finds it too
        return _CACHE[key]
    if cache_dir is not None:
        res = _cache_read(cache_dir / f"{key}.json")
        if res is not None:
            _CACHE[key] = res
            return res
    req = {"model_path": str(model_path.resolve()), "calls": calls, "want": "run",
           "source": str(Path(source).resolve()) if source else None}
    try:
        proc = subprocess.run(
            _runner_argv(), input=json.dumps(req), capture_output=True, text=True,
            timeout=timeout, cwd=str(model_path.parent),
        )
    except subprocess.TimeoutExpired:
        raise BuildError(f"{model_path}: timed out after {timeout}s") from None
    if proc.returncode != 0 or not proc.stdout.strip():
        raise BuildError(f"{model_path}: runner failed: {proc.stderr[-2000:]}")
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise BuildError(f"the runner's reply could not be read: {proc.stdout[:300]!r}") from None
    if not out.get("ok"):
        raise BuildError(f"{model_path}: {out.get('error')}\n{out.get('trace', '')}")
    res = out["results"]
    _CACHE[key] = res
    if cache_dir is not None:
        _cache_write(cache_dir / f"{key}.json", res)
    return res


def read_with_code(code_path: Path, image, at: list[float], timeout: int = DEFAULT_TIMEOUT,
                   cache_dir: Path | None = None) -> list[dict]:
    """Run a record's figure-reading code, read(image, at), in the isolated runner."""
    import tempfile

    import numpy as np

    img_sha = hashlib.sha256(np.ascontiguousarray(image).tobytes() + str(image.shape).encode()).hexdigest()
    key = _cache_key(_code_bytes(code_path), [{"image": img_sha, "at": at, "want": "figure"}])
    if cache_dir is not None:
        cached = _cache_read(cache_dir / f"{key}.json")
        if cached is not None:
            return cached
    with tempfile.TemporaryDirectory() as td:
        np.save(Path(td) / "image.npy", image)
        req = {"model_path": str(code_path.resolve()), "want": "figure", "image": str(Path(td) / "image.npy"), "at": at}
        try:
            proc = subprocess.run(_runner_argv(), input=json.dumps(req), capture_output=True,
                                  text=True, timeout=timeout, cwd=str(code_path.parent))
        except subprocess.TimeoutExpired:
            raise BuildError(f"{code_path.name}: timed out after {timeout}s") from None
    if proc.returncode != 0 or not proc.stdout.strip():
        raise BuildError(f"{code_path.name}: runner failed: {proc.stderr[-2000:]}")
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise BuildError(f"the runner's reply could not be read: {proc.stdout[:300]!r}") from None
    if not out.get("ok"):
        raise BuildError(f"{code_path.name}: {out.get('error')}")
    res = out["readings"]
    if cache_dir is not None:
        _cache_write(cache_dir / f"{key}.json", res)
    return res


def symbolic(model_path: Path, timeout: int = 120, cache_dir: Path | None = None) -> dict[str, str] | None:
    key = _cache_key(_code_bytes(model_path), [{"want": "symbolic"}])
    if cache_dir is not None:
        cached = _cache_read(cache_dir / f"{key}.json")
        if cached is not None:
            return cached["symbolic"]
    req = {"model_path": str(model_path.resolve()), "want": "symbolic"}
    proc = subprocess.run(_runner_argv(), input=json.dumps(req), capture_output=True, text=True,
                          timeout=timeout, cwd=str(model_path.parent))
    if proc.returncode != 0 or not proc.stdout.strip():
        return None  # a failure is not cached: it may be passing
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    if not out.get("ok"):
        return None  # a failure is not cached: it may be fixed
    res = out.get("symbolic")
    if cache_dir is not None:
        _cache_write(cache_dir / f"{key}.json", {"symbolic": res})
    return res


# --------------------------------------------------------------------------
# One record's build
# --------------------------------------------------------------------------


@dataclass
class RunResult:
    id: str
    model: str
    ok: bool
    error: str | None = None
    inputs: dict[str, Any] = field(default_factory=dict)  # symbol -> value used (port unit)
    settings: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)  # symbol -> value id
    added_inputs: list[str] = field(default_factory=list)
    replicates: int = 1
    notes: list[str] = field(default_factory=list)


@dataclass
class ComparisonResult:
    id: str
    purpose: str
    computed: str
    printed: str
    ok: bool
    error: str | None = None
    computed_value: Any = None  # in printed unit/scale
    printed_text: Any = None
    difference: Any = None  # computed - printed, in printed unit/scale
    verdict: str | None = None
    per_value: list[str] | None = None
    conditions_note: str | None = None
    computed_se: Any = None  # sampling error of the computed side, in printed unit and scale


@dataclass
class RecordBuild:
    source: str
    digest: str
    values: dict[str, Value] = field(default_factory=dict)
    runs: dict[str, RunResult] = field(default_factory=dict)
    comparisons: dict[str, ComparisonResult] = field(default_factory=dict)
    refinements: dict[str, dict] = field(default_factory=dict)
    alternatives: list[dict] = field(default_factory=list)
    figures: dict[str, dict] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "source": self.source,
            "digest": self.digest,
            "values": {k: v.to_json() for k, v in sorted(self.values.items())},
            "runs": {k: vars(v) for k, v in sorted(self.runs.items())},
            "comparisons": {k: vars(v) for k, v in sorted(self.comparisons.items())},
            "refinements": dict(sorted(self.refinements.items())),
            "alternatives": self.alternatives,
            "figures": dict(sorted(self.figures.items())),
            "problems": self.problems,
            "warnings": self.warnings,
        }


def conditions_agree(a: dict[str, str], b: dict[str, str]) -> tuple[bool, list[str]]:
    """Agree when every condition both name has the same value. Returns
    (agree, notes). Values are compared as printed after whitespace
    normalisation, and numerically with units when both parse."""
    notes = []
    agree = True
    for k in sorted(set(a) | set(b)):
        if k not in a or k not in b:
            notes.append(f"condition {k!r} named by one side only")
            continue
        if _cond_equal(a[k], b[k]):
            continue
        agree = False
        notes.append(f"condition {k!r} differs: {a[k]!r} vs {b[k]!r}")
    return agree, notes


def _cond_equal(x: str, y: str) -> bool:
    if " ".join(str(x).split()).lower() == " ".join(str(y).split()).lower():
        return True
    try:
        qx, qy = U.ureg.Quantity(str(x)), U.ureg.Quantity(str(y))
        return math.isclose(qx.to_base_units().magnitude, qy.to_base_units().magnitude, rel_tol=1e-9)
    except Exception:  # noqa: BLE001
        return False


DEFAULT_REPLICATES = 5


def _mean_se(xs: list) -> tuple[float | None, float | None]:
    """Mean and standard error of repeated runs; a single run has no standard error."""
    xs = [float(x) for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not xs:
        return None, None
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, None
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var / len(xs))


def _convert_se(y, se, cv: Value, pv: Value) -> float | None:
    """A standard error carried into the printed unit and scale (linearised)."""
    if y is None or not se:
        return None
    a = U.convert(y, cv.unit, pv.unit, cv.scale, pv.scale)
    b = U.convert(y + se, cv.unit, pv.unit, cv.scale, pv.scale)
    return abs(b - a)


def parse_tolerance(text: str) -> tuple[bool, float]:
    """A refinement tolerance: '1%' (relative) or a plain number (absolute, in the output's unit)."""
    tol = str(text).strip()
    try:
        return (True, float(tol[:-1]) / 100) if tol.endswith("%") else (False, float(tol))
    except ValueError:
        raise ValueError(f"tolerance {text!r} is neither a percentage such as '1%' nor a plain number "
                         "in the output's unit") from None


def _index_mismatch(cv: Value, pv: Value) -> str | None:
    """Why two curves cannot be compared point by point, or None: they must be indexed by the same
    quantity at the same x values (after unit conversion), in the same order."""
    if not pv.index or not cv.index:
        return None if not pv.index and not cv.index else "one curve has x values and the other has none"
    if cv.index_quantity != pv.index_quantity:
        return f"the curves are indexed by different quantities: {cv.index_quantity!r} vs {pv.index_quantity!r}"
    xs = [None if x is None else U.convert(x, cv.index_unit, pv.index_unit) for x in cv.index]
    for a, b in zip(xs, pv.index):
        if a is None or b is None:
            continue
        if abs(a - b) > 1e-9 * max(abs(a), abs(b), 1e-300):
            return (f"the curves are at different x values: computed at {cv.index} {cv.index_unit}, "
                    f"printed at {pv.index} {pv.index_unit}")
    return None


class Builder:
    def __init__(self, lr: LoadedRecord, cache_dir: Path | None = None, timeout: int = DEFAULT_TIMEOUT):
        self.lr = lr
        self.rec = lr.record
        self.cache_dir = cache_dir
        self.timeout = timeout
        self.figures = {f.id: f for f in self.rec.figures}
        self.figure_results: dict[str, dict] = {}

    # -- values -----------------------------------------------------------
    def _base_values(self, overrides: dict[str, str] | None = None) -> dict[str, Value]:
        vals: dict[str, Value] = {}
        for d in self.rec.data:
            vals[d.id] = self._figure_value(d) if d.figure else value_from_datum(d)
        for a in self.rec.added:
            vals[a.id] = value_from_added(a, (overrides or {}).get(a.id))
        return vals

    # -- figures -----------------------------------------------------------
    def _page_image(self, fr):
        from . import digitize as D

        pdf = self.lr.source_file()
        if pdf is None:
            raise BuildError(f"figure {fr.id}: the source file {self.rec.source.file!r} was not found")
        key = hashlib.sha256(f"{pdf.stat().st_size}:{pdf.stat().st_mtime_ns}:{pdf}:{fr.page}:{fr.dpi}:{tuple(fr.crop)}"
                             .encode()).hexdigest()[:24]
        if self.cache_dir is not None:
            f = self.cache_dir / "pages" / f"{key}.png"
            if f.exists():
                try:
                    return D.load_image(f)
                except Exception:  # cut short by a concurrent writer: render again
                    pass
        img = D.render(pdf, fr.page, dpi=fr.dpi, crop=tuple(fr.crop))
        if self.cache_dir is not None:
            import os
            import tempfile

            from PIL import Image

            (self.cache_dir / "pages").mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=self.cache_dir / "pages", prefix=f"{key}.tmp", suffix=".png")
            os.close(fd)
            Image.fromarray(img).save(tmp)
            os.replace(tmp, self.cache_dir / "pages" / f"{key}.png")
        return img

    def read_figure(self, fid: str, overlay_to=None) -> dict:
        """Read a figure from its page, applying its recorded calibration."""
        if fid in self.figure_results and overlay_to is None:
            return self.figure_results[fid]
        from . import figures as FG

        fr = self.figures[fid]
        out = overlay_to
        if out is None and self.cache_dir is not None:
            out = self.cache_dir.parent / "figures" / self.rec.source.id / f"{fid}.png"
        reader = None
        if fr.mode == "code" and fr.code:
            def reader(img, at, _p=self.lr.path / fr.code):
                return read_with_code(_p, img, at, cache_dir=self.cache_dir)
        try:
            res = FG.apply(fr, self._page_image(fr), overlay_to=out, code_reader=reader)
        except (BuildError, subprocess.CalledProcessError, OSError) as e:
            res = {"id": fid, "where": fr.where, "what": fr.what, "page": fr.page, "readings": [], "errors": [str(e)],
                   "notes": []}
        self.figure_results[fid] = res
        return res

    def _figure_value(self, d: Datum) -> Value:
        v = Value(id=d.id, quantity=d.quantity, unit=d.unit, scale=d.scale, origin=d.origin.value, kind="printed",
                  index=[], values=[], printed_values=[], conditions=dict(d.conditions))
        fr = self.figures.get(d.figure)
        if fr is None:
            return v
        res = self.read_figure(fr.id)
        v.index_quantity, v.index_unit = fr.x.quantity, fr.x.unit
        for r in res["readings"]:
            v.index.append(r["x"])
            if not r["found"]:
                v.values.append(None)
                v.printed_values.append(None)
                continue
            bars = r.get("bar_lo") is not None
            # a measured value with error bars: the bar, widened by how precisely its ends were read,
            # is its printed interval; otherwise the reading's own precision is
            lo_k, hi_k = ("bar_lo_outer", "bar_hi_outer") if bars else ("lo", "hi")
            if bars and (r.get(lo_k) is None or r.get(hi_k) is None):
                lo_k, hi_k = "bar_lo", "bar_hi"  # a reading that gives only the bar's ends
            try:
                y, lo, hi = (U.convert(q, fr.y.unit, d.unit, "linear", d.scale) for q in (r["y"], r[lo_k], r[hi_k]))
            except U.UnitError:
                v.values.append(None)
                v.printed_values.append(None)
                continue
            lo, hi = min(lo, hi), max(lo, hi)
            v.values.append(y)
            what = f" ({ERROR_BARS.get(fr.error_bars, 'unstated kind of')} bar)" if bars else ""
            if fr.mode == "code":
                what += " read by the record's code"
            v.printed_values.append(P.Printed(f"{y:.4g} [{lo:.4g}, {hi:.4g}]{what} read from {fr.where}", y, lo, hi,
                                              "figure"))
        return v

    def _run_order(self) -> list:
        """Topological order of runs: a run whose input is another run's output goes after it."""
        produced = {}
        for r in self.rec.runs:
            for oid in r.outputs.values():
                produced[oid] = r.id
        deps = {r.id: {produced[i] for i in r.inputs.values() if i in produced} for r in self.rec.runs}
        order, done = [], set()
        runs = {r.id: r for r in self.rec.runs}
        while len(done) < len(runs):
            ready = sorted(rid for rid in runs if rid not in done and deps[rid] <= done)
            if not ready:
                raise BuildError(f"{self.rec.source.id}: runs form a cycle: {sorted(set(runs) - done)}")
            for rid in ready:
                order.append(runs[rid])
                done.add(rid)
        return order

    def _port_value(self, v: Value, port, symbol: str, run_id: str) -> float:
        if v.quantity != port.quantity:
            raise BuildError(f"run {run_id}: input {symbol} expects quantity {port.quantity!r}, got {v.id} measuring {v.quantity!r}")
        if v.value is None:
            raise BuildError(f"run {run_id}: input {symbol} ({v.id}) has no readable value")
        return U.convert(v.value, v.unit, port.unit, v.scale, port.scale)

    def _do_run(self, run, vals: dict[str, Value], settings_override: dict | None = None) -> tuple[RunResult, dict[str, Value]]:
        model = model_by_id(self.lr, run.model)
        res = RunResult(id=run.id, model=run.model, ok=False)
        if model is None:
            res.error = f"unknown model {run.model}"
            return res, {}
        if not model.runnable:
            res.error = f"model {model.id} is not runnable: {model.not_runnable_reason}"
            return res, {}
        path = self.lr.model_code.get(model.id)
        if path is None:
            res.error = f"model {model.id} has no model.py"
            return res, {}
        missing = set(model.inputs) - set(run.inputs) - set(run.sweep)
        extra = (set(run.inputs) | set(run.sweep)) - set(model.inputs)
        if missing or extra:
            res.error = f"inputs do not match model {model.id}: missing {sorted(missing)}, unknown {sorted(extra)}"
            return res, {}
        settings = dict(model.settings)
        settings.update(run.settings)
        if settings_override:
            settings.update(settings_override)
        res.settings = settings
        try:
            base_inputs = {}
            for sym, vid in run.inputs.items():
                if vid not in vals:
                    raise BuildError(f"run {run.id}: input {sym} refers to unknown {vid}")
                v = vals[vid]
                if v.kind == "added":
                    res.added_inputs.append(vid)
                base_inputs[sym] = self._port_value(v, model.inputs[sym], sym, run.id)
            res.inputs = dict(base_inputs)
            sweep_index = None
            if run.sweep:
                if len(run.sweep) != 1:
                    raise BuildError(f"run {run.id}: only one sweep input is supported")
                (ssym, sid), = run.sweep.items()
                tv = vals.get(sid)
                if tv is None or not tv.is_table:
                    raise BuildError(f"run {run.id}: sweep {ssym} needs a table datum, got {sid}")
                port = model.inputs[ssym]
                if tv.index_quantity != port.quantity:
                    raise BuildError(f"run {run.id}: sweep {ssym} expects {port.quantity!r}, table {sid} is indexed by {tv.index_quantity!r}")
                sweep_index = [U.convert(x, tv.index_unit, port.unit, "linear", port.scale) for x in tv.index]
                points = [{**base_inputs, ssym: x} for x in sweep_index]
                res.inputs[ssym] = {"sweep_of": sid, "values": sweep_index}
            else:
                points = [base_inputs]
            n_rep = run.replicates or (DEFAULT_REPLICATES if model.stochastic else 1)
            if n_rep > 1 and "seed" not in settings:
                raise BuildError(f"run {run.id}: repeating model {model.id} needs a `seed` setting")
            res.replicates = n_rep
            seeds = [settings["seed"] + k for k in range(n_rep)] if n_rep > 1 else [None]
            calls = [{"inputs": pt, "settings": settings if s is None else {**settings, "seed": s}}
                     for pt in points for s in seeds]
            source = self.lr.source_file() if model.software else None
            flat = execute(path, calls, timeout=self.timeout, cache_dir=self.cache_dir, source=source,
                           source_version=self.rec.source.version)
            results = [flat[i * n_rep:(i + 1) * n_rep] for i in range(len(points))]  # per point, per seed
        except (BuildError, U.UnitError) as e:
            res.error = str(e)
            return res, {}
        origin = Origin.run.value if model.software else ROLE_OUTPUT_ORIGIN[model.role].value
        seen_cond: dict[str, set[str]] = {}
        for vid in run.inputs.values():
            for k, c in vals[vid].conditions.items():
                seen_cond.setdefault(k, set()).add(str(c))
        # inputs that disagree on a condition give a mixed one, which no single value agrees with
        cond = {k: " | ".join(sorted(cs)) for k, cs in sorted(seen_cond.items())}
        res.notes += [f"inputs disagree on {k}: {cond[k]}" for k in cond if len(seen_cond[k]) > 1]
        new: dict[str, Value] = {}
        for sym, port in model.outputs.items():
            oid = run.outputs.get(sym, f"{run.id}.{sym}")
            res.outputs[sym] = oid
            if any(isinstance(r.get(sym), list) for reps in results for r in reps):
                res.error = f"output {sym} is a list; use a sweep to produce a curve"
                return res, {}
            stats = [_mean_se([r.get(sym) for r in reps]) for reps in results]
            if sweep_index is not None:
                tv = vals[run.sweep[next(iter(run.sweep))]]
                new[oid] = Value(id=oid, quantity=port.quantity, unit=port.unit, scale=port.scale, origin=origin,
                                 kind="output", index=list(tv.index), index_quantity=tv.index_quantity,
                                 index_unit=tv.index_unit, values=[m for m, _ in stats], conditions=cond, run=run.id,
                                 ses=[s for _, s in stats] if n_rep > 1 else None)
            else:
                m, s = stats[0]
                new[oid] = Value(id=oid, quantity=port.quantity, unit=port.unit, scale=port.scale, origin=origin,
                                 kind="output", value=m, conditions=cond, run=run.id, se=s if n_rep > 1 else None)
        res.ok = True
        return res, new

    def _compare(self, c, vals: dict[str, Value]) -> ComparisonResult:
        r = ComparisonResult(id=c.id, purpose=c.purpose.value, computed=c.computed, printed=c.printed, ok=False)
        cv, pv = vals.get(c.computed), vals.get(c.printed)
        if cv is None or pv is None:
            r.error = f"missing {'computed ' + c.computed if cv is None else ''} {'printed ' + c.printed if pv is None else ''}".strip()
            return r
        if cv.quantity != pv.quantity:
            r.error = f"quantities differ: {cv.quantity!r} vs {pv.quantity!r}"
            return r
        agree, notes = conditions_agree(cv.conditions, pv.conditions)
        if notes:
            r.conditions_note = "; ".join(notes)
        if not agree and not c.conditions_ok:
            r.error = f"conditions disagree and no label says why they may be compared: {r.conditions_note}"
            return r
        try:
            if pv.is_table:
                if not cv.is_table:
                    r.error = "printed value is a table; computed is a scalar"
                    return r
                if len(cv.values) != len(pv.values):
                    r.error = "table lengths differ"
                    return r
                mismatch = _index_mismatch(cv, pv)
                if mismatch:
                    r.error = mismatch
                    return r
                comp = [None if y is None else U.convert(y, cv.unit, pv.unit, cv.scale, pv.scale) for y in cv.values]
                ses = [_convert_se(y, s, cv, pv) for y, s in zip(cv.values, cv.ses or [None] * len(cv.values))]
                diffs, per = [], []
                for y, pp, s in zip(comp, pv.printed_values, ses):
                    if pp is None:
                        diffs.append(None)
                        per.append(P.Verdict.no_verdict.value)
                        continue
                    diffs.append(None if y is None else y - pp.value)
                    per.append(P.verdict(y, pp, se=s or 0.0).value)
                if cv.ses:
                    r.computed_se = ses
                r.computed_value = comp
                r.printed_text = [p.text if p else None for p in pv.printed_values]
                r.difference = diffs
                r.per_value = per
                r.verdict = P.combine([P.Verdict(v) for v in per]).value
            else:
                if cv.value is None:
                    r.error = "computed value is missing"
                    return r
                y = U.convert(cv.value, cv.unit, pv.unit, cv.scale, pv.scale)
                se = _convert_se(cv.value, cv.se, cv, pv)
                r.computed_value = y
                r.computed_se = se
                r.printed_text = pv.printed.text if pv.printed else None
                if pv.printed is None:
                    r.verdict = P.Verdict.no_verdict.value
                else:
                    r.difference = y - pv.printed.value
                    r.verdict = P.verdict(y, pv.printed, se=se or 0.0).value
        except U.UnitError as e:
            r.error = str(e)
            return r
        r.ok = True
        return r

    def evaluate(self, overrides: dict[str, str] | None = None) -> tuple[dict[str, Value], dict[str, RunResult], dict[str, ComparisonResult]]:
        vals = self._base_values(overrides)
        runs: dict[str, RunResult] = {}
        for run in self._run_order():
            rr, new = self._do_run(run, vals)
            runs[run.id] = rr
            for k, v in new.items():
                if k in vals:
                    rr.ok = False
                    rr.error = f"output id {k} collides with an existing node"
                vals[k] = v
        comps = {c.id: self._compare(c, vals) for c in self.rec.comparisons}
        return vals, runs, comps

    def _refine(self, ref, vals: dict[str, Value]) -> dict:
        run = next((r for r in self.rec.runs if r.id == ref.run), None)
        out = {"id": ref.id, "run": ref.run, "setting": ref.setting, "factors": ref.factors, "mode": ref.mode,
               "output": ref.output, "tolerance": ref.tolerance, "tolerance_basis": ref.tolerance_basis,
               "tolerance_added": ref.tolerance_added}
        if run is None:
            out["error"] = f"unknown run {ref.run}"
            return out
        model = model_by_id(self.lr, run.model)
        base = dict(model.settings) if model else {}
        base.update(run.settings)
        if ref.setting not in base:
            out["error"] = f"setting {ref.setting!r} is not a setting of run {run.id}"
            return out
        series = []
        for f in ref.factors:
            s0 = base[ref.setting]
            sv = s0 / f if ref.mode == "divide" else s0 * f
            if isinstance(s0, int) and ref.mode == "multiply":
                sv = int(round(sv))
            rr, new = self._do_run(run, vals, {ref.setting: sv})
            if not rr.ok:
                out["error"] = rr.error
                return out
            oid = rr.outputs.get(ref.output)
            v = new.get(oid)
            if v is None:
                out["error"] = f"run {run.id} has no output {ref.output!r}"
                return out
            value = v.values if v.is_table else v.value
            if value is None or (isinstance(value, list) and all(x is None for x in value)):
                out["error"] = f"run {run.id} gave no value for {ref.output!r} at {ref.setting} = {sv}"
                return out
            series.append({"factor": f, "setting": sv, "value": value})
        out["series"] = series
        try:
            rel, tval = parse_tolerance(ref.tolerance)
        except ValueError as e:
            out["error"] = str(e)
            return out

        def dist(a, b):
            if isinstance(a, list):
                ds = [dist(x, y) for x, y in zip(a, b) if x is not None and y is not None]
                return max(ds) if ds else float("nan")
            if rel:
                return abs(a - b) / max(abs(b), 1e-300)
            return abs(a - b)

        steps = [dist(series[i]["value"], series[i - 1]["value"]) for i in range(1, len(series))]
        out["changes"] = steps
        settled = bool(steps) and steps[-1] <= tval
        out["settles"] = settled
        # principle 8: the paper's result is the value at the paper's own setting (factor 1).
        # It belongs to the model only if the series settles AND that value is within the
        # tolerance of where the series settles; a result that changes as it is refined
        # belongs to the numerics, even if it settles somewhere else.
        first = next((x for x in series if x["factor"] == 1), series[0])
        out["shift"] = dist(first["value"], series[-1]["value"])
        out["belongs_to"] = "model" if settled and out["shift"] <= tval else "numerics"
        return out

    def build(self) -> RecordBuild:
        b = RecordBuild(source=self.rec.source.id, digest=self.lr.digest())
        vals, runs, comps = self.evaluate()
        for fid in sorted(self.figures):
            res = self.read_figure(fid)
            b.figures[fid] = res
            b.problems += [f"figure {fid}: {e}" for e in res["errors"]]
            b.warnings += [f"figure {fid}: {n}" for n in res["notes"]]
        b.values, b.runs, b.comparisons = vals, runs, comps
        for rr in runs.values():
            if not rr.ok:
                b.problems.append(f"run {rr.id}: {rr.error}")
            b.warnings += [f"run {rr.id}: {n}" for n in rr.notes]
        for cr in comps.values():
            if not cr.ok:
                b.problems.append(f"comparison {cr.id}: {cr.error}")
        for ref in self.rec.refinements:
            b.refinements[ref.id] = self._refine(ref, vals)
            if "error" in b.refinements[ref.id]:
                b.problems.append(f"refinement {ref.id}: {b.refinements[ref.id]['error']}")
        # alternatives of added inputs: one at a time (06 decision), only those used by some run
        used = {vid for r in self.rec.runs for vid in r.inputs.values()}
        for a in sorted(self.rec.added, key=lambda x: x.id):
            if a.id not in used:
                continue
            for alt in sorted(a.alternatives, key=str):
                _, aruns, acomps = self.evaluate({a.id: alt})
                changes = []
                for cid, cr in sorted(comps.items()):
                    ac = acomps.get(cid)
                    if ac is None:
                        continue
                    if ac.verdict != cr.verdict:
                        changes.append({"comparison": cid, "baseline": cr.verdict, "alternative": ac.verdict,
                                        "computed": ac.computed_value})
                b.alternatives.append({"added": a.id, "baseline": a.printed, "alternative": alt,
                                       "verdict_changes": changes,
                                       "failed_runs": sorted(r.id for r in aruns.values() if not r.ok)})
        return b
