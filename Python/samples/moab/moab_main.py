#!/usr/bin/env python3

"""
MSFT Bonsai SDK3 Template for Simulator Integration using Python
Copyright 2020 Microsoft

Usage:
  For registering simulator with the Bonsai service for training:
    python simulator_integration.py   
    Then connect your registered simulator to a Brain via UI, or using the CLI: `bonsai simulator unmanaged connect -b <brain-name> -a <train-or-assess> -c BalancePole --simulator-name Cartpole
"""

import datetime
import json
import os
import pathlib
import sys
import time
from typing import Any, Dict, List
import numpy as np

from jinja2 import Template
from pyrr import matrix33, vector

from dotenv import load_dotenv, set_key
from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorInterface,
    SimulatorState,
    SimulatorSessionResponse,
)
from azure.core.exceptions import HttpResponseError
from distutils.util import strtobool

from policies import coast, random_policy
from moab_model import MoabModel, clamp 

dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = "logs"
default_config = {"initial_x":np.random.uniform(-1,1),"initial_y":np.random.uniform(-1,1),"initial_vel_x":np.random.uniform(-1,1), 
        "initial_vel_y":np.random.uniform(-1,1),"initial_roll": np.random.uniform(-1,1), "initial_pitch": np.random.uniform(-1,1)}


class TemplateSimulatorSession:
    def __init__(
        self,
        render: bool = False,
        env_name: str = "Moab",
        log_data: bool = False,
        log_file: str = None,
    ):
        """Simulator Interface with the Bonsai Platform

        Parameters
        ----------
        render : bool, optional
            Whether to visualize episodes during training, by default False
        env_name : str, optional
            Name of simulator interface, by default "Cartpole"
        log_data: bool, optional
            Whether to log data, by default False
        log_file : str, optional
            where to log data, by default None
        """
        self.model = MoabModel()
        self.count_view = False
        self.env_name = env_name
        self.render = render
        self.log_data = log_data
        if not log_file:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            log_file = current_time + "_" + env_name + "_log.csv"
            log_file = os.path.join(log_path, log_file)
            logs_directory = pathlib.Path(log_file).parent.absolute()
            if not pathlib.Path(logs_directory).exists():
                print(
                    "Directory does not exist at {0}, creating now...".format(
                        str(logs_directory)
                    )
                )
                logs_directory.mkdir(parents=True, exist_ok=True)
        self.log_file = os.path.join(log_path, log_file)

    def get_state(self) -> Dict[str, float]:
        """Extract current states from the simulator

        Returns
        -------
        Dict[str, float]
            Returns float of current values from the simulator
        """
        # return {"ball_x":float(self.model.ball.x),
        #         "ball_y": float(self.model.ball.y),
        #         "ball_vel_x": float(self.model.ball_vel.x),
        #         "ball_vel_y": float(self.model.ball_vel.y)}
        return {key:float(value) for (key,value) in self.model.state().items()}
                

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

    def halted(self) -> bool:
        """Halt current episode. Note, this should only be called if the simulator has reached an unexpected state.

        Returns
        -------
        bool
            Whether to terminate current episode
        """
        return self.model.halted()


    def get_interface(self, sim_context) -> SimulatorInterface:
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
            simulator_context=sim_context,
            description=interface["description"],
        )

    
    def episode_start(self, config: Dict = None) -> None:
        """Initialize simulator environment using scenario paramters from inkling. Note, `simulator.reset()` initializes the simulator parameters for initial positions and velocities of the cart and pole using a random sampler. See the source for details.

        Parameters
        ----------
        config : Dict, optional
            masspole and length parameters to initialize, by default None
        """
        self.model.reset()
        if config is None:
            config = default_config
        self.config = config
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

    def episode_step(self, action: Dict):
        """Step through the environment for a single iteration.

        Parameters
        ----------
        action : Dict
            An action to take to modulate environment.
        """
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

        if self.render:
            self.sim_render()

    def sim_render(self):
        pass

    def random_policy(self, state: Dict = None) -> Dict:

        return random_policy(state)


def env_setup():
    """Helper function to setup connection with Project Bonsai

    Returns
    -------
    Tuple
        workspace, and access_key
    """

    load_dotenv(verbose=True)
    workspace = os.getenv("SIM_WORKSPACE")
    access_key = os.getenv("SIM_ACCESS_KEY")

    env_file_exists = os.path.exists(".env")
    if not env_file_exists:
        open(".env", "a").close()

    if not all([env_file_exists, workspace]):
        workspace = input("Please enter your workspace id: ")
        set_key(".env", "SIM_WORKSPACE", workspace)
    if not all([env_file_exists, access_key]):
        access_key = input("Please enter your access key: ")
        set_key(".env", "SIM_ACCESS_KEY", access_key)

    load_dotenv(verbose=True, override=True)
    workspace = os.getenv("SIM_WORKSPACE")
    access_key = os.getenv("SIM_ACCESS_KEY")

    return workspace, access_key


def test_random_policy(
    num_episodes: int = 100,
    render: bool = True,
    num_iterations: int = 50,
    log_iterations: bool = False,
):
    """Test a policy using random actions over a fixed number of episodes

    Parameters
    ----------
    num_episodes : int, optional
        number of iterations to run, by default 10
    """

    sim = TemplateSimulatorSession(
        render=render, log_data=log_iterations, log_file="moab_at_st.csv"
    )
    # test_config = {"length": 1.5}
    for episode in range(num_episodes):
        iteration = 0
        terminal = False
        sim_state = sim.episode_start(config=default_config)
        sim_state = sim.get_state()
        while not terminal:
            action = sim.random_policy(sim_state)
            sim.episode_step(action)
            sim_state = sim.get_state()
            if log_iterations:
                sim.log_iterations(sim_state, action, episode, iteration)
            print(f"Running iteration #{iteration} for episode #{episode}")
            print(f"Observations: {sim_state}")
            iteration += 1
            terminal = iteration >= num_iterations

    return sim


