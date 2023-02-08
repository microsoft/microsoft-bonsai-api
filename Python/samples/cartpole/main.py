#!/usr/bin/env python3

import time
import json
import argparse
from exported_brain import test_policy
from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import SimulatorInterface, SimulatorState, SimulatorSessionResponse
from sim.simulator_model import SimulatorModel


def main():
    """
    Creates a Bonsai simulator session and executes Bonsai episodes.
    """

    # workspace = os.getenv("SIM_WORKSPACE")
    # accesskey = os.getenv("SIM_ACCESS_KEY")

    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)
    
    # Load json file as simulator integration config type file
    with open("interface.json") as file:
        interface = json.load(file)
    
    sim_model = SimulatorModel()

    registration_info = SimulatorInterface(
        name=sim_model.sim_name,
        timeout=60,
        simulator_context=config_client.simulator_context,
        description=interface["description"]
    )

    print(f"config: {config_client.server}, {config_client.workspace}")
    registered_session: SimulatorSessionResponse = client.session.create(workspace_name=config_client.workspace, body=registration_info)
    print(f"Registered simulator. {registered_session.session_id}")

    sequence_id = 1
    sim_model_state = { 'sim_halted': False }

    try:
        while True:
            sim_state = SimulatorState(sequence_id=sequence_id, state=sim_model_state, halted=sim_model_state.get('sim_halted', False))
            event = client.session.advance(
                workspace_name=config_client.workspace,
                session_id=registered_session.session_id,
                body=sim_state,
            )
            sequence_id = event.sequence_id
            print(f'[{time.strftime("%H:%M:%S")}] Last Event: {event.type}')

            if event.type == "Idle":
                time.sleep(event.idle.callback_time)
            elif event.type == "EpisodeStart":
                print(f"config {event.episode_start.config}")
                sim_model_state = sim_model.reset(event.episode_start.config)
                print(f"state {sim_model_state}")
            elif event.type == "EpisodeStep":
                print(f"action {event.episode_step.action}")
                sim_model_state = sim_model.step(event.episode_step.action)
                print(f"state {sim_model_state}")
            elif event.type == "EpisodeFinish":
                sim_model_state = { 'sim_halted': False }
            elif event.type == "Unregister":
                print(f"Simulator Session unregistered by platform because '{event.unregister.details}'")
                return
    except BaseException as err:
        client.session.delete(workspace_name=config_client.workspace, session_id=registered_session.session_id)
        print(f"Unregistered simulator because {type(err).__name__}: {err}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Bonsai and Simulator Integration...")
    parser.add_argument(
        "--render", action="store_true", default=False, help="Render training episodes",
    )
    
    parser.add_argument(
        "--exported-brain-iterations",
        type=int,
        help="Number of iterations per episode when running test.",
        default=200,
    )
    
    parser.add_argument(
        "--exported-brain-episodes",
        type=int,
        help="Number of episodes when running test.",
        default=10,
    )
    
    parser.add_argument(
        "--exported-brain-url",
        type=str,
        help="Run simulator with an exported brain at url. (ex. http://localhost:5000)",
    )

    args, _ = parser.parse_known_args()

    if args.exported_brain_url:
        url = args.exported_brain_url
        print(f"Connecting to exported brain running at {url}...")
        test_policy(
            render=args.render,
            exported_brain_iterations=args.exported_brain_iterations,
            exported_brain_episodes=args.exported_brain_episodes,
            exported_brain_url=url
        )
    else:
        main(render=args.render)

