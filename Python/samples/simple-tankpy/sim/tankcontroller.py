from sim.tank import Tank

class TankController():
    def __init__(self, hSetPoint, initialFlow, vLiq,controlFreqMultiplier =1):
        self.blt = Tank(hSetPoint, initialFlow, vLiq)
        self.controlFreqMultiplier = controlFreqMultiplier
        
    def step(self, flowrate):    
        # introduce "time drag" by using old flowrate for 1/2 or more?
        for _ in range(self.controlFreqMultiplier):
            self.blt.step(flowrate)
    
