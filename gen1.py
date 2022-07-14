# ## First Generation Estimation

# - [x] start by generating the curves for each of the sample k parameters using zsoc.py
# - [x] Generate a full discharge curve (no noise) for a battery with matching k parameters to the sample curves
# - [ ] for each of the sample curves, and the sample curve, determine the rate of change throughout the curve
# - [ ] the best guess for which curve is the best fit is the one with the closest rate of change to the sample curve

# - The first guess can be using Vo from the simulator, for a perfect-match test case
# - The second run can be using Vout, the saggy loaded discharge curve

import src.zsoc as zsoc
import matplotlib.pyplot as plt
from src.BattSim.BattSim import BattSim
import src.BattSim.CurrentSIM as CurrentSIM
import numpy as np

# generate the curves for each of the sample k parameters using zsoc.py
INPUTFILE = 'res/K_para.csv'
batteries = zsoc.generate_curves(INPUTFILE, verbose=False, generate_csv=False, resolution=200)

# pick a random battery and create a battery object for it
# Kbatt: list, Cbatt: float, R0: float, R1: float, C1: float, R2: float, C2: float, ModelID:int, soc:float=0.5
target_battery = batteries[np.random.randint(0, len(batteries))]
# print(target_battery['k'])
sim_battery = BattSim(
    Kbatt=target_battery['k'],
    Cbatt = 2,
    R0 = 0.2,
    R1 = 0.1,
    C1 = 5,
    R2 = 0.3,
    C2 = 500,
    soc=1.0,
    ModelID=1,
) # note that only the Kbatt and soc is used for the simulation, the rest of the parameters are dummy values

# simulate full discharge curve for the battery
# discharge at 1C for 1h
I = np.ones(200) * sim_battery.Cbatt * -1
T = np.arange(0, 3600, 3600/200)
Vbatt, Ibatt, soc, Vo = sim_battery.simulate(I, T)

# Now that we have the full discharge curve of the battery, we can try to match it to one of the sample curves

# for gen 1, all we will do is compare the curves and that's good enough. the second and third generation will use the first and second derivatives of curves, and curve fitting to remove noise
# essentially, the point of gen 1 is to just show that in ideal case, we can actually use a cache and recorded datapoints to lookup K values

# find the rate of change of a vector passed
def derivative(L, dt):
    """
    find the rate of change of a vector
    L: numpy array, volts, dt: float, seconds between datapoints

    returns the rate of change of the vector
    """
    if len(L) < 2:
        return 0
    if type(L) is not np.ndarray:
        L = np.array(L)
    return (L[1:] - L[:-1]) / dt

# not even bothering with time vector at this stage
def find_curve(V, batteries):
    """
    find the curve that matches the voltage and time data
    V: list, batteries: list of dicts of batteries

    returns the Kbatt of the battery that matches the data
    if no match is found, returns None
    """
    for batt in batteries:
        # compare curves
        if np.allclose(V, batt['Vo']):
            return batt['k']
        # compare derivatives
        # if np.allclose(derivative(V, 1), derivative(batt['Vo'], 1)):
        #     return batt['Kbatt']
    return None

print('expected Kbatt:\t', target_battery['k'])
print('actual Kbatt:\t', find_curve(Vo, batteries))