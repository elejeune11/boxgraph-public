# Port of Cell1DPublish.cpp lines 57-58 (int() truncates, as a C++ int conversion of a positive double)
# and lines 466-470 (ceil of a double, stored in an int).
import math


def run(inputs, settings):
    motor_pool, clutch_pool = inputs["motor_pool"], inputs["clutch_pool"]
    nm_max = int(motor_pool / inputs["motor_divisor"])
    nc_max = int(clutch_pool / inputs["clutch_divisor"])
    nm, nc = 1, 1
    if inputs["active_motors"] < motor_pool:
        nm = math.ceil(nm_max * (1 - inputs["active_motors"] / motor_pool))
    if inputs["active_clutches"] < clutch_pool:
        nc = math.ceil(nc_max * (1 - inputs["active_clutches"] / clutch_pool))
    return {"nm_max": nm_max, "nc_max": nc_max, "nm_new": nm, "nc_new": nc}
