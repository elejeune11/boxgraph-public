"""Supp. Fig. 3d (PDF p. 25): the line x = 200 um (black). Calibration and colours in _sf3d.py.
Black is also the frame's and the legend's colour: the rows searched (30 to 50) hold only this line
at the times read (it stays near 42 up to 9 min); the legend lies above 52.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _gp  # noqa: E402
import _sf3d  # noqa: E402


def read(image, at):
    spec = dict(_sf3d.SPEC, rgb=_sf3d.COLOURS["200"], rows=(30.0, 50.0))
    return _gp.read_lines(_sf3d._restore_ticks(image), at, spec)
