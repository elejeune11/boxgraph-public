"""Port of the released code's time-varying microvascular resistance (our code, not the release's):
OpenLoopCoronaryVarResBC::get_Ram, src/model/OpenLoopCoronaryVarResBC.cpp lines 9-38, line by line:

  t_cycle = fmod(time, cardiac_cycle_period)
  e = 0.5 (1 - cos(pi t_cycle / T_vc))           if t_cycle <= T_vc
      0.5 (1 + cos(pi (t_cycle - T_vc) / T_vr))  elif t_cycle <= T_vc + T_vr
      0                                          otherwise
  Ram = (sqrt(Ram_min) + (sqrt(Ram_max) - sqrt(Ram_min)) e)^2

The code evaluates Ram(t) at the solver's time; its time average over a cycle, which yong2025 calls
the mean microvascular resistance, is taken here by the midpoint rule on n_samples points per cycle
(a setting).
"""
import math


def get_ram(Ram_min, Ram_max, T_vc, T_vr, period, time):
    t_cycle = math.fmod(time, period)
    if t_cycle <= T_vc:
        e_t = 0.5 * (1.0 - math.cos(math.pi * t_cycle / T_vc))
    elif t_cycle <= T_vc + T_vr:
        e_t = 0.5 * (1.0 + math.cos(math.pi * (t_cycle - T_vc) / T_vr))
    else:
        e_t = 0.0
    sqrt_min = math.sqrt(Ram_min)
    sqrt_max = math.sqrt(Ram_max)
    ram_t = sqrt_min + (sqrt_max - sqrt_min) * e_t
    return ram_t * ram_t


def run(inputs, settings):
    n = int(settings.get("n_samples", 100000))
    T = inputs["T"]
    vals = [get_ram(inputs["Ram_min"], inputs["Ram_max"], inputs["T_vc"], inputs["T_vr"], T, (k + 0.5) * T / n)
            for k in range(n)]
    return {"Ram_mean": sum(vals) / n, "Ram_peak": max(vals)}
