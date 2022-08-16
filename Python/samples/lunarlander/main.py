from functools import partial
import json
import random
import math
import time
import os
import pathlib
from dotenv import load_dotenv, set_key
import datetime
from typing import Dict, Any, Union
from microsoft_bonsai_api.simulator.client import BonsaiClientConfig, BonsaiClient
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorState,
    SimulatorInterface,
    SimulatorSessionResponse,
)
from azure.core.exceptions import HttpResponseError

import gym
from sim.LunarLander import LunarLander
from policies import brain_policy, chosen_policy
import argparse

LOG_PATH = "logs"


def random_policy(sim_state):

    env = gym.make("LunarLanderContinuous-v2") #TOREMOVE:("highway-v0")
    env.reset()
    action = env.action_space.sample()
    return {"engine1": action[0], "engine2": action[1]}


def ensure_log_dir(log_full_path: str):
    """Create a log directory if needed

    Parameters
    ----------
    log_full_path : str
        path of log directory
    """
    print(f"Log filename: {log_full_path}")
    logs_directory = pathlib.Path(log_full_path).parent.absolute()
    print(f"Log directory: {logs_directory}")
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
        render: bool = False,
        log_data: bool = False,
        log_file_name: str = None,
        env_name: str = "LunarLanderContinuous-v2",
        obs_type: str = "Kinematics", # TODO: Review if Kinematics is needed (config-related)
        debug: bool = True,
    ):
        """Lunar Lander simulation using the gym environment. See API docs for more information:
            https://www.gymlibrary.ml/environments/box2d/lunar_lander/

        Parameters
        ----------
        render : bool, optional
            render every control timestep of the environment, by default False
        log_data : bool, optional
            whether to MDP data to CSV, by default False
        log_file_name : str, optional
            where to log data, only applicable if `log_data=True`, by default None
        env_name : str, optional
            the name of the simulator environment to create, by default "highway-v0"
        obs_type: str, optional
            the type of observations received from simulator.
        """

        # Log data is disabled by default if using the logging from TemplateSimulatorSession.
        self.sim = LunarLander(render = render,
                               log_data = False, # Data disabled since it is taken care by this class.
                               log_file_name = log_file_name,
                               env_name = env_name,
                               obs_type = obs_type,
                               debug = debug)

        # Logging features
        self.log_data = log_data
        if not log_file_name:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            log_file_name = current_time + "_" + env_name + "_log.csv"

        self.log_full_path = os.path.join(LOG_PATH, log_file_name)
        ensure_log_dir(self.log_full_path)

        self.debug = debug


    def get_state(self) -> Dict[str, Any]:
        """Extract state from MDP

        Returns
        -------
        Dict[str, Any]
            Get states from current simulator environment.
        """

        sim_state = self.sim.get_state()

        state = {
            "x_position": sim_state["x_position"],
            "y_position": sim_state["y_position"],
            "x_velocity": sim_state["x_velocity"],
            "y_velocity": sim_state["y_velocity"],
            "angle": sim_state["angle"],
            "rotation": sim_state["rotation"],
            "left_leg": sim_state["left_leg"],
            "right_leg": sim_state["right_leg"],
            # Converting to float due to parsing errors detecting during brain training
            "ship_crashed": bool(sim_state["ship_crashed"]),
            "ship_landed": bool(sim_state["ship_landed"]),
            # Config Params
            "randomized_strength": float(sim_state["randomized_strength"]),
            "randomized_steps": float(sim_state["randomized_steps"]),
            "delta_action": bool(sim_state["delta_action"]),
            # Aux vars -- Useful for delta actions
            "prev_engine1": float(sim_state["prev_engine1"]),
            "prev_engine2": float(sim_state["prev_engine2"]),
            # Gym reward/terminal
            "gym_reward": float(sim_state["gym_reward"]),
            "gym_terminal": bool(sim_state["gym_terminal"]),
            # UNUSED AT THE MOMENT
            "concept": float(sim_state["concept"]),
        }

        return state

    def episode_start(self, config: Union[Dict[str, Any], None] = None):
        """Initialize a new episode of the simulator with configuration parameters.

        Parameters
        ----------
        config : Dict[str, Any] or None
            paramters for initializing the simulator. See 'sim/LunarLander.py' to see all config parameters.
        """
        
        # Start simulation.
        self.sim.episode_start(config)

        # Logging functionality.
        if self.log_data:
            action = {"engine1": None, "engine2": None}
            self.log_iterations(state=self.get_state(),
                                action=action,
                                episode=self.sim.episode,
                                iteration=self.sim.iteration)
        
        

    def episode_step(self, action: Dict[str, Any]):
        """Step through the environment. See allowable actions here: https://highway-env.readthedocs.io/en/latest/actions/index.html

        Parameters
        ----------
        action : Dict[str, Any]
            Control/action to iterate in the environment
        """
        
        # Apply action to sim.
        self.sim.episode_step(action)

        # Logging functionality.
        if self.log_data:
            self.log_iterations(state=self.get_state(),
                                action=action,
                                episode=self.sim.episode,
                                iteration=self.sim.iteration)
        

    def halted(self) -> bool:
        """Terminate the episode if and only if the simulator cannot be continued. This washes away the entire episode from training.
        """

        return False

    @property
    def terminal(self):
        return self.sim.terminal

    @property
    def env_name(self):
        return self.sim.env_name

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
        
        # Custom way to turn lists into strings for logging
        log_state = state.copy()
        
        for key, value in log_state.items():
            if type(value) == list:
                log_state[key] = str(log_state[key])

        log_state = add_prefixes(log_state, "state")
        action = add_prefixes(action, "action")
        config = add_prefixes(self.sim.config, "config")
        data = {**log_state, **action, **config}
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


