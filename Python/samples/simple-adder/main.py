#!/usr/bin/env python3

import os
import time
from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import SimulatorInterface, SimulatorState, SimulatorSessionResponse
from azure.core.exceptions import HttpResponseError
from sim import Sim

def main():
    workspace = os.getenv("SIM_WORKSPACE")
    accesskey = os.getenv("SIM_ACCESS_KEY")

    simulator = Sim()

    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    registration_info = SimulatorInterface(
        name="simple-adder",
        timeout=60,
        simulator_context=config_client.simulator_context,
        description=None,
    )

    print(f"config: {config_client.server}, {config_client.workspace}")
    registered_session: SimulatorSessionResponse = client.session.create(workspace_name=config_client.workspace, body=registration_info)
    print(f"Registered simulator. {registered_session.session_id}")

    sequence_id = 1

    try:
        while True:
            sim_state = SimulatorState(sequence_id=sequence_id, state=simulator.state.copy(), halted=simulator.halted)
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
                simulator.reset(event.episode_start.config)
                print(f"state {simulator.state}")
            elif event.type == "EpisodeStep":
                print(f"action {event.episode_step.action}")
                simulator.step(event.episode_step.action)
                print(f"state {simulator.state}")
            elif event.type == "EpisodeFinish":
                pass
            elif event.type == "Unregister":
                print(f"Simulator Session unregistered by platform because '{event.unregister.details}'")
                return
    except BaseException as err:
        client.session.delete(workspace_name=config_client.workspace, session_id=registered_session.session_id)
        print(f"Unregistered simulator because {type(err).__name__}: {err}")

if __name__ == "__main__":
    main()
