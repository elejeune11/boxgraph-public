# Table 6 gives each RMS difference in absolute terms and "relative to the reference model in %".
# If one reference magnitude serves a whole column, pct = rms * pct_ref / rms_ref for any two rows.


def run(inputs, settings):
    return {"pct": inputs["rms"] * inputs["pct_ref"] / inputs["rms_ref"]}


def symbolic():
    import sympy as sp
    rms, rms_ref, pct_ref = sp.symbols("rms rms_ref pct_ref", positive=True)
    return {"pct": rms * pct_ref / rms_ref}
