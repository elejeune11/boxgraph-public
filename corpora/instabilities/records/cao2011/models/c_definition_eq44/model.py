# Eq. 4.4: K mu lambda_1 l^2 = (mu l^2 A/lambda_W) 2 c lambda_W^2 with lambda_1 = lambda_W.
def run(inputs, settings):
    return {"c": inputs["K"] / (2.0 * inputs["A"])}


def symbolic():
    import sympy as sp
    K, A = sp.symbols("K A", positive=True)
    return {"c": K / (2 * A)}
