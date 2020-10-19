#!/usr/bin/env python
"""
Microsoft-Bonsai-API integration with House Energy Simulator
"""

import os
from dotenv import load_dotenv, set_key
import time
from typing import Dict, Any, List
from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorState,
    SimulatorInterface,
)

from sim import house_simulator
from policies import random_policy

dir_path = os.path.dirname(os.path.realpath(__file__))


class TemplateSimulatorSession:
    def __init__(
        self, modeldir: str = "sim", render: bool = False, env_name: str = "HouseEnergy"
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
        print("Using simulator file from: ", os.path.join(dir_path, self.modeldir))
        self.default_config = {
            "K": 0.5,
            "C": 0.3,
            "Qhvac": 9,
            "Tin_initial": 30,
            "schedule_index": 2,
            "number_of_days": 1,
            "timestep": 5,
            "max_iterations": int(1 * 24 * 60 / 5),
        }
        self._reset()
        self.terminal = False

    def get_state(self) -> Dict[str, float]:
        """ Called to retreive the current state of the simulator. """

        sim_state = {
            "Tset": float(self.simulator.Tset),
            "Tset1": float(self.simulator.Tset1),  # forecast at +1 iteration
            "Tset2": float(self.simulator.Tset2),  # forecast at +2 iterations
            "Tset3": float(self.simulator.Tset3),  # forecast at +3 iterations
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
        )
        self.simulator.setup_schedule(
            days=self.sim_config["number_of_days"],
            timestep=self.sim_config["timestep"],
            schedule_index=self.sim_config["schedule_index"],
            max_iterations=288,
        )

    def episode_start(self, config: Dict[str, Any] = None):
        """Method invoked at the start of each episode with a given 
        episode configuration.

        Parameters
        ----------
        config : Dict[str, Any]
            SimConfig parameters for the current episode defined in Inkling
        """

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

    def sim_render(self):

        if self.render:
            self.simulator.show()

    def halted(self) -> bool:
        """Should return True if the simulator cannot continue"""
        return self.terminal

    def random_policy(self, state: Dict = None) -> Dict:

        return random_policy()


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


def test_random_policy(num_episodes: int = 10):
    """Test a policy using random actions over a fixed number of episodes

    Parameters
    ----------
    num_episodes : int, optional
        number of iterations to run, by default 10
    """

    sim = TemplateSimulatorSession()
    for episode in range(num_episodes):
        iteration = 0
        terminal = False
        obs = sim.episode_start()
        while not terminal:
            action = sim.random_policy()
            sim.episode_step(action)
            sim_state = sim.get_state()
            print(f"Running iteration #{iteration} for episode ${episode}")
            print(f"Observations: {sim_state}")
            iteration += 1


def main(render: bool = False):
    """Main entrypoint for running simulator connections

    Parameters
    ----------
    render : bool, optional
        visualize steps in environment, by default True, by default False
    """

    # workspace environment variables
    # env_setup()
    # load_dotenv(verbose=True, override=True)

    # Grab standardized way to interact with sim API
    sim = TemplateSimulatorSession(render=render)

    # Configure client to interact with Bonsai service
    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    # # Load json file as simulator integration config type file
    # with open("interface.json") as file:
    #     interface = json.load(file)

    # Create simulator session and init sequence id
    registration_info = SimulatorInterface(
        name=sim.env_name,
        timeout=60,
        simulator_context=config_client.simulator_context,
    )
    registered_session = client.session.create(
        workspace_name=config_client.workspace, body=registration_info
    )
    print("Registered simulator.")
    sequence_id = 1

    def CreateSession(registration_info: SimulatorInterface, config_client: BonsaiClientConfig):
        """Creates a new Simulator Session and returns new sessoin, sequenceId
        """

        try:
            print("config: {}, {}".format(config_client.server, config_client.workspace))
            registered_session: SimulatorSessionResponse = client.session.create(
                workspace_name=config_client.workspace, body=registration_info
            )
            print("Registered simulator. {}".format(registered_session.session_id))

            return registered_session, 1
        except HttpResponseError as ex:
            print("HttpResponseError in Registering session: StatusCode: {}, Error: {}, Exception: {}".format(ex.status_code, ex.error.message, ex))
            raise ex
        except Exception as ex:
            print("UnExpected error: {}, Most likely, It's some network connectivity issue, make sure, you are able to reach bonsai platform from your PC.".format(ex))
            raise ex

    registered_session, sequence_id = CreateSession(registration_info, config_client)
    episode = 0
    iteration = 0

    try:
        while True:
            # Advance by the new state depending on the event type
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
                print("[{}] Last Event: {}".format(time.strftime("%H:%M:%S"), event.type))
            except HttpResponseError as ex:
                print("HttpResponseError in Advance: StatusCode: {}, Error: {}, Exception: {}".format(ex.status_code, ex.error.message, ex))
                # This can happen in network connectivity issue, though SDK has retry logic, but even after that request may fail, 
                # if your network has some issue, or sim session at platform is going away..
                # So let's re-register sim-session and get a new session and continue iterating. :-) 
                registered_session, sequence_id = CreateSession(registration_info, config_client)
                continue
            except Exception as err:
                print("Unexpected error in Advance: {}".format(err))
                # Ideally this shouldn't happen, but for very long-running sims It can happen with various reasons, let's re-register sim & Move on.
                # If possible try to notify Bonsai team to see, if this is platform issue and can be fixed.
                registered_session, sequence_id = CreateSession(registration_info, config_client)
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
                print("Simulator Session unregistered by platform, Registering again!")
                registered_session, sequence_id = CreateSession(registration_info, config_client)
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
    main(render=False)
    # test_random_policy()
