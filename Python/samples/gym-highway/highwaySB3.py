import gym
import highway_env
from stable_baselines3 import DQN

env = gym.make("highway-v0")
print("1 - env created")
# model = DQN('MlpPolicy', env,
#               policy_kwargs=dict(net_arch=[256, 256]),
#               learning_rate=5e-4,
#               buffer_size=15000,
#               learning_starts=200,
#               batch_size=32,
#               gamma=0.8,
#               train_freq=1,
#               gradient_steps=1,
#               target_update_interval=50,
#               verbose=1,
#               tensorboard_log="highway_dqn/")
# print("2 - model created")
# model.learn(int(2e4))
# model.save("highway_dqn/model")
# print("3 - model saved")

# Load and test saved model
model = DQN.load("highway_dqn/model")
reward_sum = 0
while True:
  done = truncated = False
  obs = env.reset()
  print("reward_sum: ", reward_sum)
  reward_sum = 0
  while not (done or truncated):
    action, _states = model.predict(obs, deterministic=True)
    action = int(action)
    obs, reward, done, info = env.step(action)
    print("reward: ", reward)
    reward_sum += reward
    env.render()