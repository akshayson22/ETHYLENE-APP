import math
import numpy as np

def run_simulation(params):
    """
    Runs the exact same model logic as your Tkinter version.
    Returns a dict with arrays for plotting and any extra info.
    """
    # Unpack params
    Wp = float(params["Wp"])  # kg
    StorageTemperature = float(params["StorageTemperature"])  # °C
    Perforationdiamicron = float(params["Perforationdiamicron"])  # µm
    NumberofPerfo = float(params["NumberofPerfo"])
    mryan = float(params["mryan"])  # g
    Vl = float(params["Vl"])  # L
    Test_days = float(params["Test_days"])  # days

    # Error checks (identical to original)
    V_headspace_check = Vl * 1000 - (Wp / 0.001)  # mL
    errors = []
    if V_headspace_check < 100:
        errors.append("⚠︎ Headspace volume (V) must be at least 100 mL.")
    if NumberofPerfo > 200:
        errors.append("⚠︎ Number of perforations must be ≤ 200.")
    if Perforationdiamicron > 900:
        errors.append("⚠︎ Perforation diameter must be ≤ 900 microns.")
    if Wp > 6:
        errors.append("⚠︎ Weight of avocados must be ≤ 6 kg.")
    if StorageTemperature > 30:
        errors.append("⚠︎ Storage temperature must be ≤ 30°C.")
    if Test_days > 15:
        errors.append("⚠︎ Time must be ≤ 15 days.")
    if mryan > 5:
        errors.append("⚠︎ Scavenger mass must be ≤ 5 g.")

    if errors:
        return {"errors": errors}

    # Proceed with identical calculations
    Perfodiameter = Perforationdiamicron / 10000.0  # convert µm→cm? (your original divides by 10000)
    Vp = Vl * 1000.0  # mL

    density = 0.001  # kg/mL
    Vf = Wp / density  # mL
    V = Vp - Vf  # Headspace volume, mL

    # Storage parameters
    AirVelocity = 7.2  # cm s^-1
    L = 0.003  # cm

    T = StorageTemperature + 273.15  # K
    R = 8.314472  # J mol^-1 K^-1

    # O2 consumption
    ko2ref = 5.96e8
    ao2 = 0.75
    Eao2 = 36275
    ko2 = ko2ref * math.exp(-(Eao2 / (R * T)))  # mL kg^-1 h^-1

    # C2H4 production
    kc2h4ref = 1.19e12
    ac2h4 = 0.93
    Eac2h4 = 63836
    kc2h4 = kc2h4ref * math.exp(-(Eac2h4 / (R * T)))  # µL kg^-1 h^-1

    # Scavenger parameters
    Earyan = 22871.97195
    Kryanref = 0.695197
    Kryan = Kryanref * math.exp(-(Earyan / R) * ((1.0 / T) - (1.0 / 294.81)))
    qryanmax0 = 2.842475151  # L kg^-1 of scavenger
    qryanmax = qryanmax0 * (mryan / 1000.0) * (10**6) / (V / 1000.0)  # ppm

    if Perfodiameter <= 0:
        TotalTransethy = 0.0
        TotalTransoxy = 0.0
        TotalTransco2 = 0.0
    else:
        # Transmission via perforations
        Transethy = ((0.04 * AirVelocity) + (((2.4382e-6) * (T**1.81)) /
                        ((AirVelocity**0.05) * (L**0.25) * (Perfodiameter**0.8)))) * \
            (0.78539816339 * (Perfodiameter**2)) * 3600.0

        Transoxy = (((T**1.724) * 1.00909e-5) /
                    (Perfodiameter)) * (0.78539816339 * (Perfodiameter**2)) * 3600.0

        TotalTransethy = NumberofPerfo * Transethy
        TotalTransoxy = NumberofPerfo * Transoxy
        TotalTransco2 = 3.0 * TotalTransoxy  # CO2 transmission = 3×O2

    # Time grid
    dur = Test_days * 24.0  # h
    t = 1.0 / 3600.0  # h
    NS = int(dur / t)

    # Preallocate (NumPy for memory locality)
    yo2 = np.zeros(NS + 1, dtype=float)
    yc2h4 = np.zeros(NS + 1, dtype=float)
    yco2 = np.zeros(NS + 1, dtype=float)

    Ro2 = np.zeros(NS + 1, dtype=float)
    Rc2h4 = np.zeros(NS + 1, dtype=float)

    TransmissionRateOxy = np.zeros(NS + 1, dtype=float)
    TransmissionRateEthy = np.zeros(NS + 1, dtype=float)
    TransmissionRateCO2 = np.zeros(NS + 1, dtype=float)

    ChangeInOxy = np.zeros(NS + 1, dtype=float)
    ChangeInEthy = np.zeros(NS + 1, dtype=float)
    ChangeInCO2 = np.zeros(NS + 1, dtype=float)

    rro2 = np.zeros(NS + 1, dtype=float)
    epr = np.zeros(NS + 1, dtype=float)

    times = t + np.zeros(NS + 1, dtype=float)
    timesinhr = np.cumsum(times)

    # Initial conditions (moved outside the loop to speed up; logic unchanged)
    yo2[0] = 0.209  # 20.9%
    yc2h4[0] = 0.0  # 0 ppm
    yco2[0] = 0.0   # 0%

    RQ = 0.85  # same assumption

    # Local vars for speed
    V_local = V
    t_local = t
    TEO = TotalTransoxy
    TEC = TotalTransco2
    TEE = TotalTransethy
    ao2_local = ao2
    ac2h4_local = ac2h4
    ko2_local = ko2
    kc2h4_local = kc2h4

    # Core loop (same recurrence relations)
    for i in range(NS):
        # O2
        Ro2[i] = -(ko2_local * (yo2[i] ** ao2_local) * Wp * t_local / V_local)
        if Perfodiameter <= 0:
            TransmissionRateOxy[i] = 0.0
            TransmissionRateCO2[i] = 0.0
        else:
            TransmissionRateOxy[i] = (TEO * t_local * (yo2[0] - yo2[i])) / V_local
            TransmissionRateCO2[i] = (TEC * t_local * (0.0 - yco2[i])) / V_local

        ChangeInOxy[i] = Ro2[i] + TransmissionRateOxy[i]
        yo2[i + 1] = yo2[i] + ChangeInOxy[i]
        if yo2[i + 1] < 0.0:
            yo2[i + 1] = 0.0

        # CO2 (from RQ and transmission)
        ChangeInCO2[i] = (-Ro2[i] * RQ) + TransmissionRateCO2[i]
        yco2[i + 1] = yco2[i] + ChangeInCO2[i]
        if yco2[i + 1] < 0.0:
            yco2[i + 1] = 0.0

        # Ethylene
        Rc2h4[i] = (kc2h4_local * (yo2[i] ** ac2h4_local) * Wp * t_local) / (V_local / 1000.0)
        if Perfodiameter <= 0:
            TransmissionRateEthy[i] = 0.0
        else:
            TransmissionRateEthy[i] = -(TEE * t_local * (yc2h4[i] - yc2h4[0])) / V_local

        ChangeInEthy[i] = Rc2h4[i] + TransmissionRateEthy[i]
        yc2h4[i + 1] = yc2h4[i] + ChangeInEthy[i]
        if yc2h4[i + 1] < 0.0:
            yc2h4[i + 1] = 0.0

        # Rates
        rro2[i] = ko2_local * (yo2[i] ** ao2_local)
        epr[i] = kc2h4_local * (yo2[i] ** ac2h4_local)

    # Outputs
    Oxy = yo2
    Ethy = yc2h4
    CO2 = yco2
    TimeInHours = timesinhr
    TimesInDays = TimeInHours / 24.0

    # Ethylene removal with scavenger (same recursion)
    resultethy = np.zeros(len(Ethy), dtype=float)
    for i in range(1, len(Ethy)):
        resultethy[i] = (Ethy[i] - (Ethy[i - 1] - resultethy[i - 1])) * math.exp(-Kryan * t_local)

    ethyleneremovedwithtime = Ethy - resultethy

    if mryan <= 0:
        FinalEthy = Ethy.copy()
        RemainedScavengerCapacity = qryanmax  # not used but kept
        TimeAtWhichScavengerFinishedItsCapacity = None
    else:
        if ethyleneremovedwithtime[-1] <= qryanmax:
            FinalEthy = resultethy
            RemainedScavengerCapacity = qryanmax - ethyleneremovedwithtime[-1]
            TimeAtWhichScavengerFinishedItsCapacity = None
        else:
            idx = int(np.argmax(ethyleneremovedwithtime > qryanmax))
            firstpart1 = ethyleneremovedwithtime[:idx]
            secondpart1 = ethyleneremovedwithtime[idx:]
            secondpart2 = secondpart1 - qryanmax

            firstpart = resultethy[:len(firstpart1)]
            secondpart = firstpart[-1] + secondpart2
            FinalEthy = np.concatenate((firstpart, secondpart))
            RemainedScavengerCapacity = 0.0
            TimeAtWhichScavengerFinishedItsCapacity = (TimesInDays[len(firstpart1)] 
                                                       if len(TimesInDays) > len(firstpart1) 
                                                       else None)

    FinalEthy[FinalEthy < 0.0] = 0.0

    # axis limits as per your plotting
    xlim_days = Test_days

    return {
        "errors": [],
        "TimesInDays": TimesInDays,
        "Oxy_pct": Oxy * 100.0,
        "CO2_pct": CO2 * 100.0,
        "FinalEthy_ppm": FinalEthy,
        "xlim_days": xlim_days,
        "scavenger_done_day": TimeAtWhichScavengerFinishedItsCapacity,
        "rem_scavenger_capacity_ppm": RemainedScavengerCapacity,
        "qryanmax_ppm": qryanmax,
    }
