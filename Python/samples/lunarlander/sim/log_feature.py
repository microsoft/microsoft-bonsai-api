from functools import partial
import json
import random
import math
import time
import os
import pathlib
import datetime
from typing import Dict, Any, Union
#TOREMOVE:import highway_env
import gym
import numpy as np
import copy

LOG_PATH = "logs"


def ensure_log_dir(log_full_path: str):
    """Create a log directory if needed

    Parameters
    ----------
    log_full_path : str
        path of log directory
    """
    print(f"Log filename: {log_full_path}")
    logs_directory = pathlib.Path(log_full_path).parent.absolute()
    print(f"Log directory: {logs_directory}")
    if not pathlib.Path(logs_directory).exists():
        print(
            "Directory does not exist at {0}, creating now...".format(
                str(logs_directory)
            )
        )
        logs_directory.mkdir(parents=True, exist_ok=True)


class SimLogger:
    def __init__(
        self,
        log_data: Union[bool, str] = False,
        debug: bool = False,
    ):
        """Logging functionality for Python sims.
        """

        self.debug = debug

        # Keep track of episode & iteration (for reference, even when the sim is wrapped).
        self.episode = 0
        self.iteration = 0

        # Logging features
        self.log_data = log_data
        self.log_name = "pythonSim"
        if type(self.log_data) is str:
            self.log_data = True
            self.log_name = log_data
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        log_file_name = current_time + "_" + self.log_name + "_log.csv"

        self.log_full_path = os.path.join(LOG_PATH, log_file_name)
        ensure_log_dir(self.log_full_path)


    def new_episode(self):
        self.episode += 1
        self.iteration = 0


    def log_iterations(self, state, action, config):
        """Log iterations during training to a CSV.

        Parameters
        ----------
        state : Dict
        action : Dict
        episode : int, optional
        iteration : int, optional
        """

        import pandas as pd

        self.iteration += 1

        def add_prefixes(d, prefix: str):
            return {f"{prefix}_{k}": v for k, v in d.items()}
        
        # Custom way to turn lists into strings for logging
        log_state = state.copy()
        
        for key, value in log_state.items():
            if type(value) == list:
                log_state[key] = str(log_state[key])

        log_state = add_prefixes(log_state, "state")
        action = add_prefixes(action, "action")
        config = add_prefixes(config, "config")
        data = {**log_state, **action, **config}
        data["episode"] = self.episode
        data["iteration"] = self.iteration
        log_df = pd.DataFrame(data, index=[0])

        if os.path.exists(self.log_full_path):
            log_df.to_csv(
                path_or_buf=self.log_full_path, mode="a", header=False, index=False
            )
        else:
            log_df.to_csv(
                path_or_buf=self.log_full_path, mode="w", header=True, index=False
            )

