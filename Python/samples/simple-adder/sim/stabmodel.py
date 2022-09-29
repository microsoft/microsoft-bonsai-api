from adder import Adder
import gym
from gym import spaces
import numpy as np
from typing import NamedTuple, Dict, Any

class StabModel(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(StabModel, self).__init__()
        self.action_space = spaces.Box(low=-10.0, high=10.0, shape=(1,), dtype=np.float32)
        self.observation_space = spaces.Box(low=0, high=100,  shape=(1,), dtype=np.float32)

    def reset(self):
        self.done = False
        self.start_value = np.random.random_sample() * 100
        self.adder = Adder(self.start_value)
        self.reward = 0
        self.stepCount = 0
        print("reset")
        self.observation = [self.adder.value]
        self.observation = np.array(self.observation, dtype=np.float32)
        return self.observation  

    def step(self, action):
        self.stepCount += 1
        self.adder.add(action[0])
        self.reward = 100 - abs(50 - self.adder.value)
        self.observation = [self.adder.value]
        self.observation = np.array(self.observation, dtype=np.float32)
        if self.stepCount > 10:
            self.done = True
            self.reward = -500
        if self.adder.value >= 100 or self.adder.value <= 0:
            self.done = True
            self.reward = -300
        if self.adder.value >= 49.9 and self.adder.value <= 50.1:
            self.reward = 100000
            print("reward at: " + self.stepCount)
            self.done = True
        self.reward = self.reward - (self.stepCount * 5)
        return self.observation, self.reward, self.done, {}
