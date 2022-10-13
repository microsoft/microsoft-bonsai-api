from functools import total_ordering
import gym
import highway_env

config = {
    "simulation_frequency": 15,
    "show_trajectories": True,
    "manual_control": True,
    "observation": {
        "type": "Kinematics",
        "vehicles_count": 15,
        "features": ["presence", "x", "y", "vx", "vy", "cos_h", "sin_h"],
        "features_range": {
            "x": [-100, 100],
            "y": [-100, 100],
            "vx": [-20, 20],
            "vy": [-20, 20]
        },
        "absolute": False,
        "order": "sorted"
    }
}
env = gym.make('highway-v0')
env.configure(config)

total_reward = 0
env.reset()
done = False
while not done:
    obs, reward, done, info = env.step(env.action_space.sample())
    print("obs: ", obs)
    print("reward: ", reward)
    total_reward += reward
    env.render()
    
print("Total reward:", total_reward)
    # with manual control, these actions are ignored