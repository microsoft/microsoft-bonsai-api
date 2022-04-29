from cmath import log
import functools
from typing import Any, cast, Callable, TypeVar

from azure.core.exceptions import HttpResponseError
from microsoft_bonsai_api.simulator.generated import SimulatorAPI
from microsoft_bonsai_api.simulator.generated.operations import SessionOperations
from microsoft_bonsai_api.simulator.generated.models import EventType
from .config import BonsaiClientConfig, validate_config
import logging

from collections import Counter
from logging import Logger, StreamHandler, LogRecord, Formatter
import sys
import json 


_TCallable = TypeVar("_TCallable", bound=Callable[..., Any])


#
# A quick decorator to add logging around a session operation call.
# We log and then re-raise all exceptions, to ensure that there is no change
# in the externally visible behavior of the method.
#
def wrap_session_operation(method: _TCallable) -> _TCallable:
    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        #print(method.__name__)

        method_name = method.__name__

        self._logger.info("Calling session.{}".format(method_name),extra={'sessionId':self.session_id})
        try:
            return method(self, *args, **kwargs)
        except HttpResponseError as ex:

            contents = ''
            
            if hasattr(ex.response, 'contents'):
                contents = ex.response.contents

            self._logger.error(
                "Error when calling Session.{}: ({}) {}".format(
                method.__name__,
                ex.response.status_code,
                contents),
                exc_info=True,
                extra={'sessionId':self.session_id}
            )
            raise

    return cast(_TCallable, wrapped)

class SessionOperationsWrapper(SessionOperations):
    """
    This class wraps logging around the calls to SessionOperations
    """

    def __init__(self, real_ops: SessionOperations, logger: logging.Logger):
        self._real_ops = real_ops
        self._logger = logger
        self.session_id = ""

        #
        # This class inherits from SessionOperations only so that
        # it can replace the self.session property in the BonsaiClient.
        # We intentionally do not initialize the base class!
        #

    ###################################################################
    #
    # We add one method here for each method in SessionOperations.
    # Unless we want to add anything special, we can just add a
    # wrap_session_operation decorator to the call, and then we will
    # log any exceptions.
    #
    ###################################################################

    @wrap_session_operation
    def list(self, *args, **kwargs):
        return self._real_ops.list(*args, **kwargs)

    @wrap_session_operation
    def create(self, *args, **kwargs):
        session = self._real_ops.create(*args, **kwargs)

        self.session_id = session.session_id
        self._logger.info("Created session {}".format(self.session_id), extra={'sessionId':self.session_id})

        return session

    @wrap_session_operation
    def get(self, *args, **kwargs):
        return self._real_ops.get(*args, **kwargs)

    @wrap_session_operation
    def delete(self, *args, **kwargs):
        return self._real_ops.delete(*args, **kwargs)

    @wrap_session_operation
    def get_most_recent_action(self, *args, **kwargs):
        return self._real_ops.get_most_recent_action(*args, **kwargs)

    @wrap_session_operation
    def advance(self, *args, **kwargs):
        event = self._real_ops.advance(*args, **kwargs)

        if event.type == EventType.unregister:
            self._logger.warn(
                "Simulator {} received Unregister message from platform because '{}' with details '{}'".format(
                self.session_id,
                event.unregister.reason,
                event.unregister.details),
                extra={'sessionId':self.session_id}
            )

        return event
#
# JSON format -> https://stackoverflow.com/questions/50144628/python-logging-into-file-as-a-dictionary-or-json 
#

class BonsaiLogHandler(StreamHandler):
    """
    Specialized handler for the logs that pertain to the Bonsai SDK
    """
    def __init__(self, format=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def emit(self, record: LogRecord) -> None:
        
        #ignore anything not directly from Bonsai 
        if record.levelno != 10 and 'azure.' in record.name:
            return

        json_data = {}
        for attr in filter(lambda attr: not attr.endswith("__"), dir(record)):
            json_data[attr] = record.__getattribute__(attr)
        del json_data["getMessage"]

        print(json.dumps(json_data))

# The API object that handles the REST connection to the bonsai platform.
class BonsaiClient(SimulatorAPI):
    
    def __init__(self, config: BonsaiClientConfig, **kwargs):
        validate_config(config)
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": config.access_key,
        }

        logging.basicConfig()
        logger = logging.getLogger("azure")
        
        logger.root.handlers.clear()

        bonsai_handler = BonsaiLogHandler()
        logger.addHandler(bonsai_handler)

        if config.enable_logging:
            logger.setLevel(logging.DEBUG)
        else:
            # by default enable logs for INFO and above levels.
            logger.setLevel(logging.INFO)

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
            kwargs=kwargs
        )

        #
        # At this point, self.session is set to an instance of SessionOperations, which is an auto-generated class.
        # We want to wrap calls to self.session, so we...
        #

        # ... move the underlying SessionOperations instance out of the way (maybe we'll need it?)...
        self._session = self.session


        # ... and decorate it with logging operations!
        self.session = SessionOperationsWrapper(self._session, logger)

        # Now, when the simulator calls client.session.<whatever>(), that call will
        # pass through our wrapper on its way to the "real" SessionOperations method.