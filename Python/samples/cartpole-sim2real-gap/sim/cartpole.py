"""
Classic cart-pole system implemented by Rich Sutton et al.
Copied from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R """

import math
import random
from collections import namedtuple

CartPoleState = namedtuple("CartPoleState", "x x_no_noise x_dot x_dot_no_noise y y_no_noise y_dot y_dot_no_noise")


class CartPole:
    """ Model for the dynamics of an inverted pendulum
    """

    def __init__(self):
        self.gravity = 9.8
        self.masscart = 1.0
        self.masspole = 0.1
        self.total_mass = self.masspole + self.masscart
        self.length = 0.5  # actually half the pole's length
        self.polemass_length = self.masspole * self.length
        self.force_mag = 10.0
        self.tau = 0.02  # seconds between state updates
        self.noise = 0.05

        # For noise introduction --> Run the model to extract range in which value moves (max - min)
        self.common_min_to_max = {
            "x": 0.6,
            "x_dot": 3,
            "theta": 0.5,
            "theta_dot": 5,
        }

        self.theta_threshold_radians = 12 * 2 * math.pi / 360
        self.x_threshold = 2.4

        self.reset()

    def step(self, action):
        """ Move the state of the cartpole simulation forward one time unit
        """
        force = self.force_mag if action else -self.force_mag
        costheta = math.cos(self.theta)
        sintheta = math.sin(self.theta)
        temp = (
            force + self.polemass_length * self.theta_dot ** 2 * sintheta
        ) / self.total_mass
        thetaacc = (self.gravity * sintheta - costheta * temp) / (
            self.length
            * (4.0 / 3.0 - self.masspole * costheta * costheta / self.total_mass)
        )
        xacc = temp - self.polemass_length * thetaacc * costheta / self.total_mass
        self.x_no_noise += self.tau * self.x_dot
        self.x = self.x_no_noise + random.gauss(0,self.noise) * self.common_min_to_max["x"]
        self.x_dot_no_noise += self.tau * xacc
        self.x_dot = self.x_dot_no_noise + random.gauss(0,self.noise) * self.common_min_to_max["x_dot"]
        self.theta_no_noise += self.tau * self.theta_dot
        self.theta = self.theta_no_noise + random.gauss(0,self.noise) * self.common_min_to_max["theta"]
        self.theta_dot_no_noise += self.tau * thetaacc
        self.theta_dot = self.theta_dot_no_noise + random.gauss(0,self.noise) * self.common_min_to_max["theta_dot"]
        return self.state

    def reset(self):
        """ Reset the model of a cartpole system to it's initial conditions
        """
        self.x_no_noise = random.uniform(-0.05, 0.05)
        self.x = self.x_no_noise + random.gauss(0,self.noise) * self.common_min_to_max["x"]
        self.x_dot_no_noise = random.uniform(-0.05, 0.05)
        self.x_dot = self.x_dot_no_noise + random.gauss(0,self.noise) * self.common_min_to_max["x_dot"]
        self.theta_no_noise = random.uniform(-0.05, 0.05)
        self.theta = self.theta_no_noise + random.gauss(0,self.noise) * self.common_min_to_max["theta"]
        self.theta_dot_no_noise = random.uniform(-0.05, 0.05)
        self.theta_dot = self.theta_dot_no_noise + random.gauss(0,self.noise) * self.common_min_to_max["theta_dot"]

    @property
    def state(self):
        return CartPoleState(self.x, self.x_no_noise, self.x_dot, self.x_dot_no_noise, self.theta, self.theta_no_noise, self.theta_dot, self.theta_dot_no_noise)


def create_viewer(model):
    from render import Viewer

    viewer = Viewer()
    viewer.model = model
    return viewer


if __name__ == "__main__":

    import random
    import sys

    model = CartPole()
    viewer = create_viewer(model)
    number_episodes = 100
    for i in range(number_episodes):
        action = [0, 1]
        state = viewer.model.step(random.sample(action, 1)[0])
        viewer.update()
        if viewer.has_exit:
            viewer.close()
            sys.exit(0)
