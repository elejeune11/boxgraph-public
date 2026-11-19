"""Supp. Fig. 1e (PDF p. 23): the dashed navy 'Actual DV size' line (see sf1e_lines.py)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig2a  # noqa: E402
import sf1e_lines  # noqa: E402


def read(image, at):
    return sf1e_lines.read_colour(image, at, _fig2a.DBLUE, (0.45, 1.12))
