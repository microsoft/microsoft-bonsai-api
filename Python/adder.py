"""
SDK3 Simulator the Adder that uses the simulators/ API.
This works with the pdp_stub scholar,
and is intended for testing purposes only!

This code takes a --latency <seconds> argument.
If this flag is present, then the simulator will
sleep for this many seconds between sending state
messages.

This code takes a --sim-context.
The SIM_CONTEXT environment variable works the same way (cmd-line param overrides env var)

This code takes a --access-key argument
The SIM_ACCESS_KEY environment variable works the same way (param overrides env var)

Requires --sim-api-host or SIM_API_HOST, that points at the simulator gateway address

Requires --sim-workspace or SIM_WORKSPACE
"""

import os
import sys
import time
import datetime
import requests
import json

from microsoft_bonsai_api.simulator._simulator_api import *
from microsoft_bonsai_api.simulator.models._models_py3 import *
from microsoft_bonsai_api import BonsaiClient, CreateSimContext


def main():

    rest_api = None
    session_id = ""

    try:
        # parse the arguments and environment variables
        c = CreateSimContext("Train", "00a5e6686af84f1f", "AdderSdk3", 4, "addition")
        params = {
            "latency": 0.0,
            "api-host": os.getenv("SIM_API_HOST", ""),
            "workspace": os.getenv("SIM_WORKSPACE", ""),
            "access-key": os.getenv("SIM_ACCESS_KEY", "bonsai nothing"),
            "sim-context": c,  # os.getenv('SIM_CONTEXT', ''),
        }

        # Override / augment environment variables with cmd line

        param_name = None
        for arg in sys.argv:
            if param_name is None and arg.startswith("--") and arg[2:] in params:
                param_name = arg[2:]

            elif param_name is not None:
                params[param_name] = arg
                param_name = None

        error_strings = []
        if not params["api-host"]:
            error_strings.append(
                "Must define an api host in SIM_API_HOST or --api-host"
            )
        if not params["workspace"]:
            error_strings.append(
                "Must define a workspace in SIM_WORKSPACE or --workspace"
            )

        if len(error_strings) > 0:
            raise RuntimeError("\n".join(error_strings))

        latency_seconds = float(params["latency"])

        if latency_seconds:
            print("Using latency = {} seconds".format(latency_seconds))

        # build the api handler
        rest_api = BonsaiClient(
            workspace=params["workspace"],
            host=params["api-host"],
            access_key=params["access-key"],
        )

        capabilities = {
            "headless": True,
            "braking": "anti-lock",
            "hardness": 6,
        }

        json_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "adder_description.json"
        )
        with open(json_file_path, "r") as file:
            json_interface = file.read()
        description = json.loads(json_interface)

        # register this simulator
        register_response: SimulatorSessionResponse = rest_api.create_session(
            "the_simulator",
            latency_seconds * 2.0,
            simulator_context=params["sim-context"],
            capabilities=capabilities,
            description=description,
        )

        print("REGISTER, session: -> {}".format(register_response.session_id))

        # extract the session id from the response
        session_id = register_response.session_id
        sequence_id = 1

        # set up our initial state
        value1 = 2
        value2 = 5
        reward = 0.0
        total_episode_reward = 0.0
        episode_iterations = 0

        # Loop until Unregister or Ctrl+C
        event_type = "Idle"

        while event_type != "Unregister":

            # invoke SimulatorGateway/Advance
            advance_time = datetime.datetime.utcnow()
            advance_response: Event = rest_api.advance(
                session_id,
                sequence_id,
                {"value1": value1, "value2": value2, "_reward": reward},
            )

            if 0 == (episode_iterations % 100):
                print(advance_time, "ADVANCE -> {}".format(advance_response))

            event: Event = advance_response
            event_type = event.type

            # Handle the response
            if event_type == "Idle":
                waitForSeconds = event.idle.callback_time
                if waitForSeconds > 0.0:
                    print("Sleeping for", waitForSeconds, "seconds")
                    time.sleep(waitForSeconds)
                # just try again

            elif event_type == "Unregister":
                # will break out of loop!
                rest_api = None
                session_id = ""

            elif event_type == "EpisodeStart":
                # re-initialize the simulator state
                value1 = 2
                value2 = 5
                reward = 0.0
                total_episode_reward = 0
                episode_iterations = 0

            elif event_type == "EpisodeStep":
                # check the sum in the response
                action = event.episode_step.action
                if action["sum"] == (value1 + value2) % 10:
                    reward = 1.0
                else:
                    reward = 0.0

                total_episode_reward += reward
                episode_iterations += 1

                # Sleep while we compute our next state
                if params["latency"] > 0:
                    time.sleep(params["latency"])

                # update the simulator state
                value1 += 2
                if value1 > 9:
                    value1 -= 10

                value2 += 3
                if value2 > 9:
                    value2 -= 10

            elif event_type == "EpisodeFinish":
                # just print out the episode finish
                print(
                    "Episode finished! Total reward = {} / {}".format(
                        total_episode_reward, episode_iterations
                    )
                )

            # the simulator's sequence id is always the last one it received
            sequence_id = event.sequence_id

    except KeyboardInterrupt:
        pass

    finally:
        if rest_api is not None and session_id:
            pass
            print("\n\n\nUnregistering {}".format(session_id))
            try:
                deregister_response = rest_api.delete_session(session_id)
                print(datetime.datetime.utcnow(), "UNREGISTER ->", deregister_response)
            except:
                print(datetime.datetime.utcnow(), "UNREGISTER -> CANNOT")


if __name__ == "__main__":
    main()
