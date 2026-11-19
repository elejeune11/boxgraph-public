"""figS10f_Em

Read by the shared code in _common.py; the panel's tick labels, colour and exclusions are its entry
in _specs.py.
"""
import importlib.util
from pathlib import Path

ID = "figS10f_Em"


def read(image, at):
    s = importlib.util.spec_from_file_location("savin2011_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    return mod.read_id(image, at, ID)
