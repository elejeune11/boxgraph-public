# Our code (software: true only to read the release from $BOXGRAPH_SOURCE): the raw skeleton
# 'Human Left Coronary skeleton.txt' (guide lines 36-56) checked against the network graph
# 'Human Left Coronary graph.mat'. The skeleton (440 MB) is streamed in blocks of lines and parsed
# with numpy; only the columns used are kept. Its layout as the file holds it:
#   line 2 the number of centre points, line 4 the number of segments, line 5 the column header,
#   then one line per centre point: ID, X Y Z (pixels), neighbour IDs (-1 = none; as many slots as the
#   line has fields beyond the 7 others), Radius (pixels; -1 at a node), Stddev, BelongstoLineSegment;
#   then the line 'SEGMENT-INFO' and one line per segment: its two end points (nodes).
# Checks:
#   counts of points and segments (header and read), neighbour slots, node points (radius -1)
#   how many network elements (TreeQ.IE, TreeQ.SE) name a skeleton segment in IDsegfile, and how many
#     of the skeleton's segments are not in the network (RCA, loose and removed segments)
#   whether each element's two nodes (TreeQ.IN/SN.IDsegfile) are the segment's two end points
#   element diameter from the skeleton: the mean of 2 * radius * pixel over the segment's centre points
#     with radius > 0 and Stddev / Radius <= CVlim (TreeQ.settings.CVlim = 1, guide line 224; a setting,
#     not an input, since it is a stated switch whose printed '1' is exact); an element
#     with no such point gets diam_if_all_0 (line 225). Compared with TreeQ.IE.d / SE.d.
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("schwarz_tree", os.path.join(_HERE, "..", "tree_table1", "_tree.py"))
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)
_CACHE = {}


def _skeleton(name, block):
    if name in _CACHE:
        return _CACHE[name]
    with open(T.source_file(name), "rb") as f:
        head = [f.readline() for _ in range(5)]
        npts_h, nseg_h = int(head[1]), int(head[3])
        first = f.readline()
        ncol = len(first.split())
        r, sd, seg = [], [], []
        pending, left = [first], npts_h - 1
        n_read = 0
        while pending:
            a = np.array(b"".join(pending).split(), dtype=np.float64).reshape(len(pending), ncol)
            r.append(a[:, ncol - 3]); sd.append(a[:, ncol - 2]); seg.append(a[:, ncol - 1].astype(np.int64))
            n_read += len(pending)
            k = min(block, left)
            pending = [f.readline() for _ in range(k)]
            left -= k
        tag = f.readline().strip()
        ends = np.array(f.read().split(), dtype=np.int64).reshape(-1, 2)
    sk = {"npts_h": npts_h, "nseg_h": nseg_h, "ncol": ncol, "n_read": n_read, "tag": tag.decode(),
          "r": np.concatenate(r), "sd": np.concatenate(sd), "seg": np.concatenate(seg), "ends": ends}
    _CACHE[name] = sk
    return sk


def run(inputs, settings):
    sk = _skeleton(settings["skeleton"], settings["block_lines"])
    t = T.load(settings["network"])
    r, sd, seg, ends = sk["r"], sk["sd"], sk["seg"], sk["ends"]
    nseg = len(ends)
    out = {"n_points_header": float(sk["npts_h"]), "n_segments_header": float(sk["nseg_h"]),
           "n_points": float(sk["n_read"]), "n_segments": float(nseg),
           "n_neighbour_slots": float(sk["ncol"] - 7), "n_node_points": float(np.sum(r == -1)),
           "n_points_unassigned": float(np.sum(seg < 0))}
    ids = np.r_[t["ie_seg"], t["se_seg"]].astype(np.int64)
    inside = (ids >= 0) & (ids < nseg)
    out["n_elements_in_skeleton"] = float(inside.sum())
    out["n_skeleton_segments_in_network"] = float(len(np.unique(ids[inside])))
    out["n_skeleton_segments_not_in_network"] = float(nseg - len(np.unique(ids[inside])))
    a, b = t["ie_nodes"][:, 0], t["ie_nodes"][:, 1]
    node_ids = np.r_[np.sort(np.c_[t["in_seg"][a], t["in_seg"][b]], 1),
                     np.sort(np.c_[t["in_seg"][t["se_node"]], t["sn_seg"][t["se_sn"]]], 1)].astype(np.int64)
    out["n_elements_same_ends"] = float(np.sum(np.all(np.sort(ends[ids], 1) == node_ids, 1)))
    pix_um = inputs["pixel"] * 1e6
    keep = (seg >= 0) & (r > 0) & (sd <= settings["CVlim"] * np.where(r > 0, r, 1.0))
    cnt = np.bincount(seg[keep], minlength=nseg)
    dsk = np.bincount(seg[keep], weights=2 * r[keep] * pix_um, minlength=nseg) / np.maximum(cnt, 1)
    dsk = np.where(cnt > 0, dsk, inputs["d0"])
    d_el = dsk[ids]
    d_net = np.r_[t["ie_d"], t["se_d"]] * 1e6
    n_ie = len(t["ie_d"])
    match = np.abs(d_el / d_net - 1) <= settings["match_rel"]
    out["n_d_match_internal"] = float(match[:n_ie].sum())
    out["n_d_match_terminal"] = float(match[n_ie:].sum())
    out["d_med_skeleton"] = float(np.median(d_el))
    return out
