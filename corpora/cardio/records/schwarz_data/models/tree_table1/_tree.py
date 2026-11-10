# Our own reader of the released graph 'Human Left Coronary graph.mat' (struct TreeQ; guide sections
# 3.1-3.7), shared by the third-pass models. Reads only the fields named below, once per process.
# Nothing of the file is copied into the record.
import os
import pathlib

import numpy as np

_CACHE = {}


def source_file(name):
    return pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / name


def _scal(x):
    return float(x) if np.ndim(x) == 0 else float("nan")


def load(name):
    if name in _CACHE:
        return _CACHE[name]
    import scipy.io

    m = scipy.io.loadmat(str(source_file(name)), squeeze_me=True, struct_as_record=False)
    T = m["TreeQ"]
    ie, se, IN, SN = T.IE, T.SE, T.IN, T.SN
    t = {
        "n_in": len(IN),
        "n_sn": len(SN),
        "ie_nodes": np.array([np.asarray(e.nodes, dtype=np.int64) for e in ie]) - 1,   # TreeQ.IE.nodes
        "ie_d": np.array([_scal(e.d) for e in ie]),                                     # [m]
        "ie_l": np.array([_scal(e.l) for e in ie]),                                     # [m]
        "ie_seg": np.array([_scal(e.IDsegfile) for e in ie]),
        "ie_P": np.array([_scal(e.P) for e in ie]),
        "se_node": np.array([int(e.node) for e in se], dtype=np.int64) - 1,            # TreeQ.SE.node
        "se_sn": np.array([int(e.sn) for e in se], dtype=np.int64) - 1,                # TreeQ.SE.sn
        "se_d": np.array([_scal(e.d) for e in se]),
        "se_l": np.array([_scal(e.l) for e in se]),
        "se_seg": np.array([_scal(e.IDsegfile) for e in se]),
        "se_P": np.array([_scal(e.P) for e in se]),
        "se_inlet": np.array([bool(e.isinlet) for e in se]),
        "se_Gdist": np.array([_scal(e.Gdist) for e in se]),
        "se_V": np.array([_scal(e.VVoronoi) for e in se]),                              # [m^3]
        "se_region": np.array([_scal(e.regionID) for e in se]),                         # 1..9, 0 bg
        "se_branch": np.array([_scal(e.PerfBranchID) for e in se]),
        "in_seg": np.array([_scal(n.IDsegfile) for n in IN]),
        "sn_seg": np.array([_scal(n.IDsegfile) for n in SN]),
    }
    _CACHE[name] = t
    return t


def edges_scaled(edges_um):
    """Class edges as the released tables hold them: the edge in um times 1e-6 (metres), times 1e6 again,
    so 30 becomes 29.999999999999996 and 45 becomes 44.99999999999999 (termseg_density.xlsx SegType!A2:A11).
    Elements whose diameter sits on an edge (e.g. the 30 um given to diameterless elements) fall in the
    class above only with these edges."""
    return np.array([e * 1e-6 * 1e6 for e in edges_um])


def classify(d_m, edges_um):
    """Class index 0..n-1 of each diameter (lower edge inclusive, the last class open); -1 below.
    The diameter is scaled to um in the same floating-point way (d * 1e6) before comparing."""
    return np.searchsorted(edges_scaled(edges_um), np.asarray(d_m) * 1e6, side="right") - 1


def class_index(d_um, edges_um):
    """The class whose lower bound is d_um."""
    k = [i for i, e in enumerate(edges_um) if abs(e - d_um) < 1e-6 * max(1.0, e)]
    if not k:
        raise ValueError(f"{d_um} um is not a class lower bound of {edges_um}")
    return k[0]


def stats(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return [float("nan")] * 5
    return [float(np.percentile(v, p)) for p in (10, 25, 50, 75, 90)]
