#!/usr/bin/env python
"""
Microsoft-Bonsai-API integration with House Energy Simulator
"""

import os
import pathlib
import time
import datetime
import random
from distutils.util import strtobool
from typing import Any, Dict, List, Union
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv, set_key
from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorInterface,
    SimulatorState,
)

from policies import random_policy, forget_memory, brain_policy
from sim import house_simulator

LOG_PATH = "logs"

def ensure_log_dir(log_full_path):
    """
    Ensure the directory for logs exists — create if needed.
    """
    print(f"logfile: {log_full_path}")
    logs_directory = pathlib.Path(log_full_path).parent.absolute()
    print(f"Checking {logs_directory}")
    if not pathlib.Path(logs_directory).exists():
        print(
            "Directory does not exist at {0}, creating now...".format(
                str(logs_directory)
            )
        )
        logs_directory.mkdir(parents=True, exist_ok=True)


class TemplateSimulatorSession:
    def __init__(
        self,
        modeldir: str = "sim",
        render: bool = False,
        log_data: bool = False,
        log_file_name: str = None,
        env_name: str = "HouseEnergy",
    ):
        """Template for simulating sessions with microsoft_bonsai_api

        Parameters
        ----------
        modeldir: str, optional
            directory where you sim folder lives
        render: bool, optional
            render the current iteration
        env_name: str, optional
            name of simulator environment, registered by SimulatorInterface 
        """

        self.modeldir = modeldir
        self.env_name = env_name
        self.default_config = {
            "K": 0.5,
            "C": 0.3,
            "Qhvac": 9,
            "Tin_initial": 25,
            "Tout_median": 25,
            "Tout_amplitude": 5,
            "Tset_start": 25,
            "Tset_stop": 20,
            "Tset_transition": 144,
            "timestep": 5,
            "horizon": 288,
        }
        self._reset()
        self.terminal = False
        self.render = render
        self.log_data = log_data
        if not log_file_name:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            log_file_name = current_time + "_" + env_name + "_log.csv"

        self.log_full_path = os.path.join(LOG_PATH, log_file_name)
        ensure_log_dir(self.log_full_path)

    def get_state(self) -> Dict[str, float]:
        """ Called to retreive the current state of the simulator. """

        sim_state = {
            "Tset": float(self.simulator.Tset),
            "Tin": float(self.simulator.Tin),
            "Tout": float(self.simulator.Tout),
            "power": float(self.simulator.get_Power()),
        }

        return sim_state

    def _reset(self, config: dict = None):
        """Helper function for resetting a simulator environment

        Parameters
        ----------
        config : dict, optional
            [description], by default None
        """

        if config:
            self.sim_config = config
        else:
            self.sim_config = self.default_config

        self.simulator = house_simulator.House(
            K=self.sim_config["K"],
            C=self.sim_config["C"],
            Qhvac=self.sim_config["Qhvac"],
            Tin_initial=self.sim_config["Tin_initial"],
            Tout_median=self.sim_config["Tout_median"],
            Tout_amplitude=self.sim_config["Tout_amplitude"],
            Tset_start=self.sim_config["Tset_start"],
            Tset_stop=self.sim_config["Tset_stop"],
            Tset_transition=self.sim_config["Tset_transition"],
        )
        self.simulator.build_schedule()

    def episode_start(self, config: Dict[str, Any] = None):
        """Method invoked at the start of each episode with a given 
        episode configuration.

        Parameters
        ----------
        config : Dict[str, Any]
            SimConfig parameters for the current episode defined in Inkling
        """
        self.config = config
        self._reset(config)

    def episode_step(self, action: Dict[str, Any]):
        """Called for each step of the episode 

        Parameters
        ----------
        action : Dict[str, Any]
            BrainAction chosen from the Bonsai Service, prediction or exploration
        """

        self.simulator.update_hvacON(action["hvacON"])
        self.simulator.update_Tin()
        if self.render:
            self.sim_render()

    def sim_render(self):

        if self.render:
            self.simulator.show()

    def halted(self) -> bool:
        """Should return True if the simulator cannot continue"""
        return self.terminal

    def random_policy(self, state: Dict = None) -> Dict:

        return random_policy()

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

        # def add_prefixes(d, prefix: str):
        #     return {f"{prefix}_{k}": v for k, v in d.items()}
        
        # state = add_prefixes(state, "state")
        # action = add_prefixes(action, "action")
        # config = add_prefixes(self.sim_config, "config")
        config = self.sim_config
        data = {**state, **action, **config}
        data["episode"] = episode
        data["iteration"] = iteration
        log_df = pd.DataFrame(data, index=[0])
        
        if os.path.exists(self.log_full_path):
            log_df.to_csv(
                path_or_buf=self.log_full_path, mode="a", header=False, index=False
            )
        else:
            log_df.to_csv(
                path_or_buf=self.log_full_path, mode="w", header=True, index=False
            )

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

