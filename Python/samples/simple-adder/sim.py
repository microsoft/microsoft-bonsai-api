class Sim:
    def __init__(self):
        self.reset({ 'config_val': 0})

    def reset(self, config):
        self.config = config;
        self.action = { 'action_val': 0 }
        self.total = 0

    def step(self, action):
        self.action = action

    @property
    def state(self):
        self.total += self.action['action_val']

        state = { 'total': self.total}
        # TODO: Is sorting keys necessary? Why does order matter? Does it fully solve the problem of hash tables that could still reorder properties?
        for config_key, config_value in sorted(self.config.items()):
            state['state_' + config_key] = config_value
        for action_key, action_value in sorted(self.action.items()):
            state['state_' + action_key] = action_value
        return state

    @property
    def halted(self):
        return False