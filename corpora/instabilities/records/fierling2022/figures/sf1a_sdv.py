"""Supp. Fig. 1a (PDF p. 23): the purple line sigma_DV against the pre-stress sigma_a (main panel).
Calibration in _sf1a.py; colour dark violet (148, 0, 211).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _sf1a  # noqa: E402


def read(image, at):
    return _sf1a.read(image, at, (148, 0, 211))
