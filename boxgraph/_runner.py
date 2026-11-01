"""Executes a record's model code in a separate, isolated interpreter.

Reads a JSON request on stdin, writes a JSON reply on stdout. It imports the
model file by path and calls run(inputs, settings) for each call,
symbolic() for the atlas, or read(image, at) for a figure read by the record's code. Kept dependency-free so it can run with `python -I`.
"""

import importlib.util
import json
import math
import sys
import traceback


def _load(path):
    spec = importlib.util.spec_from_file_location("record_model", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _clean(v):
    try:
        import numpy as np  # noqa: F401

        if hasattr(v, "tolist"):
            v = v.tolist()
    except Exception:  # noqa: BLE001
        pass
    if isinstance(v, (list, tuple)):
        return [_clean(x) for x in v]
    if isinstance(v, (int, float)):
        f = float(v)
        return None if math.isnan(f) else f
    return v


def main():
    req = json.load(sys.stdin)
    reply = sys.stdout
    sys.stdout = sys.stderr  # whatever the record's code prints must not corrupt the reply
    try:
        if req.get("source"):  # a software record's model runs the source's own code from here
            import os

            os.environ["BOXGRAPH_SOURCE"] = req["source"]
        mod = _load(req["model_path"])
        if req.get("want") == "figure":
            import numpy as np

            image = np.load(req["image"])
            rs = mod.read(image, list(req["at"]))
            if not isinstance(rs, list):
                raise TypeError("read() must return a list of readings")
            out = {"ok": True, "readings": [{k: _clean(v) for k, v in dict(r).items()} for r in rs]}
        elif req.get("want") == "symbolic":
            if not hasattr(mod, "symbolic"):
                out = {"ok": True, "symbolic": None}
            else:
                exprs = mod.symbolic()
                out = {"ok": True, "symbolic": {k: str(v) for k, v in exprs.items()}}
        else:
            results = []
            for call in req["calls"]:
                r = mod.run(dict(call["inputs"]), dict(call.get("settings", {})))
                if not isinstance(r, dict):
                    raise TypeError("run() must return a dict of outputs")
                results.append({k: _clean(v) for k, v in r.items()})
            out = {"ok": True, "results": results}
    except Exception as e:  # noqa: BLE001
        out = {"ok": False, "error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-4000:]}
    json.dump(out, reply)


if __name__ == "__main__":
    main()
