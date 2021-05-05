"""
Simulator for the Moab plate+ball balancing device.
"""
__author__ = "Mike Estee"
__copyright__ = "Copyright 2020, Microsoft Corp."

# pyright: strict, reportUnknownMemberType=false

import logging
import os
import sys
import json

from jinja2 import Template
from pyrr import matrix33, vector

from moab_model import MoabModel, clamp

from bonsai_common import SimulatorSession, Schema
from microsoft_bonsai_api.simulator.generated.models import SimulatorInterface
from microsoft_bonsai_api.simulator.client import BonsaiClientConfig

log = logging.getLogger(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = "logs"
default_config = {"length": 0.5, "masspole": 0.1}


class MoabSim(SimulatorSession):
    def __init__(self, config: BonsaiClientConfig,
        render: bool=False,env_name: str = "Moab",
        log_data: bool=False,log_file: str = None):
        super().__init__(config)
        self.model = MoabModel()
        self._episode_count = 0
        self.model.reset()

    # callbacks
    def halted(self) -> bool:
        return self.model.halted()

    def get_interface(self) -> SimulatorInterface:
        interface_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "moab_interface.json"
        )

        # load the template
        try:
            with open(interface_file_path, "r") as file:
                template_str = file.read()
        except:
            log.info(
                "Failed to load interface template file: {}".format(interface_file_path)
            )
            raise

        # render the template with our constants
        template = Template(template_str)
        interface_str = template.render(
            initial_pitch=self.model.pitch,
            initial_roll=self.model.roll,
            initial_height_z=self.model.height_z,
            time_delta=self.model.time_delta,
            gravity=self.model.time_delta,
            plate_radius=self.model.plate_radius,
            plate_theta_vel_limit=self.model.plate_theta_vel_limit,
            plate_theta_acc=self.model.plate_theta_acc,
            plate_theta_limit=self.model.plate_theta_limit,
            plate_z_limit=self.model.plate_z_limit,
            ball_mass=self.model.ball_mass,
            ball_radius=self.model.ball_radius,
            ball_shell=self.model.ball_shell,
            obstacle_radius=self.model.obstacle_radius,
            obstacle_x=self.model.obstacle_x,
            obstacle_y=self.model.obstacle_y,
            target_x=self.model.target_x,
            target_y=self.model.target_y,
            initial_x=self.model.ball.x,
            initial_y=self.model.ball.y,
            initial_z=self.model.ball.z,
            initial_vel_x=self.model.ball_vel.x,
            initial_vel_y=self.model.ball_vel.y,
            initial_vel_z=self.model.ball_vel.z,
            initial_speed=0,
            initial_direction=0,
            ball_noise=self.model.ball_noise,
            plate_noise=self.model.plate_noise,
        )
        interface = json.loads(interface_str)
        return SimulatorInterface(
            name=interface["name"],
            timeout=interface["timeout"],
            simulator_context=self.get_simulator_context(),
            description=interface["description"],
        )

    def get_state(self) -> Schema:
        return self.model.state()

    def _set_velocity_for_speed_and_direction(self, speed: float, direction: float):
        # get the heading
        dx = self.model.target_x - self.model.ball.x
        dy = self.model.target_y - self.model.ball.y

        # direction is meaningless if we're already at the target
        if (dx != 0) or (dy != 0):

            # set the magnitude
            vel = vector.set_length([dx, dy, 0.0], speed)

            # rotate by direction around Z-axis at ball position
            rot = matrix33.create_from_axis_rotation([0.0, 0.0, 1.0], direction)
            vel = matrix33.apply_to_vector(rot, vel)

            # unpack into ball velocity
            self.model.ball_vel.x = vel[0]
            self.model.ball_vel.y = vel[1]
            self.model.ball_vel.z = vel[2]

    def episode_start(self, config: Schema) -> None:
        # return to known good state to avoid accidental episode-episode dependencies
        self.model.reset()

        # initial control state. these are all [-1..1] unitless
        self.model.roll = config.get("initial_roll", self.model.roll)
        self.model.pitch = config.get("initial_pitch", self.model.pitch)

        self.model.height_z = config.get("initial_height_z", self.model.height_z)

        # constants, SI units.
        self.model.time_delta = config.get("time_delta", self.model.time_delta)
        self.model.jitter = config.get("jitter", self.model.jitter)
        self.model.gravity = config.get("gravity", self.model.gravity)
        self.model.plate_theta_vel_limit = config.get(
            "plate_theta_vel_limit", self.model.plate_theta_vel_limit
        )
        self.model.plate_theta_acc = config.get(
            "plate_theta_acc", self.model.plate_theta_acc
        )
        self.model.plate_theta_limit = config.get(
            "plate_theta_limit", self.model.plate_theta_limit
        )
        self.model.plate_z_limit = config.get("plate_z_limit", self.model.plate_z_limit)

        self.model.ball_mass = config.get("ball_mass", self.model.ball_mass)
        self.model.ball_radius = config.get("ball_radius", self.model.ball_radius)
        self.model.ball_shell = config.get("ball_shell", self.model.ball_shell)

        self.model.obstacle_radius = config.get(
            "obstacle_radius", self.model.obstacle_radius
        )
        self.model.obstacle_x = config.get("obstacle_x", self.model.obstacle_x)
        self.model.obstacle_y = config.get("obstacle_y", self.model.obstacle_y)

        # a target position the AI can try and move the ball to
        self.model.target_x = config.get("target_x", self.model.target_x)
        self.model.target_y = config.get("target_y", self.model.target_y)

        # observation config
        self.model.ball_noise = config.get("ball_noise", self.model.ball_noise)
        self.model.plate_noise = config.get("plate_noise", self.model.plate_noise)

        # now we can update the initial plate metrics from the constants and the controls
        self.model.update_plate(plate_reset=True)

        # initial ball state after updating plate
        self.model.set_initial_ball(
            config.get("initial_x", self.model.ball.x),
            config.get("initial_y", self.model.ball.y),
            config.get("initial_z", self.model.ball.z),
        )
        # velocity set as a vector
        self.model.ball_vel.x = config.get("initial_vel_x", self.model.ball_vel.x)
        self.model.ball_vel.y = config.get("initial_vel_y", self.model.ball_vel.y)
        self.model.ball_vel.z = config.get("initial_vel_z", self.model.ball_vel.z)

        # velocity set as a speed/direction towards target
        initial_speed = config.get("initial_speed", None)
        initial_direction = config.get("initial_direction", None)
        if initial_speed is not None and initial_direction is not None:
            self._set_velocity_for_speed_and_direction(initial_speed, initial_direction)

        # new episode, iteration count reset
        self.iteration_count = 0
        self._episode_count += 1
    def log_iterations(self, state, action, episode: int = 0, iteration: int = 1):
        """Log iterations during training to a CSV.

        Parameters
        ----------
        state : Dict
        action : Dict
        episode : int, optional
        iteration : int, optional
        """

        import pandas as pd

        def add_prefixes(d, prefix: str):
            return {f"{prefix}_{k}": v for k, v in d.items()}

        state = add_prefixes(state, "state")
        action = add_prefixes(action, "action")
        config = add_prefixes(self.config, "config")
        data = {**state, **action, **config}
        data["episode"] = episode
        data["iteration"] = iteration
        log_df = pd.DataFrame(data, index=[0])

        if os.path.exists(self.log_file):
            log_df.to_csv(
                path_or_buf=self.log_file, mode="a", header=False, index=False
            )
        else:
            log_df.to_csv(path_or_buf=self.log_file, mode="w", header=True, index=False)

    def episode_step(self, action: Schema):
        # use new syntax or fall back to old parameter names
        self.model.roll = action.get("input_roll", self.model.roll)
        self.model.pitch = action.get("input_pitch", self.model.pitch)

        # clamp inputs to legal ranges
        self.model.roll = clamp(self.model.roll, -1.0, 1.0)
        self.model.pitch = clamp(self.model.pitch, -1.0, 1.0)

        self.model.height_z = clamp(
            action.get("input_height_z", self.model.height_z), -1.0, 1.0
        )

        self.model.step()

    def episode_finish(self, reason: str):
        # log ball's distance to center and velocity at the end of each episode.
        log.info(
            "Episode {} ends at iter {}, ball dist to target ={}, ball speed={} reason={}".format(
                self._episode_count,
                self.iteration_count,
                self.model.estimated_distance,
                self.model.estimated_speed,
                reason,
            )
        )


if __name__ == "__main__":
    try:
        # configuration for talking to server
        config = BonsaiClientConfig(argv=sys.argv)
        sim = MoabSim(config)
        sim.model.reset()
        while sim.run():
            continue

    except Exception as e:
        print(e)
