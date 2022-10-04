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
from sim.simulator_model import SimulatorModel
import gym

from policies import brain_policy, chosen_policy
import argparse

LOG_PATH = "logs"

def random_policy(sim_state):

    env = gym.make("LunarLanderContinuous-v2") #TOREMOVE:("highway-v0")
    env.reset()
    action = env.action_space.sample()
    return {"engine1": action[0], "engine2": action[1]}

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
    sim_session = SimulatorModel(
        render=render,
        log_data=log_iterations,
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
    debug: bool = False,
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

    try: 
        workspace = os.environ["SIM_WORKSPACE"]
        accesskey = os.environ["SIM_ACCESS_KEY"]
    except:
        raise IndexError(
            f"Workspace or access key not set or found. Use --config-setup for help setting up."
        )


    # Configure client to interact with Bonsai service
    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    # Create simulator session and init sequence id
    registration_info = SimulatorInterface(
        name="LunarLanderContinuous-v2",
        timeout=60,
        simulator_context=config_client.simulator_context,
    )

    print(
        "config: {}, {}".format(config_client.server, config_client.workspace)
    )
    registered_session: SimulatorSessionResponse = client.session.create(
        workspace_name=config_client.workspace, body=registration_info
    )
    print("Registered simulator. {}".format(registered_session.session_id))

    episode = 0
    iteration = 0
    sim_model = SimulatorModel(
        render=render,
        log_data=log_iterations,
        debug=debug
    )
    sim_model_state = { 'sim_halted': False }
    try:
        while True:
            # Advance by the new state depending on the event type
            # TODO: it's risky using `get_state` without first initializing the sim
            sim_state = SimulatorState(
                sequence_id=sequence_id, state=sim_model_state, halted=sim_model_state.get('sim_halted', False)
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
                continue
            except Exception as err:
                print("Unexpected error in Advance: {}".format(err))
                continue

            # Event loop
            if event.type == "Idle":
                time.sleep(event.idle.callback_time)
                print("Idling...")
            elif event.type == "EpisodeStart":
                print("Episode config being used:", event.episode_start.config)
                sim_model_state = sim_model.reset(event.episode_start.config)
                print(f"state {sim_model_state}")
                episode += 1
            elif event.type == "EpisodeStep":
                iteration += 1
                print(f"action {event.episode_step.action}")
                sim_model_state = sim_model.step(event.episode_step.action)
                print(f"state {sim_model_state}")
            elif event.type == "EpisodeFinish":
                print("Episode Finishing...")
                sim_model_state = { 'sim_halted': False }
                iteration = 0
            elif event.type == "Unregister":
                print(
                    "Simulator Session unregistered by platform because '{}', Registering again!".format(
                        event.unregister.details
                    )
                )
                return

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
        "--debug",
        default=False,
        help="Debug sim using default embedded methods in sim.py",
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
            debug=args.debug,
        )

