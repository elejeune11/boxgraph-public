# Adapter for the released svOneDSolver (corpus/cardio/envs/oned/build/bin/OneDSolver, built from
# svoned_code at commit 8939eed). It writes a legacy input file (cards as in the code's
# docs/source/content/inputFileGuide.rst) into a temporary directory, runs the executable there and
# reads back its TEXT output: one row per finite-element node, the first column the initial state
# (t = 0) and then one column per saved time step. Nothing of the release is copied: the inflow
# waveform is read at run time from the release file a model's settings name.
import math
import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
EXE = ROOT / "corpus" / "cardio" / "envs" / "oned" / "build" / "bin" / "OneDSolver"
MMHG = 1333.22368  # dyn/cm^2 per mmHg


def read_table(rel_path, name):
    """A LIST data table of a legacy input file: [(t, value), ...]."""
    lines = (ROOT / rel_path).read_text().splitlines()
    i0 = [i for i, ln in enumerate(lines) if ln.split()[:3] == ["DATATABLE", name, "LIST"]][0]
    out = []
    for ln in lines[i0 + 1:]:
        if ln.strip() == "ENDDATATABLE":
            break
        if ln.strip():
            a, b = ln.split()[:2]
            out.append((float(a), float(b)))
    return out


def solve(segments, joints, material, inflow, settings):
    """segments: list of dicts (name, length, n_el, node_in, node_out, area_in, area_out, q0, bc, table);
    joints: list of (node, [inlet segment ids], [outlet segment ids]); material: dict rho, mu, p_ref, n,
    k1, k2, k3 (cgs); inflow: [(t, Q)] of one period. Returns {segment name: {"flow", "pressure"}} with
    rows = nodes and columns = t = 0, dt, 2 dt, ..., and the time step dt."""
    T = inflow[-1][0]
    spc = int(settings["steps_per_cycle"])
    ncyc = int(settings["n_cycles"])
    dt = T / spc
    nodes = sorted({(s["node_in"], s.get("z_in", 0.0)) for s in segments} | {(s["node_out"], s.get("z_out", 0.0)) for s in segments})
    card = ["MODEL m_"]
    seen = set()
    for nid, z in nodes:
        if nid not in seen:
            card.append(f"NODE {nid} 0.0 0.0 {z:.10g}")
            seen.add(nid)
    for k, (node, ins, outs) in enumerate(joints):
        card.append(f"JOINT J{k} {node} IN{k} OUT{k}")
        card.append(f"JOINTINLET IN{k} {len(ins)} " + " ".join(str(i) for i in ins))
        card.append(f"JOINTOUTLET OUT{k} {len(outs)} " + " ".join(str(i) for i in outs))
    tables = []
    for i, s in enumerate(segments):
        card.append(f"SEGMENT {s['name']} {i} {s['length']:.10g} {int(s['n_el'])} {s['node_in']} {s['node_out']} "
                    f"{s['area_in']:.10g} {s['area_out']:.10g} {s['q0']:.10g} MAT1 NONE 0.0 0 0 {s['bc']} {s['table'] or 'NONE'}")
        if s["bc"] == "RESISTANCE":
            tables.append(f"DATATABLE {s['table']} LIST\n0.0 {s['R']:.10g}\nENDDATATABLE")
    card += tables
    card.append("DATATABLE INFLOW LIST\n" + "\n".join(f"{t:.10g} {q:.10g}" for t, q in inflow) + "\nENDDATATABLE")
    m = material
    card.append(f"MATERIAL MAT1 OLUFSEN {m['rho']:.10g} {m['mu']:.10g} {m['p_ref']:.10g} {m['n']:.10g} "
                f"{m['k1']:.10g} {m['k2']:.10g} {m['k3']:.10g}")
    card.append(f"SOLVEROPTIONS {dt:.12g} 1 {spc * ncyc} {int(settings['quad_points'])} INFLOW FLOW "
                f"{float(settings['tolerance']):.3g} {int(settings['formulation'])} {int(settings['stabilization'])}")
    card.append("OUTPUT TEXT")
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "m.in").write_text("\n".join(card) + "\n")
        proc = subprocess.run([str(EXE), "m.in"], cwd=td, capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            tail = [ln for ln in proc.stdout.splitlines()[-5:]]
            raise RuntimeError("OneDSolver failed: " + " | ".join(tail))
        res = {}
        for s in segments:
            r = {}
            for f in ("flow", "pressure"):
                rows = (Path(td) / f"m_{s['name']}_{f}.dat").read_text().split("\n")
                r[f] = [[float(x) for x in row.split()] for row in rows if row.strip()]
            res[s["name"]] = r
    return res, dt, T, spc, ncyc


def last_cycle(series, spc):
    """The last cycle of a node's series, from phase 0 (end of the previous cycle) to phase T."""
    return series[-(spc + 1):]


def peak_time(y, dt):
    """Phase of the largest value, refined by a parabola through it and its two neighbours."""
    k = max(range(len(y)), key=lambda i: y[i])
    if 0 < k < len(y) - 1:
        a, b, c = y[k - 1], y[k], y[k + 1]
        den = a - 2 * b + c
        if den != 0:
            return (k + 0.5 * (a - c) / den) * dt
    return k * dt


def at_phase(y, dt, t):
    """Linear interpolation of a last-cycle series at phase t."""
    x = t / dt
    i = max(0, min(len(y) - 2, int(math.floor(x))))
    w = x - i
    return (1 - w) * y[i] + w * y[i + 1]


def cycle_mean(y):
    """Trapezoidal mean over a last-cycle series sampled from phase 0 to T."""
    n = len(y) - 1
    return (0.5 * y[0] + sum(y[1:-1]) + 0.5 * y[-1]) / n
