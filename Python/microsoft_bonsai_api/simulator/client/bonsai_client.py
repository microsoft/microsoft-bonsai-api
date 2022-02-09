from msilib.schema import Error
from typing import Dict
from microsoft_bonsai_api.simulator.generated import SimulatorAPI
from .config import BonsaiClientConfig, validate_config

import logging
from azure.core.exceptions import HttpResponseError
import sys

sys.path.insert(0,'C:\dev\microsoft-bonsai-api\Python\microsoft_bonsai_api\simulator\client')
from bonsai_handler import BonsaiStreamHandler
from microsoft_bonsai_api.simulator.generated.models import SimulatorInterface, SimulatorState, SimulatorSessionResponse

# The API object that handles the REST connection to the bonsai platform.
class BonsaiClient(SimulatorAPI):
    
    def __init__(self, config: BonsaiClientConfig, **kwargs):

        validate_config(config)
        
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": config.access_key,
        }

        logging.basicConfig()
        self.logger = logging.getLogger("azure")
        self.logger.propagate = True

        if config.enable_logging:
            self.logger.setLevel(logging.DEBUG)
        else:
            # by default enable logs for Warning and above levels.
            self.logger.setLevel(logging.WARNING)

        infoOutputHandler = BonsaiStreamHandler(sys.stdout)
        infoOutputHandler.setLevel(logging.INFO)
        
        # create a handler for ERROR outputs
        errorOutputHandler = logging.StreamHandler(sys.stderr)
        errorOutputHandler.setLevel(logging.ERROR)
        
        self.logger.root.handlers = [infoOutputHandler,errorOutputHandler]
        
        self.session_id = None
        self.sequence_id = 1

        # Add retry methods. This is used by Default RetryPolicy of azure.core
        # https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/azure/core/pipeline/policies/_retry.py
        kwargs.setdefault(
            "retry_on_methods",
            set(["HEAD", "GET", "PUT", "POST", "DELETE", "OPTIONS", "TRACE"]),
        )

        super(BonsaiClient, self).__init__(
            base_url=config.server,
            headers=self._headers,
            logging_enable=config.enable_logging,
            kwargs=kwargs,
        )


    def create(
        self,
        workspace_name,  # type: str
        body,  # type: "models.SimulatorInterface"
        **kwargs  # type: Any
    ):
        try:
            registered_session: SimulatorSessionResponse = self.session.create(workspace_name, body, **kwargs)
            self.session_id = registered_session.session_id
        except Exception as e:
            
            still_log = True

            if e.args:
                if len(e.args) > 0:
                    if '(BonsaiAuthDeprecated)' in e.args[0]: 
                        self.logger.error('Expired or invalid sim access key. Please try again or go to the Bonsai workspace info page to generate a new one.')
                        quit()

            if still_log:
                self.logger.error(e)
        
    def advance(
        self,
        workspace_name,  # type: str
        state,
        halted,
        **kwargs  # type: Any
    ):
        try:
            sim_state = SimulatorState(sequence_id=self.sequence_id, state=state, halted=halted)
            event = self.session.advance(workspace_name, self.session_id, sim_state, **kwargs)
            self.sequence_id = event.sequence_id

            return event
        except Exception as e:
            self.logger.error(e)

    def delete(
        self,
        workspace_name,  # type: str
        **kwargs  # type: Any
    ):
        try:
            self.session.delete(workspace_name, self.session_id, **kwargs)
        except Exception as e:
            self.logger.error(e)
