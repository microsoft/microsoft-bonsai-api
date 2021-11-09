#!/usr/bin/env python3

import os
import time
from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import SimulatorInterface, SimulatorState, SimulatorSessionResponse
from sim import Sim

def main():
    workspace = os.getenv("SIM_WORKSPACE")
    accesskey = os.getenv("SIM_ACCESS_KEY")

    sim_model = Sim()

    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    registration_info = SimulatorInterface(
        name="simple-adder-sim",
        timeout=60,
        simulator_context=config_client.simulator_context,
        description=None,
    )

    print(f"config: {config_client.server}, {config_client.workspace}")
    registered_session: SimulatorSessionResponse = client.session.create(workspace_name=config_client.workspace, body=registration_info)
    print(f"Registered simulator. {registered_session.session_id}")

    sequence_id = 1
    sim_model_halted = False
    sim_model_state = {}

    try:
        while True:
            sim_state = SimulatorState(sequence_id=sequence_id, state=sim_model_state, halted=sim_model_halted)
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
                sim_model_halted, sim_model_state = sim_model.reset(event.episode_start.config)
                if not sim_model_halted:
                    print(f"state {sim_model_state}")
            elif event.type == "EpisodeStep":
                print(f"action {event.episode_step.action}")
                sim_model_halted, sim_model_state = sim_model.step(event.episode_step.action)
                if not sim_model_halted:
                    print(f"state {sim_model_state}")
            elif event.type == "EpisodeFinish":
                sim_model_halted = False
                sim_model_state = {}
            elif event.type == "Unregister":
                print(f"Simulator Session unregistered by platform because '{event.unregister.details}'")
                return
    except BaseException as err:
        client.session.delete(workspace_name=config_client.workspace, session_id=registered_session.session_id)
        print(f"Unregistered simulator because {type(err).__name__}: {err}")

if __name__ == "__main__":
    main()
