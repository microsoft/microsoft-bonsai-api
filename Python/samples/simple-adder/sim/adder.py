class Adder:
    def __init__(self, initial_value: float):
        self.value = initial_value

    def add(self, addend: float):
        self.value += addend
