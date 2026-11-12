# Reads the released sample CSV (columns x1,y1,z1,x2,y2,z2,radius, no header, um) from $BOXGRAPH_SOURCE.
# Our own code; nothing of the release is copied.
import csv
import math
import os

CSV = "matlab-scripts/Sample-Output-csv-from-test/Result-With-C-Lecia-3-p003.csv"


def rows():
    path = os.path.join(os.environ["BOXGRAPH_SOURCE"], CSV)
    out = []
    with open(path, newline="") as f:
        for r in csv.reader(f):
            if not r or not "".join(r).strip():
                continue
            v = [float(x) for x in r]
            if len(v) != 7:
                raise ValueError(f"expected 7 columns, got {len(v)}")
            out.append(v)
    return out


def length(r):
    return math.dist(r[0:3], r[3:6])


def links(rs, voxel_unit):
    """Group consecutive rows into links: the script writes a tortuous link as 2 or 5 consecutive pieces with the
    link's one radius, each piece starting one skeleton point after the previous one ends (lines 438-472). A row
    continues the previous link when it has the same radius and starts within one voxel diagonal of its end."""
    reach = math.sqrt(3) * voxel_unit * 1.01
    groups = []
    for r in rs:
        g = groups[-1] if groups else None
        if g and r[6] == g[-1][6] and math.dist(g[-1][3:6], r[0:3]) <= reach:
            g.append(r)
        else:
            groups.append([r])
    return groups


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])
