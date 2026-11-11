"""Our helper for running the released svOneDSolver (built from the code folder at commit 8939eed,
corpus/cardio/envs/oned/build/bin/OneDSolver) on a network we describe. It writes a legacy input file
with the cards of the code's docs/source/content/inputFileGuide.rst into a temporary directory, runs
the executable there and reads back its TEXT output (cvOneDBFSolver: one row per finite-element node,
the first column the initial state, then one column per saved step). Nothing of the release is copied.
"""
import math
import os
import re
import subprocess
import tempfile


def corpus_code_dir():
    """corpus/<corpus>/code, the folder that holds the code folder (and other released sources)."""
    src = os.environ.get("BOXGRAPH_SOURCE")
    if src:
        return os.path.dirname(os.path.abspath(src))
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, *[".."] * 6, "corpus", "cardio", "code"))


def exe():
    return os.path.join(os.path.dirname(corpus_code_dir()), "envs", "oned", "build", "bin", "OneDSolver")


_NUM = r"[0-9]*\.?[0-9]+(?:[eE][+-]?[0-9]+)?"
_TERM = re.compile(r"([+-]?)\s*(" + _NUM + r")\*sin\((\d+)\*PI\*t/T(?:([+-]" + _NUM + r"))?\)")


def fourier_inflow(rel_path):
    """The inflow of a Boileau benchmark (boileau_data inflow.txt): a constant plus sine terms
    a_k sin(2 pi k t / T + phi_k), parsed (not evaluated) from the file's single expression line.
    Returns a function of t (s) and the period T printed in the file's header."""
    text = open(os.path.join(corpus_code_dir(), rel_path)).read()
    T = float(re.search(r"period T=([0-9.]+)", text).group(1))
    expr = [ln for ln in text.splitlines() if ln.strip().startswith("inflow=")][0]
    body = expr.split("=", 1)[1].strip()
    factor = 1.0
    m = re.match(r"(" + _NUM + r")\*\((.*)\)$", body)   # a scale factor in front: "500*(...)", "10e5*(...)"
    if m:
        factor, body = float(m.group(1)), m.group(2)
    elif body.startswith("(") and body.endswith(")"):
        body = body[1:-1]
    const = factor * float(re.match(r"\s*(" + _NUM + ")", body).group(1))
    terms = []
    for sign, amp, k2, ph in _TERM.findall(body):
        a = factor * float(amp) * (-1.0 if sign == "-" else 1.0)
        terms.append((a, int(k2), float(ph) if ph else 0.0))

    def q(t):
        return const + sum(a * math.sin(k2 * math.pi * t / T + ph) for a, k2, ph in terms)
    return q, T, len(terms)


def solve(segments, joints, materials, inflow_table, dt, n_steps, quad_points, tolerance,
          formulation, stabilization):
    """segments: dicts with name, length, n_el, node_in, node_out, z_in, z_out, area_in, area_out, q0,
    mat, bc (NOBOUND, RESISTANCE, RCR), table (name) and table_rows (list of (t, v)) for the outlet;
    joints: (node, [inlet segment ids], [outlet segment ids]); materials: dicts with name, kind
    (LINEAR or OLUFSEN), rho, mu, p_ref, n, params; inflow_table: [(t, Q)] of one period.
    Returns {segment name: {"flow", "pressure", "area"}} as rows (nodes) of columns (t = k dt)."""
    card = ["MODEL m_"]
    seen = set()
    for s in segments:
        for nid, z in ((s["node_in"], s["z_in"]), (s["node_out"], s["z_out"])):
            if nid not in seen:
                card.append(f"NODE {nid} 0.0 0.0 {z:.12g}")
                seen.add(nid)
    for k, (node, ins, outs) in enumerate(joints):
        card.append(f"JOINT J{k} {node} IN{k} OUT{k}")
        card.append(f"JOINTINLET IN{k} {len(ins)} " + " ".join(str(i) for i in ins))
        card.append(f"JOINTOUTLET OUT{k} {len(outs)} " + " ".join(str(i) for i in outs))
    tables = []
    for i, s in enumerate(segments):
        card.append(f"SEGMENT {s['name']} {i} {s['length']:.12g} {int(s['n_el'])} {s['node_in']} {s['node_out']} "
                    f"{s['area_in']:.12g} {s['area_out']:.12g} {s['q0']:.12g} {s['mat']} NONE 0.0 0 0 "
                    f"{s['bc']} {s.get('table') or 'NONE'}")
        if s.get("table_rows"):
            tables.append(f"DATATABLE {s['table']} LIST\n" + "\n".join(f"{a:.12g} {b:.12g}" for a, b in s["table_rows"])
                          + "\nENDDATATABLE")
    card += tables
    card.append("DATATABLE INFLOW LIST\n" + "\n".join(f"{t:.12g} {q:.12g}" for t, q in inflow_table) + "\nENDDATATABLE")
    for m in materials:
        par = " ".join(f"{p:.12g}" for p in m["params"])
        card.append(f"MATERIAL {m['name']} {m['kind']} {m['rho']:.12g} {m['mu']:.12g} {m['p_ref']:.12g} {m['n']:.12g} {par}")
    card.append(f"SOLVEROPTIONS {dt:.12g} 1 {int(n_steps)} {int(quad_points)} INFLOW FLOW "
                f"{float(tolerance):.3g} {int(formulation)} {int(stabilization)}")
    card.append("OUTPUT TEXT")
    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(td, "m.in"), "w") as fh:
            fh.write("\n".join(card) + "\n")
        proc = subprocess.run([exe(), "m.in"], cwd=td, capture_output=True, text=True, timeout=900)
        if proc.returncode != 0:
            raise RuntimeError("OneDSolver failed: " + " | ".join(proc.stdout.splitlines()[-6:]))
        if "Newton not converged" in proc.stdout:
            raise RuntimeError("OneDSolver: Newton not converged at some step (the release goes on silently)")
        res = {}
        for s in segments:
            r = {}
            for f in ("flow", "pressure", "area"):
                with open(os.path.join(td, f"m_{s['name']}_{f}.dat")) as fh:
                    r[f] = [[float(x) for x in row.split()] for row in fh if row.strip()]
            res[s["name"]] = r
    return res


def at_phase(series, dt, n_steps, T, phase):
    """Value of a node's series in the last computed period, at phase in [0, T), interpolated linearly
    between saved steps (column k is t = k dt; the last period ends at column n_steps)."""
    t_end = n_steps * dt
    t = t_end - T + (phase % T)
    x = t / dt
    i = max(0, min(len(series) - 2, int(math.floor(x))))
    w = x - i
    return (1 - w) * series[i] + w * series[i + 1]
