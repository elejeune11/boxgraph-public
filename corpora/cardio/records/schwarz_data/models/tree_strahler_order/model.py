# Our code (software: true only to read the released network from $BOXGRAPH_SOURCE): the per-order
# statistics of kassab1993's diameter-defined Strahler orders of 'Human Left Coronary graph.mat'. The
# ordering, elements and connectivity are tree_strahler's (its run_order); see that model's header.
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("schwarz_tree_strahler", os.path.join(_HERE, "..", "tree_strahler", "model.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def run(inputs, settings):
    return S.run_order(inputs, settings)
