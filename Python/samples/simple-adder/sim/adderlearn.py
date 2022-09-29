import gym
import os
import time
from stable_baselines3 import PPO
from stabmodel import StabModel

TRIAL= 4

models_dir = f"models/ppo" + str(TRIAL)
log_dir = f"logs/ppo" + str(TRIAL)

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
    
env = StabModel()

model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=log_dir)

TIMESTEPS = 1000000
for i in range(1,10):
    model.learn(total_timesteps=TIMESTEPS, tb_log_name=f"PPO{TRIAL}" , reset_num_timesteps=False)
    model.save(f"{models_dir}/run{i}")
    print(f"Run {i} complete")
