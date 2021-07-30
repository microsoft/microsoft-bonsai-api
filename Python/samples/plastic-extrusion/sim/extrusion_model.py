from dataclasses import dataclass
import math

from sim import temperature as tm
from sim import units


π = math.pi


@dataclass
class ExtrusionModel:

    ω: float  # radians / second
    Δω: float  # radians / second
    f_c: float  # hertz
    T: float  # Kelvin
    ΔT: float = 0  # Kelvin
    Δt: float = 1  # second

    # screw parameters
    D: float = 2.5 * units.METERS_PER_INCH  # meters
    L_s: float = 60 * units.METERS_PER_INCH  # meters
    H: float = 0.24 * units.METERS_PER_INCH  # meters
    W: float = 0.45 * units.METERS_PER_INCH  # meters
    φ: float = math.radians(17.5)  # radians

    # die parameters
    R_d: float = 0.5 * units.METERS_PER_INCH
    L_d: float = 2 * units.METERS_PER_INCH

    # extruder control actions
    ω_max: float = (200 / 60) * units.RADIANS_PER_REVOLUTION  # radians / second
    f_max: float = 10  # Hz

    # material parameters for viscosity power law model
    # values for rigid PVC @ 180 deg C from [PTPL]
    m: float = 1.7e4  # no units given in [PTPL], so I'm assuming Pa * s
    n: float = 0.26  # (dimensionless)

    # desired part specifications
    L0: float = 1 * 12 * units.METERS_PER_INCH
    ε: float = 0.1 * units.METERS_PER_INCH

    def __post_init__(self):

        # channel velocity (from [EH] Eq. 4.4)
        self.V_z = π * self.D * math.cos(self.φ) * self.ω

        # drag flow (from [EH] Eq. 4.3)
        self.Q_D = 0.5 * self.W * self.H * self.V_z

        # constant for pressure flow determined from screw geometry
        self.β1 = (self.W * self.H ** 3 * math.sin(self.φ)) / (12 * self.L_s)

        # Rabinowitsch correction to shear rate for non-Newtonian fluids
        self.rabinowitsch_correction = (3 * self.n + 1) / (4 * self.n)

        # die constant
        self.k = (π * self.R_d ** 4) / (8 * self.L_d)

        self.viscosity_screw()
        self.viscosity_die()

        # operating pressure
        self.P_op = self.Q_D / (self.β1 / self.η_s + self.k / self.η_d)

        # flow rate (see [WVFR])
        self.Q_op = self.k * self.P_op / self.η_d

        # cross-sectional area of the die
        self.A = π * self.R_d ** 2

        # linear fluid velocity
        self.v = self.Q_op / self.A

        # part length (assuming no extrudate swell)
        self.L = self.v / self.f_c

        self.production_efficiency()

    def shear_rate_screw(self):
        """
        Shear rate of the material in the barrel due to the rotation of the screw.

        Returns
        -------
        γdot : float
            Shear rate (1 / seconds).

        References
        ----------
        .. [EH] Eq. 8.1
        """

        return π * self.D * self.ω / self.H

    def shear_rate_die(self, Q):
        """
        References
        ----------
        .. [EH] Eq. 8.2
        .. [D] p. 41
        .. [WSR] <https://en.wikipedia.org/wiki/Shear_rate>
        """

        return (4 * Q) / (π * self.R_d ** 3)

    def viscosity_power_law(self, γdot):
        """
        Returns
        -------
        η : float
            Viscosity (Pascal * seconds).

        References
        ----------
        .. [D] p. 45
        """

        return self.m * γdot ** (self.n - 1)

    def temperature_adjustment(self):
        """Temperature adjustment to viscosity"""

        self.ΔT = tm.temperature_change(Δω=self.Δω)
        return tm.arrhenius(T1=self.T, T2=self.T + self.ΔT)

    def viscosity_screw(self):

        γdot = self.shear_rate_screw()
        γdot *= self.rabinowitsch_correction

        η_shear = self.viscosity_power_law(γdot=γdot)
        h_temp = self.temperature_adjustment()

        self.η_s = η_shear * h_temp

    def viscosity_die(self):

        γdot = self.shear_rate_die(Q=self.Q_D)
        γdot *= self.rabinowitsch_correction

        η_shear = self.viscosity_power_law(γdot=γdot)

        self.η_d = η_shear

    def length_within_tolerance(self):
        return abs(self.L - self.L0) < self.ε

    def production_efficiency(self):

        # NOTE: the cutter frequency is equivalent to the number of parts
        # produced per second.  Since the simulation time step is also
        # 1 second, this is also the number of parts per iteration.
        parts_per_iteration = self.f_c * self.Δt

        if self.length_within_tolerance():
            self.yield_ = parts_per_iteration
        else:
            self.yield_ = 0
