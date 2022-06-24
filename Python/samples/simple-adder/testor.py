# from supply_chain.inventory_management import InvManagementMasterEnv
from sim.simulator_model import SimulatorModel
# from classic_or.newsvendor import NewsvendorEnv
# sim = InvManagementMasterEnv()
# sim = NewsvendorEnv()
sim = SimulatorModel()
tot_reward = 0
config = {}
sim.reset(config)
action = {"ammountToOrder" : 100}
done = False
while not done:
    asdf = sim.step(action)
    reward = asdf["reward1"]
    done = asdf["halted"]
    tot_reward += reward
    print("reward", "{:,}".format(int(reward)))
print("   tot reward", "{:,}".format(int(tot_reward)))