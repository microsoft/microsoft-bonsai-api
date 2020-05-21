import os
import sys
import time
from datetime import datetime
import requests
import json
from bonsai.simulatorapi.simulator_api import *
from bonsai.simulatorapi.models import *
from bonsai.simulatorapi import *

# The API object that handles the REST connection to the bonsai platform.
class BonsaiClient(object):
    
    def __init__(
        self,
        workspace:str,
        host:str,
        access_key:str
    ):
        # TODO: Use access_key!

        self._headers = {
            'Content-Type': 'application/json',
            'Authorization': access_key,
        }

        self._workspace = workspace

        self._ws_url = '{}/v2/workspaces/{}/simulators'.format(host, workspace)
        self.simApi = SimulatorAPI(host)
        self.workspace = workspace
    
    def pretty_json(self, o):
        return json.dumps(o, sort_keys=True, indent=3, separators=(',', ': '))

    def create_session(
        self,
        simulator_name: str,
        timeout_seconds: float,
        simulator_context: str,
        capabilities: dict = {},
        description: dict = {}
        ):

        registration_info = {
            'name': simulator_name,
            'timeout': timeout_seconds,
            'capabilities': capabilities,
            'description': description,
            'simulatorContext': simulator_context,
        }

        print("Creating session with", self.pretty_json(registration_info), '\n\n')

        response = self.simApi.session.create(self.workspace, registration_info, custom_headers=self._headers)
        
        if (isinstance(response, SimulatorSessionResponse)):
            return response
        elif (isinstance(response, ProblemDetails)):
            # ToDo: For each error response type, take actions such as retry.
            print('Encountered Error in Creating Session. status: {}, reason: {}'.format(response.status, response.reason))
        else:
            print('Unrecognised error in CreateSession: {}'.format(response))

        return response

    def delete_session(self, session_id: str):
        response = self.simApi.session.delete(self.workspace, session_id, custom_headers=self._headers)
        
        if (isinstance(response, ProblemDetails)):
            print('Error in deleting session. Details: {}'.format(response))
        else:
            print('Successfully deleted session')

        return response

    def list_sessions(self):
        response = self.simApi.session.list(self.workspace, custom_headers=self._headers)
        
        if (isinstance(response, list)):
            return response
        else:
            print('Error in deleting session. Details: {}'.format(response))
            return None


    def fetch_action(self, session_id: str):
        response = self.simApi.session.get_most_recent_action(self.workspace, session_id, custom_headers=self._headers)
        
        if (isinstance(response, Event)):
            return response
        else:
            print('Error in FetchAction. Details: {}'.format(response))
            return None

    def advance(self, session_id: str, sequence_id: int, state):
        json={
            'session_id': session_id,
            'sequence_id': sequence_id,
            'state': state,
            'halted': False
        }
        
        response = self.simApi.session.advance(self.workspace, session_id, json, custom_headers=self._headers)
        
        if (isinstance(response, Event)):
            return response
        else:
            print('Error in Advance session. Details: {}'.format(response))
            return None


# Helper Method to create sim-context string.
def CreateSimContext(action, workspaceName, brainName, brainVersion, conceptName, deploymentMode = "Testing", simulatorClientId = "1234"):
    
    return "{{\"deploymentMode\": \"{}\", \"simulatorClientId\": \"{}\", \"purpose\": {{ \"action\": \"{}\", \"target\": {{ \"workspaceName\": \"{}\", \"brainName\": \"{}\", \"brainVersion\": {}, \"conceptName\": \"{}\" }} }} }}".format(
        deploymentMode,
        simulatorClientId,
        action,
        workspaceName,
        brainName,
        brainVersion,
        conceptName
    )