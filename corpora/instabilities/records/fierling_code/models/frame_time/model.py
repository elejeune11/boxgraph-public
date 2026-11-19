# Reads the released merged statistics file from $BOXGRAPH_SOURCE and returns t_rauzi (min) of frame n. How frames
# were put on the experiments' clock is not in the release: the file only holds the result.
import os
import pathlib


def run(inputs, settings):
    lines = (pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / settings["file"]).read_text(errors="replace").splitlines()
    header = lines[0].split("\t")
    ti, fi = header.index("t_rauzi"), header.index("framecounter")
    n = int(round(inputs["n"]))
    for l in lines[1:]:
        p = l.split("\t")
        if len(p) > max(ti, fi) and p[fi].strip() == str(n):
            return {"t": float(p[ti])}
    raise ValueError(f"no frame {n} in {settings['file']}")
