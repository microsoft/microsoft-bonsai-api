import gym
from stable_baselines3 import PPO
from stabmodel import StabModel

env = StabModel()

models_dir = f"models/ppo2"
model_path = f"{models_dir}/run96"

model = PPO.load(model_path, env=env)

episodes = 10

for ep in range(episodes):
    obs = env.reset()
    done = False
    while not done:
        action, _states = model.predict(obs)
        obs, reward, done, info = env.step(action)
        print("action: ", action)
        print("obs:", obs, "reward:", reward, "done:", done)
