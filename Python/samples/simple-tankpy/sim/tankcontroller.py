from sim.tank import Tank

class TankController():
    def __init__(self, hSetPoint, initialFlow, vLiq,controlFreqMultiplier=1):
        self.blt = Tank(hSetPoint, initialFlow, vLiq)
        self.controlFreqMultiplier = controlFreqMultiplier
        self.iterCount = 0
        self.SPChangeDone = False
        
    def step(self, flowrate):    
        # introduce "time drag" by using old flowrate for 1/2 or more?
        for _ in range(self.controlFreqMultiplier):
            self.blt.step(flowrate)
        
        self.iterCount += 1
        
        # switch SP 1/2 way through
        if self.iterCount > 150 and (not self.SPChangeDone):
            self.blt.hSetPoint = 5 - self.blt.hSetPoint
            self.SPChangeDone = True
    
