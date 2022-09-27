import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import csv
from gekko import GEKKO

# create MPC with GEKKO
m = GEKKO()
m.time = [0,1,2,4,8,12,16,20]

# empirical constants
Kp_h1 = 1.3
tau_h1 = 18.4
Kp_h2 = 1
tau_h2 = 24.4

# manipulated variable
p = m.MV(value=0,lb=1e-5,ub=1)
p.STATUS = 1
p.DCOST = 0.01
p.FSTATUS = 0

# unmeasured state
h1 = m.Var(value=0.0)

# controlled variable
h2 = m.CV(value=0.0)
h2.STATUS = 1
h2.FSTATUS = 1
h2.TAU = 20
h2.TR_INIT = 1

# equations
m.Equation(tau_h1*h1.dt()==-h1 + Kp_h1*p)
m.Equation(tau_h2*h2.dt()==-h2 + Kp_h2*h1)

# options
m.options.IMODE = 6
m.options.CV_TYPE = 2

# simulated system (for measurements)
def tank(levels,t,pump,valve):
    h1 = max(1.0e-10,levels[0])
    h2 = max(1.0e-10,levels[1])
    c1 = 0.08 # inlet valve coefficient
    c2 = 0.04 # tank outlet coefficient
    dhdt1 = c1 * (1.0-valve) * pump - c2 * np.sqrt(h1)
    dhdt2 = c1 * valve * pump + c2 * np.sqrt(h1) - c2 * np.sqrt(h2)
    if h1>=1.0 and dhdt1>0.0:
        dhdt1 = 0
    if h2>=1.0 and dhdt2>0.0:
        dhdt2 = 0
    dhdt = [dhdt1,dhdt2]
    return dhdt

# Initial conditions (levels)
h0 = [0,0]

# Time points to report the solution
tf = 400
t = np.linspace(0,tf,tf+1)

# Set point
sp = np.zeros(tf+1)
sp[5:100] = 0.5
sp[100:200] = 0.8
sp[200:300] = 0.2
sp[300:] = 0.5

# Inputs that can be adjusted
pump = np.zeros(tf+1)

# Disturbance
valve = 0.0

# Record the solution
y = np.zeros((tf+1,2))
y[0,:] = h0

# Create plot
plt.figure(figsize=(10,7))
plt.ion()
plt.show()

# Simulate the tank step test
for i in range(1,tf):
    #########################
    # MPC ###################
    #########################
    # measured height
    h2.MEAS = y[i,1]
    # set point deadband
    h2.SPHI = sp[i]+0.01
    h2.SPLO = sp[i]-0.01
    h2.SP = sp[i]
    # solve MPC
    m.solve(disp=False)
    # retrieve 1st pump new value
    pump[i] = p.NEWVAL

    #########################
    # System ################
    #########################
    # Specify the pump and valve
    inputs = (pump[i],valve)
    # Integrate the model
    h = odeint(tank,h0,[0,1],inputs)
    # Record the result
    y[i+1,:] = h[-1,:]
    # Reset the initial condition
    h0 = h[-1,:]

    # update plot every 5 cycles
    if (i%5==3):
        plt.clf()
        plt.subplot(2,1,1)
        plt.plot(t[0:i],sp[0:i],'k-')    
        plt.plot(t[0:i],y[0:i,0],'b-')
        plt.plot(t[0:i],y[0:i,1],'r--')
        plt.ylabel('Height (m)')
        plt.legend(['Set point','Height 1','Height 2'])
        plt.subplot(2,1,2)
        plt.plot(t[0:i],pump[0:i],'k-')
        plt.ylabel('Pump')    
        plt.xlabel('Time (sec)')
        plt.draw()
        plt.pause(0.01)

# Construct and save data file
data = np.vstack((t,pump))
data = np.hstack((np.transpose(data),y))
np.savetxt('data.txt',data,delimiter=',')