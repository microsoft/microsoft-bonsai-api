from microsoft_bonsai_api.simulator.generated.aio import SimulatorAPI
from .config import BonsaiClientConfig, validate_config
import logging

# The API object that handles the REST connection to the bonsai platform.
class BonsaiClientAsync(SimulatorAPI):
    def __init__(self, config: BonsaiClientConfig, **kwargs):
        validate_config(config)
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": config.access_key,
        }

        logging.basicConfig()
        logger = logging.getLogger("azure")

        if config.enable_logging:
            logger.setLevel(logging.DEBUG)
        else:
            # by default enable logs for Warning and above levels.
            logger.setLevel(logging.WARNING)

        # Add retry methods. This is used by Default RetryPolicy of azure.core
        # https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/azure/core/pipeline/policies/_retry.py
        kwargs.setdefault(
            "retry_on_methods",
            set(["HEAD", "GET", "PUT", "POST", "DELETE", "OPTIONS", "TRACE"]),
        )

        super(BonsaiClientAsync, self).__init__(
            base_url=config.server,
            headers=self._headers,
            logging_enable=config.enable_logging,
            kwargs=kwargs,
        )
