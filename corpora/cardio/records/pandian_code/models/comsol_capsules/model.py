# Port of the COMSOL geometry construction in Code_building_geometry.rtf (see model.yaml), voxelized. Our code;
# it reads the released sample CSV through the sample_network model's reader.
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("pandian_code_csv", os.path.join(_HERE, "..", "sample_network", "_csv.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def _mark(mask, origin, dx, a, b, r):
    """Set the cells whose centres lie within r of segment a-b (a capsule)."""
    lo = np.floor((np.minimum(a, b) - r - origin) / dx).astype(int)
    hi = np.ceil((np.maximum(a, b) + r - origin) / dx).astype(int) + 1
    lo = np.maximum(lo, 0)
    hi = np.minimum(hi, mask.shape)
    if np.any(hi <= lo):
        return
    axes = [origin[i] + (np.arange(lo[i], hi[i]) + 0.5) * dx for i in range(3)]
    X, Y, Z = np.meshgrid(*axes, indexing="ij")
    P = np.stack([X, Y, Z], axis=-1)
    ab = b - a
    t = np.clip(((P - a) @ ab) / float(ab @ ab), 0.0, 1.0)
    d2 = np.sum((P - (a + t[..., None] * ab)) ** 2, axis=-1)
    sl = tuple(slice(lo[i], hi[i]) for i in range(3))
    mask[sl] |= d2 <= r * r


def run(inputs, settings):
    W, H, th, dx = inputs["W"], inputs["H"], inputs["t"], float(settings["dx"])
    rs = np.array(C.rows())
    a_all, b_all, r_all = rs[:, 0:3], rs[:, 3:6], rs[:, 6]
    # the block [0, W] x [0, W] x [0, H] (centre W/2, W/2, H/2), gridded only over the box the wide capsules reach
    reach = r_all.max() + th
    zlo = max(0.0, np.floor((min(a_all[:, 2].min(), b_all[:, 2].min()) - reach) / dx) * dx)
    zhi = min(H, max(a_all[:, 2].max(), b_all[:, 2].max()) + reach)
    origin = np.array([0.0, 0.0, zlo])
    shape = (int(np.ceil(W / dx)), int(np.ceil(W / dx)), int(np.ceil((zhi - zlo) / dx)))
    lumen = np.zeros(shape, dtype=bool)
    outer = np.zeros(shape, dtype=bool)
    for a, b, r in zip(a_all, b_all, r_all):
        _mark(lumen, origin, dx, a, b, r)
        _mark(outer, origin, dx, a, b, r + th)
    # cells cut by the block's faces: count only the part inside (the faces are at multiples of dx in x and y)
    cz = origin[2] + (np.arange(shape[2]) + 0.5) * dx
    inside_z = (cz < H).astype(float)
    cx = (np.arange(shape[0]) + 0.5) * dx
    inside_x = (cx < W).astype(float)
    wgt = inside_x[:, None, None] * inside_x[None, :, None] * inside_z[None, None, :]
    cell = dx ** 3
    v_lumen = float(np.sum(lumen * wgt)) * cell
    v_outer = float(np.sum(outer * wgt)) * cell
    v_block = W * W * H
    return {"lumen_fraction": v_lumen / v_block, "endo_fraction": (v_outer - v_lumen) / v_block, "V_lumen": v_lumen}