def test_policy(
    render: bool = False,
    num_iterations: int = 288,
    log_iterations: bool = False,
    policy=random_policy,
    policy_name: str = "random",
    scenario_file: str="assess_config.json",
):
    """Test a policy using random actions over a fixed number of episodes

    Parameters
    ----------
    render : bool, optional
        Flag to turn visualization on
    """
    
    # Use custom assessment scenario configs
    with open(scenario_file) as fname:
        assess_info = json.load(fname)
    scenario_configs = assess_info['episodeConfigurations']
    num_episodes = len(scenario_configs)+1

    current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_file_name = current_time + "_" + policy_name + "_log.csv"
    sim = TemplateSimulatorSession(
        render=render, log_data=log_iterations, log_file_name=log_file_name
    )
    for episode in range(1, num_episodes):
        iteration = 1
        terminal = False
        sim_state = sim.episode_start(config=scenario_configs[episode-1])
        sim_state = sim.get_state()
        
        if any('exported_brain_url' in key for key in policy.keywords):
            # Reset the Memory vector because exported brains don't understand episodes 
            url = '{}/v1'.format(policy.keywords['exported_brain_url'])
            forget_memory(url)

        if log_iterations:
            action = policy(sim_state)
            for key, value in action.items():
                action[key] = None
            sim.log_iterations(sim_state, action, episode, iteration)
        print(f"Running iteration #{iteration} for episode #{episode}")
        iteration += 1
        while not terminal:
            action = policy(sim_state)
            sim.episode_step(action)
            sim_state = sim.get_state()
            if log_iterations:
                sim.log_iterations(sim_state, action, episode, iteration)
            print(f"Running iteration #{iteration} for episode #{episode}")
            print(f"Observations: {sim_state}")
            iteration += 1
            terminal = iteration >= num_iterations+2 or sim.halted()

    return sim

def main(
    render: bool = False,
    log_iterations: bool=False,
    config_setup: bool = False, 
    env_file: Union[str, bool]=".env",
    workspace: str=None,
    accesskey: str=None,
):
    """Main entrypoint for running simulator connections

    Parameters
    ----------
    render : bool, optional
        visualize steps in environment, by default True, by default False
    log_iterations: bool, optional
        log iterations during training to a CSV file
    config_setup: bool, optional
        if enabled then uses a local `.env` file to find sim workspace id and access_key
    env_file: str, optional
        if config_setup True, then where the environment variable for lookup exists
    workspace: str, optional
        optional flag from CLI for workspace to override
    accesskey: str, optional
        optional flag from CLI for accesskey to override
    """

    # check if workspace or access-key passed in CLI
    use_cli_args = all([workspace, accesskey])

    # use dotenv file if provided
    use_dotenv = env_file or config_setup

    # check for accesskey and workspace id in system variables
    # Three scenarios
    # 1. workspace and accesskey provided by CLI args
    # 2. dotenv provided
    # 3. system variables
    # do 1 if provided, use 2 if provided; ow use 3; if no sys vars or dotenv, fail

    if use_cli_args:
        # BonsaiClientConfig will retrieve as environment variables
        os.environ["SIM_WORKSPACE"] = workspace
        os.environ["SIM_ACCESS_KEY"] = accesskey
    elif use_dotenv:
        if not env_file:
            env_file = ".env"
        print(
            f"No system variables for workspace-id or access-key found, checking in env-file at {env_file}"
        )
        workspace, accesskey = env_setup(env_file)
        load_dotenv(env_file, verbose=True, override=True)
    else:
        try:
            workspace = os.environ["SIM_WORKSPACE"]
            accesskey = os.environ["SIM_ACCESS_KEY"]
        except:
            raise IndexError(
                f"Workspace or access key not set or found. Use --config-setup for help setting up."
            )

    # Grab standardized way to interact with sim API
    sim = TemplateSimulatorSession(render=render, log_data=log_iterations)

    # Configure client to interact with Bonsai service
    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    # Create simulator session and init sequence id
    registration_info = SimulatorInterface(
        name=sim.env_name,
        timeout=60,
        simulator_context=config_client.simulator_context,
    )

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
                print(
                    "Simulator Session unregistered by platform because '{}', Registering again!".format(
                        event.unregister.details
                    )
                )
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
        "--render", action="store_true", default=False, help="Render training episodes",
    )
    parser.add_argument(
        "--log-iterations",
        action="store_true",
        default=False,
        help="Log iterations during training",
    )
    parser.add_argument(
        "--config-setup",
        action="store_true",
        default=False,
        help="Use a local environment file to setup access keys and workspace ids",
    )
    parser.add_argument(
        "--env-file",
        type=str,
        metavar="ENVIRONMENT FILE",
        help="path to your environment file",
        default=None,
    )
    parser.add_argument(
        "--workspace",
        type=str,
        metavar="WORKSPACE ID",
        help="your workspace id",
        default=None,
    )
    parser.add_argument(
        "--accesskey",
        type=str,
        metavar="Your Bonsai workspace access-key",
        help="your bonsai workspace access key",
        default=None,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--test-random",
        action="store_true",
        help="Run simulator locally with a random policy, without connecting to platform",
    )

    group.add_argument(
        "--test-exported",
        type=int,
        const=5000,  # if arg is passed with no PORT, use this
        nargs="?",
        metavar="PORT",
        help="Run simulator with an exported brain running on localhost:PORT (default 5000)",
    )

    parser.add_argument(
        "--iteration-limit",
        type=int,
        metavar="EPISODE_ITERATIONS",
        help="Episode iteration limit when running local test.",
        default=640,
    )
    
    parser.add_argument(
        "--custom-assess",
        type=str,
        default=None,
        help="Custom assess config json filename",
    )

    args, _ = parser.parse_known_args()
    
    scenario_file = 'assess_config.json'
    if args.custom_assess:
        scenario_file = args.custom_assess

    if args.test_random:
        test_policy(
            render=args.render, log_iterations=args.log_iterations, policy=random_policy
        )
    elif args.test_exported:
        port = args.test_exported
        url = f"http://localhost:{port}"
        print(f"Connecting to exported brain running at {url}...")
        trained_brain_policy = partial(brain_policy, exported_brain_url=url)
        test_policy(
            render=args.render,
            log_iterations=args.log_iterations,
            policy=trained_brain_policy,
            policy_name="exported",
            num_iterations=args.iteration_limit,
            scenario_file=scenario_file,
        )
    else:
        main(
            config_setup=args.config_setup,
            render=args.render,
            log_iterations=args.log_iterations,
            env_file=args.env_file,
            workspace=args.workspace,
            accesskey=args.accesskey,
        )
