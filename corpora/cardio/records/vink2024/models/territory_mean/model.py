# Equal-weight mean of three territory MBVs (mL/mL) at each study state present in all three curves.
# The paper averages all ROIs; equal territory weights are this record's choice (q_territory_weights).


def run(inputs, settings):
    cur = [{round(x): y for x, y in zip(inputs[k]["x"], inputs[k]["y"])} for k in ("LAD", "RCA", "CX")]
    xs = sorted(set(cur[0]) & set(cur[1]) & set(cur[2]))
    return {"MBV": {"x": [float(k) for k in xs], "y": [sum(c[k] for c in cur) / 3.0 for k in xs]}}
