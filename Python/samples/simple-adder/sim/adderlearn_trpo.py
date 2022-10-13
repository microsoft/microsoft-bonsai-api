import gym
import os
import time
from stable_baselines3 import TRPO
from stabmodel import StabModel

TRIAL= 1
ALGO = "TRPO"

models_dir = f"models/{ALGO}" + str(TRIAL)
log_dir = f"logs/{ALGO}" + str(TRIAL)

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
    
env = StabModel()

model = TRPO('MlpPolicy', env, verbose=1, tensorboard_log=log_dir)

TIMESTEPS = 100000
for i in range(1,100):
    model.learn(total_timesteps=TIMESTEPS, tb_log_name=f"{ALGO}{TRIAL}" , reset_num_timesteps=False)
    model.save(f"{models_dir}/run{i}")
    print(f"Run {i} complete")
