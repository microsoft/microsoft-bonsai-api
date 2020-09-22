from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import time
import math
import numpy as np
import random
from scipy.integrate import odeint
 
from .render_qube import QubeRendererVpython
# uncomment to test sim using if __name__=='__main__'
#from render_qube import QubeRendererVpython

class QubeSimulator(object):
    """Simulation for the Quanser Qube Inverted Pendulum."""

    def __init__(self, frequency=250):
        self.frequency = frequency
        self._dt = 1.0 / self.frequency
        self._max_voltage = 3.0

        # Motor
        self.Rm = 8.4  # Resistance
        self.kt = 0.042  # Current-torque (N-m/A)
        self.km = 0.042  # Back-emf constant (V-s/rad)

        # Rotary Arm
        self.mr = 0.095  # Mass (kg)
        self.Lr = 0.085  # Total length (m)
        self.Jr = self.mr * self.Lr ** 2 / 12  # Moment of inertia about pivot (kg-m^2)
        self.Dr = 0.00027  # Equivalent viscous damping coefficient (N-m-s/rad)

        # Pendulum Link
        self.mp = 0.024  # Mass (kg)
        self.Lp = 0.129  # Total length (m)
        self.Jp = self.mp * self.Lp ** 2 / 12  # Moment of inertia about pivot (kg-m^2)
        self.Dp = 0.00005  # Equivalent viscous damping coefficient (N-m-s/rad)

        self.g = 9.81  # Gravity constant
        
        self.state = (
            np.array([0, np.pi, 0, 0], dtype=np.float64) + \
            np.random.randn(4) * 0.05
        )

        self.count_view = False

    def step(self, action):
        action = np.clip(action, -self._max_voltage, self._max_voltage)
        self.state = self._forward_model_ode(
            *self.state, action, self._dt
        )
        return self.state

    def reset(self, config=None):
        self.state = (
            np.array([0, np.pi, 0, 0], dtype=np.float64) + \
            np.random.randn(4) * 0.05
        )
        if config:
            self.Lp = config.get("Lp", 0.129)
            self.mp = config.get("mp", 0.024)
            self.Rm = config.get("Rm", 8.4)
            self.kt = config.get("kt", 0.042)
            self.km = config.get("km", 0.042)
            self.mr = config.get("mr", 0.095)
            self.Lr = config.get("Lr", 0.085)
            self.Dr = config.get("Dr", 0.00027)
            self.Dp = config.get("Dp", 0.00005)
            self.Jp = self.mp * self.Lp ** 2 / 12  # Recalculate for new mp, Lp
            self.Jr = self.mr * self.Lr ** 2 / 12  # Recalculate for new mr, Lr

            self.frequency = config.get("frequency", 250)
            self._dt = 1.0 / self.frequency

            self.state = np.array([
                config.get("initial_theta", np.random.randn() * 0.05),
                config.get("initial_alpha", np.pi + np.random.randn() * 0.05),
                config.get("initial_theta_dot", np.random.randn() * 0.05),
                config.get("initial_alpha_dot", np.random.randn() * 0.05),
            ])
        return self.state

    def view(self):
        if self.count_view == False:
            self.viewer = QubeRendererVpython(
                self.state[0], 
                self.state[1],
                self.frequency
            )
            self.count_view = True
        self.viewer.render(self.state[0], self.state[1])

    def _diff_forward_model_ode(self, state, t, action, dt):
        theta, alpha, theta_dot, alpha_dot = state
        Vm = action
        tau = -(self.km * (Vm - self.km * theta_dot)) / self.Rm  # torque

        # fmt: off
        # From Rotary Pendulum Workbook
        theta_dot_dot = (-self.Lp*self.Lr*self.mp*(-8.0*self.Dp*alpha_dot + self.Lp**2*self.mp*theta_dot**2*np.sin(2.0*alpha) + 4.0*self.Lp*self.g*self.mp*np.sin(alpha))*np.cos(alpha) + (4.0*self.Jp + self.Lp**2*self.mp)*(4.0*self.Dr*theta_dot + self.Lp**2*alpha_dot*self.mp*theta_dot*np.sin(2.0*alpha) + 2.0*self.Lp*self.Lr*alpha_dot**2*self.mp*np.sin(alpha) - 4.0*tau))/(4.0*self.Lp**2*self.Lr**2*self.mp**2*np.cos(alpha)**2 - (4.0*self.Jp + self.Lp**2*self.mp)*(4.0*self.Jr + self.Lp**2*self.mp*np.sin(alpha)**2 + 4.0*self.Lr**2*self.mp))
        alpha_dot_dot = (2.0*self.Lp*self.Lr*self.mp*(4.0*self.Dr*theta_dot + self.Lp**2*alpha_dot*self.mp*theta_dot*np.sin(2.0*alpha) + 2.0*self.Lp*self.Lr*alpha_dot**2*self.mp*np.sin(alpha) - 4.0*tau)*np.cos(alpha) - 0.5*(4.0*self.Jr + self.Lp**2*self.mp*np.sin(alpha)**2 + 4.0*self.Lr**2*self.mp)*(-8.0*self.Dp*alpha_dot + self.Lp**2*self.mp*theta_dot**2*np.sin(2.0*alpha) + 4.0*self.Lp*self.g*self.mp*np.sin(alpha)))/(4.0*self.Lp**2*self.Lr**2*self.mp**2*np.cos(alpha)**2 - (4.0*self.Jp + self.Lp**2*self.mp)*(4.0*self.Jr + self.Lp**2*self.mp*np.sin(alpha)**2 + 4.0*self.Lr**2*self.mp))
        # fmt: on

        diff_state = np.array([theta_dot, alpha_dot, theta_dot_dot, alpha_dot_dot]).reshape(
            (4,)
        )
        diff_state = np.array(diff_state, dtype="float64")
        return diff_state


    def _forward_model_ode(self, theta, alpha, theta_dot, alpha_dot, Vm, dt):
        t = np.linspace(0.0, dt, 2)

        state = np.array([theta, alpha, theta_dot, alpha_dot])
        next_state = np.array(odeint(self._diff_forward_model_ode, state, t, args=(Vm, dt)))[1, :]
        theta, alpha, theta_dot, alpha_dot = next_state

        theta = ((theta + np.pi) % (2 * np.pi)) - np.pi
        alpha = ((alpha + np.pi) % (2 * np.pi)) - np.pi

        return theta, alpha, theta_dot, alpha_dot

'''
# Need to comment out in order to call from script in another file
if __name__ == '__main__':
    qube = QubeSimulator(frequency=250)

    ## LQR benchmark controller gains
    K = np.array([-2.0, 35.0, -1.5, 3.0])
    
    for episode in range(2):
        # Optional config
        config = {
            # Parameters
            "Lp": 0.129,
            "mp": 0.024,
            "Rm": 8.4,
            "kt": 0.042,
            "km": 0.042,
            "mr": 0.095,
            "Lr": 0.085,
            "Dr": 0.00027,
            "Dp": 0.00005,
            "frequency": 250,
            # Initial Conditions
            "theta": random.randint(0, 360) * 2 * np.pi / 360,
            "alpha": 0 + np.random.randn() * 0.05, # make sure pi if reset_down
            "theta_dot": 0 + np.random.randn() * 0.05,
            "alpha_dot": 0 + np.random.randn() * 0.05
        }

        print('episode: ', episode)
        state = qube.reset(config)
        
        for i in range(2048):
            #action = random.uniform(-3, 3)
            action = K.dot(state)
            state = qube.step(action)
            qube.view()
'''