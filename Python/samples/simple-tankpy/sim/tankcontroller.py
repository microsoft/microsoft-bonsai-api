from sim.tank import Tank

class TankController():
    def __init__(self, hSetPoint, initialFlow):
        self.blt = Tank(1, initialFlow)
        self.blt.hSetPoint = hSetPoint
        
    def step(self, flowrate):    
        self.blt.step(flowrate)
    
