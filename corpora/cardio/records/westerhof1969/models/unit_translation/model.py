MMHG_DYN_CM2 = 1333.22387415  # 1 mmHg in dyn cm^-2 (g cm^-1 s^-2)


def run(inputs, settings):
    kp = inputs["kp"] / MMHG_DYN_CM2  # volts per dyn cm^-2 (per b)
    kq, kt = inputs["kq"], inputs["kt"]  # amperes per cm3/s (per b); electric s per real s
    return {
        "kR": kp / kq,          # ohm per g cm^-4 s^-1
        "kL": kp * kt / kq,     # henry per g cm^-4
        "kC": kq * kt / kp,     # farad per g^-1 cm^4 s^2
        "kV": kq * kt,          # coulomb per cm^3 (per b)
    }
