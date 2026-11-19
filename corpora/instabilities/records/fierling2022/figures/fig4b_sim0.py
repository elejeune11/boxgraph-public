"""Fig. 4b (PDF p. 8): simulated (dashed) furrow apex position at x = 0. Reading in _fig4b.py."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig4b  # noqa: E402


def read(image, at):
    return _fig4b.read(image, at, "0")
