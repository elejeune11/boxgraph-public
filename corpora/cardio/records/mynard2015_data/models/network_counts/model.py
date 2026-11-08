# Adapter (software: true): counts in the released Supplemental File 1 (MOESM1_1D_segments.xlsx), read from
# $BOXGRAPH_SOURCE. Our own code:
#   n_segments: rows of the sheet with a segment number in column A;
#   n_pulm_art_tree: segments of the block 'Pulmonary Arteries' downstream of LPA and RPA (column H, followed
#     segment by segment), i.e. the lobar and fractal arteries without RVot, MPA, LPA and RPA;
#   n_pulm_vein: segments of the block 'Pulmonary Veins';
#   n_junctions: points where two or more 1D segment ends meet. The outlet end of a segment is joined to the
#     inlet end of every segment its column H names, and its inlet end to the outlet end of every segment its
#     column G names (names matched ignoring case, spaces and parentheses, since the sheet writes e.g.
#     'RDICAI' for RDICA(I)); a junction is a group of two or more joined ends. Names that are not segments
#     (heart chambers, valves, 'VB:' beds) join nothing. With settings.valves_as_junctions false, the two
#     ventricular outflow connections listed beside a valve (LVot-AoRt, RVot-MPA: 'AorticValve, AoRt',
#     'PulmonaryValve, MPA') are not junctions, since a valve sits between the segments.
import importlib.util
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("mynard2015_data_sheets", os.path.join(_HERE, "_sheets.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def _norm(name):
    return re.sub(r"[()\s]", "", name).lower()


def _downstream(segs, roots):
    by = {s["C"]: s for s in segs}
    seen, stack = set(), [n for r in roots for n in S.names(by[r]["H"]) if n in by]
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack += [m for m in S.names(by[n]["H"]) if m in by]
    return seen


def run(inputs, settings):
    segs = S.segments()
    pa = [s for s in segs if s["block"] == "Pulmonary Arteries"]
    tree = _downstream(pa, ["LPA", "RPA"])
    idx = {_norm(s["C"]): s["C"] for s in segs}
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    valves = {"aorticvalve", "pulmonaryvalve"}
    for s in segs:
        find((s["C"], "in"))
        find((s["C"], "out"))
        for col, end, other in (("G", "in", "out"), ("H", "out", "in")):
            listed = S.names(s[col])
            beside_valve = any(_norm(t) in valves for t in listed)
            for t in listed:
                k = _norm(t)
                if k not in idx:
                    continue
                if beside_valve and not settings["valves_as_junctions"]:
                    continue
                union((s["C"], end), (idx[k], other))
    groups = {}
    for k in list(parent):
        groups.setdefault(find(k), []).append(k)
    # the other side of a valve connection lists the upstream segment plainly (AoRt's G is 'LVot'): drop it too
    n_j = 0
    for members in groups.values():
        if len(members) < 2:
            continue
        if not settings["valves_as_junctions"] and len(members) == 2:
            names = {m[0] for m in members}
            if names in ({"LVot", "AoRt"}, {"RVot", "MPA"}):
                continue
        n_j += 1
    return {
        "n_segments": float(len(segs)),
        "n_pulm_art_tree": float(len(tree)),
        "n_pulm_vein": float(sum(s["block"] == "Pulmonary Veins" for s in segs)),
        "n_junctions": float(n_j),
    }
