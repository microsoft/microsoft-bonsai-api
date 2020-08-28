"""
Classic cart-pole system implemented by Rich Sutton et al.
Copied from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R """

import math
import random
from collections import namedtuple

CartPoleState = namedtuple("CartPoleState", "x x_dot y y_dot")


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
        self.x += self.tau * self.x_dot
        self.x_dot += self.tau * xacc
        self.theta += self.tau * self.theta_dot
        self.theta_dot += self.tau * thetaacc

        return self.state

    def reset(self):
        """ Reset the model of a cartpole system to it's initial conditions
        """
        self.x = random.uniform(-0.05, 0.05)
        self.x_dot = random.uniform(-0.05, 0.05)
        self.theta = random.uniform(-0.05, 0.05)
        self.theta_dot = random.uniform(-0.05, 0.05)

    @property
    def state(self):
        return CartPoleState(self.x, self.x_dot, self.theta, self.theta_dot)


def create_viewer(model):
    from render import Viewer

    viewer = Viewer()
    viewer.model = model
    return viewer


if __name__ == "__main__":

    import random
    import sys

    model = CartPole(length=1)
    viewer = create_viewer(model)
    number_episodes = 100
    for i in range(number_episodes):
        action = [0, 1]
        state = viewer.model.step(random.sample(action, 1)[0])
        viewer.update()
        if viewer.has_exit:
            viewer.close()
            sys.exit(0)
