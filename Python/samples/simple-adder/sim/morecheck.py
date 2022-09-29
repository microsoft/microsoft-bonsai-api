from stabmodel import StabModel

env = StabModel()
episodes = 1

for episode in range(1, episodes+1):
    state = env.reset()
    done = False

    while not done:
        action = env.action_space.sample()
        n_state, reward, done, info = env.step(action.round(1))
