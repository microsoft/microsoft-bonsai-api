#!/usr/bin/env python3

from asyncio.log import logger
from cmath import log
import os
import time
from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import SimulatorInterface, SimulatorState, SimulatorSessionResponse
from sim.simulator_model import SimulatorModel

#additional imports
from logging import Logger
import logging.handlers
import sys

def main():
        """
        Creates a Bonsai simulator session and executes Bonsai episodes.
        """

        workspace = os.getenv("SIM_WORKSPACE")
        accesskey = os.getenv("SIM_ACCESS_KEY")

        config_client = BonsaiClientConfig()
        config_client.enable_logging = True #enable DEBUG on the logger
        
        client = BonsaiClient(config_client)
        logger = client.logger

        registration_info = SimulatorInterface(
            name="simple-adder-sim",
            timeout=60,
            simulator_context=config_client.simulator_context,
            description=None,
        )

        logger.info(f"config: {config_client.server}, {config_client.workspace}")
        client.create(workspace_name=config_client.workspace, body=registration_info)
        logger.info(f"Registered simulator. {client.session_id}")

        #sequence_id = 1
        sim_model = SimulatorModel()
        sim_model_state = { 'sim_halted': False }

        try:
            while True:
                #sim_state = SimulatorState(sequence_id=sequence_id, state=sim_model_state, halted=sim_model_state.get('sim_halted', False))
                
                event = client.advance(
                    workspace_name=config_client.workspace,
                    state=sim_model_state, 
                    halted=sim_model_state.get('sim_halted', False)
                )
                #sequence_id = event.sequence_id
                logger.info(f'Last Event: {event.type}')

                if event.type == "Idle":
                    time.sleep(event.idle.callback_time)
                elif event.type == "EpisodeStart":
                    logger.info(f"config {event.episode_start.config}")
                    sim_model_state = sim_model.reset(event.episode_start.config)
                    logger.info(f"state {sim_model_state}")
                elif event.type == "EpisodeStep":
                    logger.info(f"action {event.episode_step.action}")
                    sim_model_state = sim_model.step(event.episode_step.action)
                    logger.info(f"state {sim_model_state}")
                elif event.type == "EpisodeFinish":
                    sim_model_state = { 'sim_halted': False }
                elif event.type == "Unregister":
                    logger.info(f"Simulator Session unregistered by platform because '{event.unregister.details}'")
                    return
        except BaseException as err:
            client.delete(workspace_name=config_client.workspace)
            logger.info(f"Unregistered simulator because {type(err).__name__}: {err}")

if __name__ == "__main__":
   main()
