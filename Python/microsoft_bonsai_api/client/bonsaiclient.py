import os
import sys
import time
from datetime import datetime
import requests
import json
from typing import Optional, Dict, Any

from microsoft_bonsai_api.simulator._simulator_api import *
from microsoft_bonsai_api.simulator.models import *
from .config import Config

# The API object that handles the REST connection to the bonsai platform.
class BonsaiClient(object):
    def __init__(self, config: Config):
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": config.access_key,
        }

        self.workspace = config.workspace
        self.sim_api = SimulatorAPI(base_url=config.server, headers=self._headers)

    def pretty_json(self, o):
        return json.dumps(o, sort_keys=True, indent=3, separators=(",", ": "))

    def create_session(
        self,
        simulator_name: str,
        timeout_seconds: float,
        simulator_context: str,
        capabilities: Optional[dict] = None,
        description: Optional[dict] = None,
    ):

        if capabilities is None:
            capabilities = {}

        if description is None:
            description = {}

        registration_info = {
            "name": simulator_name,
            "timeout": timeout_seconds,
            "capabilities": capabilities,
            "description": description,
            "simulatorContext": simulator_context,
        }

        print("Creating session with", self.pretty_json(registration_info), "\n\n")

        response = self.sim_api.session.create(self.workspace, registration_info)

        if isinstance(response, SimulatorSessionResponse):
            return response
        elif isinstance(response, ProblemDetails):
            # TODO: Investigate under what situations ProblemDetails is returned
            # ToDo: For each error response type, take actions such as retry.
            print(
                "Encountered Error in Creating Session. status: {}, reason: {}".format(
                    response.status, response.reason
                )
            )
        else:
            print("Unrecognised error in CreateSession: {}".format(response))

        return response

    def delete_session(self, session_id: str):
        response = self.sim_api.session.delete(self.workspace, session_id)

        if isinstance(response, ProblemDetails):
            print("Error in deleting session. Details: {}".format(response))
        else:
            print("Successfully deleted session")

        return response

    def list_sessions(self):
        response = self.sim_api.session.list(self.workspace)

        if isinstance(response, list):
            return response
        else:
            print("Error in deleting session. Details: {}".format(response))
            return None

    def fetch_action(self, session_id: str):
        response = self.sim_api.session.get_most_recent_action(
            self.workspace, session_id
        )

        if isinstance(response, Event):
            return response
        else:
            print("Error in FetchAction. Details: {}".format(response))
            return None

    def advance(self, session_id: str, sequence_id: int, state: Dict[str, Any]):
        json = {
            "session_id": session_id,
            "sequence_id": sequence_id,
            "state": state,
            "halted": False,
        }

        response = self.sim_api.session.advance(self.workspace, session_id, json)

        if isinstance(response, Event):
            return response
        else:
            print("Error in Advance session. Details: {}".format(response))
            return None
