# Reads one value per row of cells from a released one-line .gdat in $BOXGRAPH_SOURCE, as area_AP_DV_paper.plot
# plots Fig. 3b: by column name (stripe_i_norm, Area_i) or by gnuplot column number offset + i.
import os
import pathlib


def run(inputs, settings):
    lines = [l for l in (pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / settings["file"]).read_text(errors="replace").splitlines()
             if l.strip() and not l.startswith("#")]
    header, values = lines[0].split("\t"), lines[1].split("\t")
    i = int(round(inputs["row"]))
    name = settings.get("name") or ""
    if name:
        k = header.index(name.replace("{i}", str(i)))
    else:
        k = int(settings["offset"]) + i - 1  # gnuplot column(offset + i) is 1-based
    return {"y": float(values[k])}
