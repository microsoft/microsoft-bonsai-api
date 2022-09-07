import math

# Single Tank, everything in meters and seconds 

class Tank():
    def __init__(self, hSetPoint, vFlowrate, vLiq):
        
        self.vFlowRate = vFlowrate # m3/s
        self.gamma = 1 # % flow rate going to tank
        self.td = 0.1 # time differential per control loop
        self.T = math.floor(60 / self.td) # sec (1 min)
        self.pi = 3.14159 
        self.g = 9.81 # m/s2
        
        self.tankHeight = 5 # m
        self.tankRadius = 10 # m
        self.tankArea = self.pi * (self.tankRadius**2) # area = pi * r**2
        self.vTank = self.tankArea * self.tankHeight # volume of tank (m3)
        self.vLiq = vLiq # volume of liquid in tank (m3)
        self.drainRadius = 0.75 # m
        self.drainArea = self.pi * (self.drainRadius**2) # area = pi * r**2
        self.hLiq = 0 # m 
        self.overflowed = False
        self.emptied = False
        self.vIn = 0 # m3
        self.vDrain = 0 # m3
        self.hSetPoint = hSetPoint # m

    def step(self, flowrate):
        
        self.vFlowRate = flowrate
            
        self.vIn = ((self.vFlowRate * self.gamma) * self.td) + self.vIn  ## m3 = (m3/s * s) + m3
        
        self.vLiq = self.vLiq + self.vIn # add flowrate to volume of liquid in tank  ## m3 = (m3 + m3)
        
        self.hLiq = max(self.vLiq / self.tankArea, 0) # height of Liquid = v / pi * r**2, can't be below 0  ## m = (m3 / pi*m2 )
        
        self.vDrain = self.drainArea * math.sqrt(2 * self.g * self.hLiq) * self.td # V = Cd A (2 g H)1/2 * timeDelta   ## m3 = (m2 * sqrt(m/s2 * m) * s)

        self.vLiq = max(self.vLiq - self.vDrain, 0) # take away the volume of the drain from the volume of the liquid  ## m3 = (m3 - m3)
        
        self.vIn = 0 # reset it so simple tank works, but an above tank can set it from it's drain value if configured
        
        if self.vLiq > self.vTank:
           self.overflowed = True
        elif self.vLiq == 0:
           self.emptied = True


        

    # if tank.overflowed:
    #     print("overflow!!")
    #     break
    # elif tank.emptied:
    #     print("emptied!!")
    #     break

