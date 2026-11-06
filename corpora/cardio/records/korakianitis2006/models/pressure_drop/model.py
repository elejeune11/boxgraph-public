def run(inputs, settings):
    return {"drop": inputs["P_normal"] - inputs["P_case"]}


def symbolic():
    import sympy as sp
    P_normal, P_case = sp.symbols("P_normal P_case", positive=True)
    return {"drop": P_normal - P_case}
