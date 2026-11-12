# Port of VascAnalysis_singleChannel_NodeCoordinatesRadiusExport.m lines 46-76 (our code, not the release's).
import math


def _mround(x):
    """MATLAB round(): halves away from zero."""
    return math.floor(abs(x) + 0.5) * (1 if x >= 0 else -1)


def run(inputs, settings):
    vx = 1.0 / inputs["res_x"]  # um per pixel, as Bio-Formats reports PhysicalSizeX
    vy = 1.0 / inputs["res_y"]
    Nx, Ny, Nz = inputs["Nx"], inputs["Ny"], inputs["Nz"]
    vz = 1.0 if Nz == 1 else inputs["dz"]  # lines 50-55
    nx = inputs["nx"]  # line 64
    ny = _mround((vy / vx) * Ny / Nx * nx)  # line 65
    nz = _mround((vz / vx) * Nz / Nx * nx)  # line 66
    voxel_unit = ((vx * Nx) / nx + (vy * Ny) / ny + (vz * Nz) / nz) / 3.0  # lines 74-76
    return {"voxel_unit": voxel_unit, "ny": float(ny), "nz": float(nz),
            "grid_width": nx * voxel_unit, "grid_depth": nz * voxel_unit}
