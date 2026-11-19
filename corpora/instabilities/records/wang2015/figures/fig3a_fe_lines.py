"""Fig. 3A (p. 4): the dotted 'Computation' (finite element) phase boundaries; the reading
code is in _fig3.py. This module only says where each boundary is searched for (ranges of
the axes, wide enough to contain the line and no other dotted line); each fig3a_fe_*.py
reading calls one of these functions."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig3.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def fold_pd(image, at):
    """Horizontal line between fold (below) and period-double (above), searched for
    between mu_f/mu_s = 5 and 30, right of eM = 0.34."""
    return F.horizontal_line(image, at, 5, 30, 0.34, 0.59)


def pd_ridge(image, at):
    """Horizontal line between period-double (below) and ridge (above), between 300 and 3000."""
    return F.horizontal_line(image, at, 300, 3000, 0.34, 0.59)


def crease_fold(image, at):
    """Short horizontal line between crease (below) and fold (above), eM 0.36 to 0.43,
    between mu_f/mu_s = 1.0 and 1.8."""
    return F.horizontal_line(image, at, 1.0, 1.8, 0.36, 0.43)


def flat_crease(image, at):
    """Vertical line between flat (left) and crease (right), searched for in eM 0.33 to 0.37."""
    return F.vertical_line(image, at, 0.33, 0.37)


def wrinkle_upper(image, at):
    """The boundary between wrinkle (left) and fold, period-double or ridge (right),
    searched for in eM 0.29 to 0.36."""
    return F.vertical_line(image, at, 0.29, 0.36)
