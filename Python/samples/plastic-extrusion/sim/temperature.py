import numpy as np
from scipy import interpolate

from sim import units


# data from [EH] Table 23.1
DATA_SPEED_CHANGE_RPM = np.array([0, 1, 2, 10, 15, 25])
DATA_TEMPERATURE_CHANGE_FAHRENHEIT = np.array([0, 2, 4, 10, 15, 30])

# convert from RPM to radians / second
DATA_SPEED_CHANGE = DATA_SPEED_CHANGE_RPM * units.RADIANS_PER_REVOLUTION / 60
# convert from Fahrenheit to Celsius
DATA_TEMPERATURE_CHANGE = (5 / 9) * DATA_TEMPERATURE_CHANGE_FAHRENHEIT


def temperature_change(Δω):
    """
    Changing the screw speed causes a corresponding change in material temperature.

    Parameters
    ----------
    Δω : float
        Change in screw angular speed (radians / second^2).

    Returns
    -------
    ΔT : float
        Temperature change induced by the change in screw angular speed.
    """

    f = interpolate.interp1d(
        x=DATA_SPEED_CHANGE,
        y=DATA_TEMPERATURE_CHANGE,
        kind="quadratic",
        fill_value="extrapolate",
    )
    # NOTE: the interpolation is only well-behaved for non-negative inputs,
    # so we force it to be symmetric
    ΔT = f(np.abs(Δω)) * np.sign(Δω)
    return ΔT


# https://en.wikipedia.org/wiki/Gas_constant
R = 8.314  # J / mol / K

# [D] p. 47
Ea_PVC = 85_000  # J / mol


def arrhenius(T1, T2, Ea=Ea_PVC):
    """
    Temperature adjustment to viscosity.

    Parameters
    ----------
    T1 : float
        Temperature at previous time step (Kelvin).
    T2 : float
        Temperature at current time step (Kelvin).
    Ea : float, optional
        Activation energy (J / mol).

    Returns
    -------
    h_T : float
        Temperature adjustment.
    
    References
    ----------
    .. [D] p. 47
    .. [WARE] <https://en.wikipedia.org/wiki/Arrhenius_equation>
    .. [WARP] <https://en.wikipedia.org/wiki/Arrhenius_plot>
    """

    return np.exp((Ea / R) * (1 / T2 - 1 / T1))
