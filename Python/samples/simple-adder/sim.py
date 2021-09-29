class Sim:
    def __init__(self):
        self.reset({ 'initial_value': 0})

    def reset(self, config):
        self.value = config['initial_value']

    def step(self, action):
        self.value += action['addend']

    @property
    def state(self):
        state = { 'value': self.value }
        return state

    @property
    def halted(self):
        return False