def main(
    render: bool = False, log_iterations: bool = False, config_setup: bool = False
):
    """Main entrypoint for running simulator connections

    Parameters
    ----------
    render : bool, optional
        visualize steps in environment, by default True, by default False
    log_iterations: bool, optional
        log iterations during training to a CSV file
    """

    # workspace environment variables
    if config_setup:
        env_setup()
        load_dotenv(verbose=True, override=True)

    # Grab standardized way to interact with sim API
    sim = TemplateSimulatorSession(render=render, log_data=log_iterations)

    # Configure client to interact with Bonsai service
    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    # Create simulator session and init sequence id
    # registration_info = SimulatorInterface(
    #                         name=sim.env_name, 
    #                         timeout=interface['timeout'], 
    #                         simulator_context=config_client.simulator_context, 
    # )
    
    # # Create simulator session and init sequence id
    registration_info = sim.get_interface(config_client.simulator_context)

    def CreateSession(
        registration_info: SimulatorInterface, config_client: BonsaiClientConfig
    ):
        """Creates a new Simulator Session and returns new session, sequenceId
        """

        try:
            print(
                "config: {}, {}".format(config_client.server, config_client.workspace)
            )
            registered_session: SimulatorSessionResponse = client.session.create(
                workspace_name=config_client.workspace, body=registration_info
            )
            print("Registered simulator. {}".format(registered_session.session_id))

            return registered_session, 1
        except HttpResponseError as ex:
            print(
                "HttpResponseError in Registering session: StatusCode: {}, Error: {}, Exception: {}".format(
                    ex.status_code, ex.error.message, ex
                )
            )
            raise ex
        except Exception as ex:
            print(
                "UnExpected error: {}, Most likely, it's some network connectivity issue, make sure you are able to reach bonsai platform from your network.".format(
                    ex
                )
            )
            raise ex

    registered_session, sequence_id = CreateSession(registration_info, config_client)
    episode = 0
    iteration = 0

    try:
        while True:
            # Advance by the new state depending on the event type
            # TODO: it's risky not doing doing `get_state` without first initializing the sim
            sim_state = SimulatorState(
                sequence_id=sequence_id, state=sim.get_state(), halted=sim.halted(),
            )
            print(sim.get_state())
            time.sleep(0.1)

            try:
                event = client.session.advance(
                    workspace_name=config_client.workspace,
                    session_id=registered_session.session_id,
                    body=sim_state,
                )
                sequence_id = event.sequence_id
                print(
                    "[{}] Last Event: {}".format(time.strftime("%H:%M:%S"), event.type)
                )
            except HttpResponseError as ex:
                print(
                    "HttpResponseError in Advance: StatusCode: {}, Error: {}, Exception: {}".format(
                        ex.status_code, ex.error.message, ex
                    )
                )
                # This can happen in network connectivity issue, though SDK has retry logic, but even after that request may fail,
                # if your network has some issue, or sim session at platform is going away..
                # So let's re-register sim-session and get a new session and continue iterating. :-)
                registered_session, sequence_id = CreateSession(
                    registration_info, config_client
                )
                continue
            except Exception as err:
                print("Unexpected error in Advance: {}".format(err))
                # Ideally this shouldn't happen, but for very long-running sims It can happen with various reasons, let's re-register sim & Move on.
                # If possible try to notify Bonsai team to see, if this is platform issue and can be fixed.
                registered_session, sequence_id = CreateSession(
                    registration_info, config_client
                )
                continue

            # Event loop
            if event.type == "Idle":
                time.sleep(event.idle.callback_time)
                print("Idling...")
            elif event.type == "EpisodeStart":
                # print(event.episode_start.config)
                sim.episode_start(event.episode_start.config)
                episode += 1
            elif event.type == "EpisodeStep":
                iteration += 1
                sim.episode_step(event.episode_step.action)
                if sim.log_data:
                    sim.log_iterations(
                        episode=episode,
                        iteration=iteration,
                        state=sim.get_state(),
                        action=event.episode_step.action,
                    )
            elif event.type == "EpisodeFinish":
                print("Episode Finishing...")
                iteration = 0
            elif event.type == "Unregister":
                print("Simulator Session unregistered by platform because '{}', Registering again!".format(event.unregister.details))
                registered_session, sequence_id = CreateSession(
                    registration_info, config_client
                )
                continue
            else:
                pass
    except KeyboardInterrupt:
        # Gracefully unregister with keyboard interrupt
        client.session.delete(
            workspace_name=config_client.workspace,
            session_id=registered_session.session_id,
        )
        print("Unregistered simulator.")
    except Exception as err:
        # Gracefully unregister for any other exceptions
        client.session.delete(
            workspace_name=config_client.workspace,
            session_id=registered_session.session_id,
        )
        print("Unregistered simulator because: {}".format(err))


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Bonsai and Simulator Integration...")
    parser.add_argument(
        "--render",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Render training episodes",
    )
    parser.add_argument(
        "--log-iterations",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Log iterations during training",
    )
    parser.add_argument(
        "--config-setup",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Use a local environment file to setup access keys and workspace ids",
    )
    parser.add_argument(
        "--test-local",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Run simulator locally without connecting to platform",
    )

    args = parser.parse_args()

    if args.test_local:
        test_random_policy(render=args.render, log_iterations=args.log_iterations)
    else:
        main(
            config_setup=args.config_setup,
            render=args.render,
            log_iterations=args.log_iterations,
        )

