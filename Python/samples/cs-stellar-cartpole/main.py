#!/usr/bin/env python3

"""
MSFT Bonsai SDK3 Template for Simulator Integration using Python
Copyright 2020 Microsoft

Usage:
  For registering simulator with the Bonsai service for training:
    python simulator_integration.py   
    Then connect your registered simulator to a Brain via UI, or using the CLI: `bonsai simulator unmanaged connect -b <brain-name> -a <train-or-assess> -c BalancePole --simulator-name Cartpole
"""

import os
import pathlib
import sys
from dotenv import load_dotenv, set_key
import time
import datetime
from typing import Dict, Any, List
from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorState,
    SimulatorInterface,
)

from sim import cartpole
from policies import random_policy, coast

dir_path = os.path.dirname(os.path.realpath(__file__))
default_config = {"length": 0.5, "masspole": 0.1}


class TemplateSimulatorSession:
    def __init__(
        self,
        render: bool = False,
        env_name: str = "Cartpole",
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
        self.simulator = cartpole.CartPole()
        self.count_view = False
        self.env_name = env_name
        self.render = render
        self.log_data = log_data
        if not log_file:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file = current_time + "_" + env_name + "_log.csv"
            log_file = os.path.join("log", log_file)
            logs_directory = pathlib.Path(log_file).parent.absolute()
            if not pathlib.Path(logs_directory).exists():
                print(
                    "Directory does not exist at {0}, creating now...".format(
                        str(logs_directory)
                    )
                )
                logs_directory.mkdir(parents=True, exist_ok=True)
        self.log_file = log_file

    def get_state(self) -> Dict[str, float]:
        """Extract current states from the simulator

        Returns
        -------
        Dict[str, float]
            Returns float of current values from the simulator
        """
        return {
            "x_position": self.simulator.x,
            "x_velocity": self.simulator.x_dot,
            "angle_position": self.simulator.theta,
            "angle_velocity": self.simulator.theta_dot,
        }

    def halted(self) -> bool:
        """Halt current episode. Note, this should only be called if the simulator has reached an unexpected state.

        Returns
        -------
        bool
            Whether to terminate current episode
        """
        return False

    def episode_start(self, config: Dict = None) -> None:
        """Initialize simulator environment using scenario paramters from inkling. Note, `simulator.reset()` initializes the simulator parameters for initial positions and velocities of the cart and pole using a random sampler. See the source for details.

        Parameters
        ----------
        config : Dict, optional
            masspole and length parameters to initialize, by default None
        """

        if "length" in config.keys():
            self.simulator.length = config["length"]
        if "masspole" in config.keys():
            self.simulator.masspole = config["masspole"]
        self.simulator.reset()
        if config is None:
            config = default_config
        self.config = config

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
        self.simulator.step(action["command"])
        if self.render:
            self.sim_render()

    def sim_render(self):
        from sim import render

        if self.count_view == False:
            self.viewer = render.Viewer()
            self.viewer.model = self.simulator
            self.count_view = True

        self.viewer.update()
        if self.viewer.has_exit:
            sys.exit(0)

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
    num_episodes: int = 5,
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

    sim = TemplateSimulatorSession(render=render, log_data=log_iterations)
    # test_config = {"length": 1.5}
    for episode in range(num_episodes):
        iteration = 0
        terminal = False
        sim_state = sim.episode_start(config=default_config)
        while not terminal:
            action = sim.random_policy(sim_state)
            sim.episode_step(action)
            sim_state = sim.get_state()
            print(f"Running iteration #{iteration} for episode #{episode}")
            print(f"Observations: {sim_state}")
            sim.log_iterations(sim_state, action, episode, iteration)
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

    # # Load json file as simulator integration config type file
    # with open("interface.json") as file:
    # interface = json.load(file)

    # Create simulator session and init sequence id
    registration_info = SimulatorInterface(
        name=sim.env_name,
        timeout=60,
        simulator_context=config_client.simulator_context,
    )
    registered_session = client.session.create(
        workspace_name=config_client.workspace, body=registration_info
    )
    print("Registered simulator.")
    sequence_id = 1
    episode = 0
    iteration = 0

    try:
        while True:
            # Advance by the new state depending on the event type
            sim_state = SimulatorState(
                sequence_id=sequence_id, state=sim.get_state(), halted=sim.halted(),
            )
            event = client.session.advance(
                workspace_name=config_client.workspace,
                session_id=registered_session.session_id,
                body=sim_state,
            )
            sequence_id = event.sequence_id
            print("[{}] Last Event: {}".format(time.strftime("%H:%M:%S"), event.type))

            # Event loop
            if event.type == "Idle":
                time.sleep(event.idle.callback_time)
                print("Idling...")
            elif event.type == "EpisodeStart":
                print(event.episode_start.config)
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
                client.session.delete(
                    workspace_name=config_client.workspace,
                    session_id=registered_session.session_id,
                )
                print("Unregistered simulator.")
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
        "--render", type=bool, default=False, help="Render training episodes"
    )
    parser.add_argument(
        "--log-iterations",
        type=bool,
        default=False,
        help="Log iterations during training",
    )
    parser.add_argument(
        "--config-setup",
        type=bool,
        default=False,
        help="Use a local environment file to setup access keys and workspace ids",
    )

    args = parser.parse_args()

    main(
        config_setup=args.config_setup,
        render=args.render,
        log_iterations=args.log_iterations,
    )
    # test_random_policy(render=args.render, log_iterations=args.log_iterations)
