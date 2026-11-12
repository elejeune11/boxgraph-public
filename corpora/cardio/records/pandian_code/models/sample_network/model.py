# Adapter (software: true): the geometry of the released sample network, read from the CSV the script exported
# (matlab-scripts/Sample-Output-csv-from-test/Result-With-C-Lecia-3-p003.csv, under $BOXGRAPH_SOURCE). Our own
# code: counts, lengths, radii and the span of the segments' end points.
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("pandian_code_csv", os.path.join(_HERE, "_csv.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def run(inputs, settings):
    rs = C.rows()
    vu = inputs["voxel_unit"]
    lens = [C.length(r) for r in rs]
    groups = C.links(rs, vu)
    link_len = [sum(C.length(r) for r in g) for g in groups]
    link_r = [g[0][6] for g in groups]
    gaps = sum(math.dist(a[3:6], b[0:3]) for g in groups for a, b in zip(g, g[1:]))
    total = sum(lens)
    # length-weighted mean diameter over links (the script's link_radius_all2, line 531, weights by path length)
    d_lw = 2 * sum(r * L for r, L in zip(link_r, link_len)) / sum(link_len)
    pts = [r[0:3] for r in rs] + [r[3:6] for r in rs]
    span = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    v_box = span[0] * span[1] * span[2]
    v_cyl = sum(math.pi * r[6] ** 2 * C.length(r) for r in rs)
    return {
        "n_segments": float(len(rs)),
        "n_links": float(len(groups)),
        "L_total": total,
        "L_seg_median": C.median(lens),
        "L_seg_min": min(lens),
        "L_seg_max": max(lens),
        "L_link_median": C.median(link_len),
        "gap_total": gaps,
        "r_median": C.median(link_r),
        "D_median": 2 * C.median(link_r),
        "D_min": 2 * min(link_r),
        "D_max": 2 * max(link_r),
        "D_mean_lw": d_lw,
        "span_x": span[0],
        "span_y": span[1],
        "span_z": span[2],
        "V_cyl": v_cyl,
        "length_density_box": total / v_box * 1e6,  # um/um^3 -> mm/mm^3
        "volume_fraction_box": v_cyl / v_box,
    }
