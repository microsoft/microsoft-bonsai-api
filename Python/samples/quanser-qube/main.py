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
import time
from typing import Dict, Any, Optional
from microsoft_bonsai_api.simulator.client import BonsaiClientConfig, BonsaiClient
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorState,
    SimulatorInterface,
)

import argparse
from sim.qube_simulator import QubeSimulator

class TemplateSimulatorSession():
    def __init__(self, render):
        ## Initialize python api for simulator
        self.simulator = QubeSimulator()
        self.render = render

    def get_state(self) -> Dict[str, Any]:
        """Called to retreive the current state of the simulator. """
        return {
            ## Add simulator state as dictionary
            "theta": float(self.simulator.state[0]),
            "alpha": float(self.simulator.state[1]),
            "theta_dot": float(self.simulator.state[2]),
            "alpha_dot": float(self.simulator.state[3])
        }

    def episode_start(self, config: Dict[str, Any]):
        """ Called at the start of each episode """
        ## Add simulator reset api here using config from desired lesson in inkling
        self.simulator.reset(config)

    def episode_step(self, action: Dict[str, Any]):
        """ Called for each step of the episode """
        ## Add simulator step api here using action from Bonsai platform
        self.simulator.step(action['Vm'])

        if self.render:
            self.simulator.view()

    def halted(self) -> bool:
        """
        Should return True if the simulator cannot continue for some reason
        """
        return (
            False
        )


def main(render = False):
    # Grab standardized way to interact with sim API

    sim = TemplateSimulatorSession(render= render)

    # Configure client to interact with Bonsai service
    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    # Load json file as simulator integration config type file
    with open('interface.json') as file:
        interface = json.load(file)

    # Create simulator session and init sequence id
    registration_info = SimulatorInterface(
                            name=interface['name'], 
                            timeout=interface['timeout'], 
                            simulator_context=config_client.simulator_context, 
    )
    registered_session = client.session.create(
                            workspace_name=config_client.workspace, 
                            body=registration_info
    )
    print("Registered simulator.")
    sequence_id = 1

    try:
        while True:
            # Advance by the new state depending on the event type
            sim_state = SimulatorState(
                            sequence_id=sequence_id, state=sim.get_state(), 
                            halted=sim.halted()
            )
            event = client.session.advance(
                        workspace_name=config_client.workspace, 
                        session_id=registered_session.session_id, 
                        body=sim_state
            )
            sequence_id = event.sequence_id
            print("[{}] Last Event: {}".format(time.strftime('%H:%M:%S'), 
                                               event.type))

            # Event loop
            if event.type == 'Idle':
                time.sleep(event.idle.callback_time)
                print('Idling...')
            elif event.type == 'EpisodeStart':
                sim.episode_start(event.episode_start.config)
            elif event.type == 'EpisodeStep':
                sim.episode_step(event.episode_step.action)
            elif event.type == 'EpisodeFinish':
                print('Episode Finishing...')
            elif event.type == 'Unregister':
                print("Simulator Session unregistered by platform because '{}', Registering again!".format(event.unregister.details))
                client.session.delete(
                    workspace_name=config_client.workspace, 
                    session_id=registered_session.session_id
                )
                print("Unregistered simulator.")
            else:
                pass
    except KeyboardInterrupt:
        # Gracefully unregister with keyboard interrupt
        client.session.delete(
            workspace_name=config_client.workspace, 
            session_id=registered_session.session_id
        )
        print("Unregistered simulator.")
    except Exception as err:
        # Gracefully unregister for any other exceptions
        client.session.delete(
            workspace_name=config_client.workspace, 
            session_id=registered_session.session_id
        )
        print("Unregistered simulator because: {}".format(err))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='args for sim integration',
                                     allow_abbrev=False)
    parser.add_argument('--render', action='store_true')
    args, _ = parser.parse_known_args()
    main(render=args.render)