def env_setup(env_file: str = ".env"):
    """Helper function to setup connection with Project Bonsai

    Returns
    -------
    Tuple
        workspace, and access_key
    """

    load_dotenv(dotenv_path=env_file, verbose=True, override=True)
    workspace = os.getenv("SIM_WORKSPACE")
    access_key = os.getenv("SIM_ACCESS_KEY")

    env_file_exists = os.path.exists(env_file)
    if not env_file_exists:
        open(env_file, "a").close()

    if not all([env_file_exists, workspace]):
        workspace = input("Please enter your workspace id: ")
        set_key(env_file, "SIM_WORKSPACE", workspace)
    if not all([env_file_exists, access_key]):
        access_key = input("Please enter your access key: ")
        set_key(env_file, "SIM_ACCESS_KEY", access_key)

    load_dotenv(dotenv_path=env_file, verbose=True, override=True)
    workspace = os.getenv("SIM_WORKSPACE")
    access_key = os.getenv("SIM_ACCESS_KEY")

    return workspace, access_key


def test_policy(
    render: bool = False,
    num_iterations: int = 640,
    log_iterations: bool = False,
    policy=random_policy,
    policy_name: str = "random",
    scenario_file: str = "test_scenarios.json",
    debug=True,
):
    """Test a policy using random actions or a trained brain over a fixed number of episodes

    Parameters
    ----------
    render : bool, optional
        [description], by default False
    num_iterations : int, optional
        [description], by default 640
    log_iterations : bool, optional
        [description], by default False
    policy : [type], optional
        [description], by default random_policy
    policy_name : str, optional
        [description], by default "random"
    scenario_file : str, optional
        list of episode initializations used in assessment, by default "test_scenarios.json"

    Returns
    -------
    [type]
        [description]
    """

    if type(policy) is str:
        policy_name = policy
        policy = lambda state: chosen_policy(state, policy_name=policy_name)
        if debug:
            print("\nRUNNING TEST POLICY:", policy_name, "\n")

    # Use custom assessment scenario configs
    with open(scenario_file) as fname:
        assess_info = json.load(fname)
    scenario_configs = assess_info["episodeConfigurations"]
    num_episodes = len(scenario_configs) + 1

    current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_file_name = current_time + "_" + policy_name + "_log.csv"
    sim_session = TemplateSimulatorSession(
        render=render,
        log_data=log_iterations,
        log_file_name=log_file_name,
        debug=debug
    )
    for episode in range(1, num_episodes):
        iteration = 1
        terminal = False
        sim_state = sim_session.episode_start(config=scenario_configs[episode - 1])
        sim_state = sim_session.get_state()
        if debug:
            # Logging now happens directly within TemplateSimulatorSession.
            print(f"\nRunning iteration #{iteration} for episode #{episode}")
        iteration += 1
        while not terminal:
            action = policy(sim_state)
            sim_session.episode_step(action)
            sim_state = sim_session.get_state()
            # Logging now happens directly within TemplateSimulatorSession.
            
            if debug:
                print(f"Running iteration #{iteration} for episode #{episode}")
            iteration += 1
            terminal = iteration >= num_iterations + 2 or sim_session.terminal

    return sim_session


def main(
    render: bool = False,
    log_iterations: bool = False,
    config_setup: bool = False,
    env_file: Union[str, bool] = ".env",
    workspace: str = None,
    accesskey: str = None,
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
            # TODO: it's risky using `get_state` without first initializing the sim
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
                print("Episode config being used:", event.episode_start.config)
                sim.episode_start(event.episode_start.config)
                episode += 1
            elif event.type == "EpisodeStep":
                iteration += 1
                sim.episode_step(event.episode_step.action)
                # Logging happens directly within TemplateSimulatorSession.
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
        "--test-policy",
        type=str,
        help="Run simulator locally with an specified policy, without connecting to platform",
        default=None,
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

    if args.custom_assess:
        scenario_file = args.custom_assess

    if args.test_random:
        test_policy(
            render=args.render,
            log_iterations=args.log_iterations,
            policy=random_policy # FUNCTION type.
        )
    elif args.test_policy:
        test_policy(
            render=args.render,
            log_iterations=args.log_iterations,
            policy=args.test_policy # STR type.
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

