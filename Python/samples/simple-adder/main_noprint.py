#!/usr/bin/env python3

#TEST
import os
import time
import datetime

from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import SimulatorInterface, SimulatorState, SimulatorSessionResponse
from sim.simulator_model import SimulatorModel

def main(workspace=None,accesskey=None):
    """
    Creates a Bonsai simulator session and executes Bonsai episodes.
    """

    if workspace is None:
        workspace = os.getenv("SIM_WORKSPACE")
    
    if accesskey is None:
        accesskey = os.getenv("SIM_ACCESS_KEY")

    config_client = BonsaiClientConfig()
    #config_client.enable_logging = True
    client = BonsaiClient(config_client)

    registration_info = SimulatorInterface(
        name="simple-adder-sim",
        timeout=60,
        simulator_context=config_client.simulator_context,
        description=None,
    )

    registered_session: SimulatorSessionResponse = client.session.create(workspace_name=config_client.workspace, body=registration_info)
 
    sequence_id = 1
    sim_model = SimulatorModel()
    sim_model_state = { 'sim_halted': False }

    while True:
        sim_state = SimulatorState(sequence_id=sequence_id, state=sim_model_state, halted=sim_model_state.get('sim_halted', False))
        event = client.session.advance(
            workspace_name=config_client.workspace,
            session_id=registered_session.session_id,
            body=sim_state,
        )
        sequence_id = event.sequence_id

        if event.type == "Idle":
            time.sleep(event.idle.callback_time)
        elif event.type == "EpisodeStart":
            sim_model_state = sim_model.reset(event.episode_start.config)
        elif event.type == "EpisodeStep":

            s = datetime.datetime.now().second

            if s % 5 == 0:
                print('sleeping for 120 seconds')
                time.sleep(120)

            sim_model_state = sim_model.step(event.episode_step.action)
        elif event.type == "EpisodeFinish":
            sim_model_state = { 'sim_halted': False }
        elif event.type == "Unregister":
            return

if __name__ == "__main__":
    
    import argparse

    parser = argparse.ArgumentParser(description="Bonsai and Simulator Integration...")
   
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
    
    args, _ = parser.parse_known_args()

    main(workspace=args.workspace,accesskey=args.accesskey)
