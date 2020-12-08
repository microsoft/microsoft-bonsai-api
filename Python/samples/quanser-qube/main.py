#!/usr/bin/env python3

"""
MSFT Bonsai SDK3 Template for Simulator Integration using Python
Copyright 2020 Microsoft

Usage:
  For registering simulator with the Bonsai service for training:
    python __main__.py \
           --workspace <workspace_id> \
           --accesskey="<access_key> \
  Then connect your registered simulator to a Brain via UI
  Alternatively, one can set the SIM_ACCESS_KEY and SIM_WORKSPACE as
  environment variables.
"""

import json
import pathlib
import os
import time
import datetime
import random
from distutils.util import strtobool
from dotenv import load_dotenv, set_key
from typing import Dict, Any, Optional
from microsoft_bonsai_api.simulator.client import BonsaiClientConfig, BonsaiClient
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorState,
    SimulatorInterface,
)

from policies import *
import argparse
from sim.qube_simulator import QubeSimulator

default_config = {
    "Lp": 0.129,
    "mp": 0.024,
    "Rm": 8.4,
    "kt": 0.042,
    "km": 0.042,
    "mr": 0.095,
    "Lr": 0.085,
    "Dr": 0.00027,
    "Dp": 0.00005,
    "frequency": 80,
    "inital_theta": 1.4,
    "initial_alpha": 0,  # range of alpha if (0, \pi), \pi starts the pendulum at the bottom, zero starts at it at the top
    "initial_theta_dot": 0.0,
    "initial_alpha_dot": 0.0,
}

balance_config = {
    "Lp": 0.129,
    "mp": 0.024,
    "Rm": 8.4,
    "kt": 0.042,
    "km": 0.042,
    "mr": 0.095,
    "Lr": 0.085,
    "Dr": 0.00027,
    "Dp": 0.00005,
    "frequency": 80,
    "inital_theta": 1.4,
    "initial_alpha": 0,  # range of alpha if (0, \pi), \pi starts the pendulum at the bottom, zero starts at it at the top
    "initial_theta_dot": 0.0,
    "initial_alpha_dot": 0.0,
}

swingup_config = {
    "Lp": 0.129,
    "mp": 0.024,
    "Rm": 8.4,
    "kt": 0.042,
    "km": 0.042,
    "mr": 0.095,
    "Lr": 0.085,
    "Dr": 0.00027,
    "Dp": 0.00005,
    "frequency": 80,
    "inital_theta": 1.4,
    "initial_alpha": 3.14,  # range of alpha if (0, \pi), \pi starts the pendulum at the bottom, zero starts at it at the top
    "initial_theta_dot": 0.0,
    "initial_alpha_dot": 0.0,
}



class TemplateSimulatorSession:
    def __init__(
        self,
        env_name: str = "Quanser",
        render: bool = False,
        log_data: bool = False,
        log_file: str = None,
    ):
        ## Initialize python api for simulator
        self.simulator = QubeSimulator()
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
        self.config = default_config

    def get_state(self) -> Dict[str, Any]:
        """Called to retreive the current state of the simulator. """
        return {
            ## Add simulator state as dictionary
            "theta": float(self.simulator.state[0]),
            "alpha": float(self.simulator.state[1]),
            "theta_dot": float(self.simulator.state[2]),
            "alpha_dot": float(self.simulator.state[3]),
        }

    def episode_start(self, config: Dict[str, Any] = default_config):
        """ Called at the start of each episode """
        ## Add simulator reset api here using config from desired lesson in inkling
        self.simulator.reset(config)

    def episode_step(self, action: Dict[str, Any]):
        """ Called for each step of the episode """
        ## Add simulator step api here using action from Bonsai platform
        self.simulator.step(action["Vm"])

        if self.render:
            self.simulator.view()

    def halted(self) -> bool:
        """
        Should return True if the simulator cannot continue for some reason
        """
        return False

    def random_policy(self, sim_state: Dict[str, Any]) -> Dict[str, float]:

        return {"Vm": random.uniform(-3, 3)}

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
    num_episodes: int = 1000,
    render: bool = True,
    num_iterations: int = 50,
    policy=random_policy,
    mixing_percentage: float = 0.5,
    config: Dict[str, float] = balance_config,
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
        sim.episode_start(config=config)
        sim_state = sim.get_state()
        while not terminal:
            # hybrid policy would mix random_policy with lqr policy
            action = policy(sim_state)
            sim.episode_step(action)
            sim_state = sim.get_state()
            print(f"Running iteration #{iteration} for episode #{episode}")
            print(f"Observations: {sim_state}")
            if log_iterations:
                sim.log_iterations(sim_state, action, episode, iteration)
            iteration += 1
            terminal = iteration >= num_iterations

    return sim


def main(render=False, config_setup: bool = False, log_iterations: bool = False):

    # workspace environment variables
    if config_setup:
        env_setup()
        load_dotenv(verbose=True, override=True)

    # Grab standardized way to interact with sim API
    sim = TemplateSimulatorSession(render=render)

    # Configure client to interact with Bonsai service
    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    # Load json file as simulator integration config type file
    with open("interface.json") as file:
        interface = json.load(file)

    # Create simulator session and init sequence id
    registration_info = SimulatorInterface(
        name=interface["name"],
        timeout=interface["timeout"],
        simulator_context=config_client.simulator_context,
    )
    registered_session = client.session.create(
        workspace_name=config_client.workspace, body=registration_info
    )
    print("Registered simulator.")
    sequence_id = 1

    try:
        while True:
            # Advance by the new state depending on the event type
            sim_state = SimulatorState(
                sequence_id=sequence_id, state=sim.get_state(), halted=sim.halted()
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
                sim.episode_start(event.episode_start.config)
            elif event.type == "EpisodeStep":
                sim.episode_step(event.episode_step.action)
            elif event.type == "EpisodeFinish":
                print("Episode Finishing...")
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
        default=True,
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

