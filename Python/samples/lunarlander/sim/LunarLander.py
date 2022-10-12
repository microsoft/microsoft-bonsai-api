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

from sim.log_feature import SimLogger


class LunarLander:
    def __init__(
        self,
        render: bool = False,
        log_data: Union[bool, str] = False,
        env_name: str = "LunarLanderContinuous-v2",
        obs_type: str = "Kinematics", # TODO: Review if Kinematics is needed (config-related)
        debug: bool = True,
    ):
        """Lunar Lander simulation using the gym environment. See API docs for more information:
            https://www.gymlibrary.ml/environments/box2d/lunar_lander/

        Parameters
        ----------
        render : bool, optional
            render every control timestep of the environment, by default False
        log_data : bool/str, optional
            whether to MDP data to CSV, by default False.
            If str is provided, CSV name generation will use tag for unique identification.
        env_name : str, optional
            the name of the simulator environment to create, by default "highway-v0"
        obs_type: str, optional
            the type of observations received from simulator.
        """

        self.simulator = gym.make(env_name)
        self.state = self.simulator.reset().tolist()
        self.state_prev = np.copy(self.state)
        self.reward = 0
        self.terminal = False
        self.env_name = env_name
        self.obs_type = obs_type
        self.render = render
        self.debug = debug

        # Logging features
        self.log_data = log_data
        self.sim_logger = SimLogger(log_data=self.log_data)

        # Initialize MT configuration parameters.
        self.initialize_MT_vars()


    def get_state(self) -> Dict[str, Any]:
        """Extract state from MDP.

        Returns
        -------
        Dict[str, Any]
            Get states from current simulator environment
        """
        state = {
            "x_position": self.state[0],
            "y_position": self.state[1],
            "x_velocity": self.state[2],
            "y_velocity": self.state[3],
            "angle": self.state[4],
            "rotation": self.state[5],
            "left_leg": self.state[6],
            "right_leg": self.state[7],
            # Converting to float due to parsing errors detecting during brain training
            "ship_crashed": bool(self.ship_crashed),
            "ship_landed": bool(self.ship_landed),
            # Config Params
            "randomized_strength": float(self.randomized_strength),
            "randomized_steps": int(self.randomized_steps),
            "delta_action": bool(self.delta_action),
            # Aux vars -- Useful for delta actions
            "prev_engine1": float(self.action_prev[0]),
            "prev_engine2": float(self.action_prev[1]),
            # Gym reward/terminal
            "gym_reward": float(self.reward),
            "gym_terminal": bool(self.terminal),
            # UNUSED AT THE MOMENT
            "prev_x_position": float(self.state_prev[0]),
            "prev_y_position": float(self.state_prev[1]),
            "prev_x_velocity": float(self.state_prev[2]),
            "prev_y_velocity": float(self.state_prev[3]),
            "concept": float(self.concept),
        }

        return state

    @property
    def ship_crashed(self):
        return self.reward < -75

    @property
    def ship_landed(self):
        return self.reward > 75


    def episode_start(self, config: Union[Dict[str, Any], None] = None):
        """Initialize a new episode of the simulator with configuration parameters.

        Parameters
        ----------
        config : Dict[str, Any] or None
            parameters for initializing the simulator.
            --> Note, valid MT parameters are listed in "self.bonsai_MT_config".
        """
        # Update episode number, and restart iteration count.
        if self.log_data:
            self.sim_logger.new_episode()

        # Reset concept
        self.concept = 0
        self.hold_selected_concept = 1 # <1 .. 50>

        if config:
            # reset the environment if the env_name is in the SimConfig
            if "env_name" in config.keys():
                self.simulator = gym.make(config["env_name"])
                self.state = self.simulator.reset().tolist()
                self.state_prev = np.copy(self.state)
                self.reward = 0
                self.terminal = False
                self.env_name = config["env_name"]

            # Store MT configuration, whenever provided.
            MT_config = dict([(k,v) for k,v in config.items() if k in self.bonsai_MT_config])
            if self.debug:
                print("Configuration for Episode Start:", MT_config)
            for param, value in MT_config.items():
                setattr(self, param, value)
        else:
            if self.debug:
                print("No config was provided to the simulation during Episode Start. Running with default params.")
            config = {}
        self.config = config
        
        # Restart sim, and restore status variables
        self.state = self.simulator.reset().tolist()
        self.state_prev = np.copy(self.state)
        self.reward = 0
        self.terminal = False
        if self.render:
            self.simulator.render()
        
        # APPLY RANDOM ACTIONS TO INCREASE THE STARTING STOCHASTICITY
        #  By default, there is no randomization.
        self.apply_random_actions()
        
        

    def episode_step(self, action: Dict[str, Any]):
        """Step through the environment. See allowable actions here: https://highway-env.readthedocs.io/en/latest/actions/index.html

        Parameters
        ----------
        action : Dict[str, Any]
            Control/action to iterate in the environment
        """

        # Log iterations at every episode step.
        if self.log_data:
            self.sim_logger.log_iterations(state=self.get_state(),
                                           action=action,
                                           config=self.config)

        # Hold concept with same action if selected, otherwise, run as normal
        if self.hold_concept_with_same_action:
            self._STEP(action)
            while self.i_hold_selected_concept != 0:
                self._STEP(action)
            return
        
        self._STEP(action)
        
        

    def _STEP(self, action: Dict[str, Any]):
        """Step through the environment. See allowable actions here: https://highway-env.readthedocs.io/en/latest/actions/index.html

        Parameters
        ----------
        action : Dict[str, Any]
            Control/action to iterate in the environment
        """
        
        # Reset concept to 0 when we reach the 'keep_concept' limit, otherwise transfer the action to attribute
        if "concept" not in action.keys():
            pass
            #debug
            #print("No concept action provided. Value is not updated.")
        else:
            self.concept = action["concept"]
            self.i_hold_selected_concept += 1
            if self.i_hold_selected_concept >= self.hold_selected_concept:
                #debug
                #print(f"Resetting concept after {self.i_hold_selected_concept} iterations.")
                self.concept = 0
                self.i_hold_selected_concept = 0
        
        # If engine2 is not provided, values for 'engine_left' & 'engine_right' must be provided.
        # --> Lunar Lander Gym sim requires engine2 to have been merged already.
        if "engine2" not in action.keys():
            assert "engine_left" in action.keys() and "engine_right" in action.keys(), \
                "Failed to apply action, you must provide 'engine_left' & 'engine_right' when 'engine2' is missing."

            action_left = np.clip(action["engine_left"], 0.0, 1.0)
            action_right = np.clip(action["engine_right"], 0.0, 1.0)
            engine2 = action_right - action_left
            # Add aggregated value to action dictionary coming from brain so it can be read bellow.
            action["engine2"] = engine2
        
        # Gather engine actions
        engine1 = np.clip(action["engine1"], -1.0, 1.0)
        engine2 = np.clip(action["engine2"], -1.0, 1.0)

        # Perform any necessary action transformations
        if self.delta_action > 0:
            engine1 += self.action_prev[0]
            engine2 += self.action_prev[1]
        elif self.rolling_action_weight > 0:
            engine1 = self.rolling_action_weight*self.action_prev[0] + (1-self.rolling_action_weight)*engine1
            engine2 = self.rolling_action_weight*self.action_prev[1] + (1-self.rolling_action_weight)*engine2
        else:
            pass

        engine1 = np.clip(engine1, -1.0, 1.0)
        engine2 = np.clip(engine2, -1.0, 1.0)
        aux_action = np.asarray([engine1, engine2])
        obs, reward, done, _ = self.simulator.step(aux_action)
        self.terminal = done
        self.action_prev = np.copy(aux_action)
        self.state_prev = np.copy(self.state)
        self.state = obs.tolist()
        self.reward = reward

        if self.render:
            self.simulator.render()

    def halted(self) -> bool:
        """Terminate the episode if and only if the simulator cannot be continued. This washes away the entire episode from training.
        """

        return False


    def initialize_MT_vars(self):
        """
            Initialize the Machine Teaching (MT) params that allow configuring the simulation framework.
        """

        # Randomize episode start by applying random actions.
        #  Applied actions have a max value of +-self.randomized_strength and are applied for over self.randomized_steps iterations.
        self.randomized_strength = 1
        self.randomized_steps = 0
        # When enabled, actions received from the brain are assumed to be the delta from the previous iteration.
        # -> 0 == No delta actions applied; 1 == action provided is delta
        self.delta_action = 0
        self.action_prev = [0, 0]
        # When enabled, the actions received are rolled over across iterations
        #  -> % of previous action to mantain: 0 == No rolling window applied; 0.9 == 90% prev + 10% new.
        self.rolling_action_weight = 0
        # Add ability to mask the use of other concepts every X timesteps.
        # -> Used to automatically capture last concept selected by a modular decomposed control.
        #   -> self.concept is reset to "0" every self.hold_selected_concept iterations.
        #   -> Useful to prevent the control from changing policies too often by forcing the control agent to only change when concept is "0".
        # -> If integrating with Bonsai, the decomposition must look as follows:
        #   -> 0 = None, 1 = Move right, 2 = Move left, 3 = Move down, 4 = Move up, 5 = ApproachLand
        self.concept = 0
        self.hold_selected_concept = 1 # <1 .. 50>
        self.i_hold_selected_concept = 0 # iterates over the number of selected 'hold_selected_concept'
        # -> Variation to indicate the brain that the holding should be done at the simulation level.
        #   -> 1 == Sim applies the same action for self.hold_selected_concept steps.
        self.hold_concept_with_same_action = 0
        
        # APPEND ALL MT CONFIG VARIABLES IN A LIST TO BE CAPTURED IF A CONFIG IS PROVIDED AT EPISODE START.
        self.bonsai_MT_config = ["randomized_strength",
                                 "randomized_steps",
                                 "delta_action",
                                 "rolling_action_weight",
                                 "hold_selected_concept",
                                 "hold_concept_with_same_action"]

        # Reset auxiliary variables if no config is provided.
        self.reset_MT_vars()

    
    def reset_MT_vars(self):
        """
            Reset the variables that change when applying randomization for episode start.
        """
        # Reset initialization values for applied action to (0,0) no matter the randomization applied.
        self.action_prev = [0, 0]
        
        # Reset concept, and its corresponding auxiliar iteration counter.
        self.concept = 0
        self.i_hold_selected_concept = 0 # iterates over the number of selected 'hold_selected_concept'


    def apply_random_actions(self):
        """
            Apply random actions to increase the starting stochasticity
             Note, by default, there is no randomization.
        """
        # Iterate applying random actions for the iterations desired.
        #  By default, randomized_strength is 1.
        for _ in range(self.randomized_steps):
            rand_act_eng1 = (np.random.random()-0.5)*2*self.randomized_strength
            rand_act_eng2 = (np.random.random()-0.5)*2*self.randomized_strength

            rand_action = dict([("engine1", rand_act_eng1), ("engine2", rand_act_eng2), ("concept", self.concept)])
            self.episode_step(rand_action)

            if self.render:
                self.simulator.render()
        
        # Reset MT auxiliary vars to zero after stepping for random actions.
        self.reset_MT_vars()


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Bonsai and Simulator Integration...")
    parser.add_argument(
        "--render", action="store_true", default=False, help="Render training episodes",
    )
    parser.add_argument(
        "--log-iterations",
        action="store_true",
        default=False,
        help="Log iterations during training",
    )
    args, _ = parser.parse_known_args()

    # Initialize simulation.
    sim = LunarLander(
            render=args.render,
            log_data=args.log_iterations
    )

