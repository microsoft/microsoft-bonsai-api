import numpy as np
import matplotlib.pyplot as plt

class House():
    def __init__(self, 
                K: float=0.5, 
                C: float=0.3, 
                Qhvac: float=9, 
                hvacON: float=0, 
                occupancy: float=1, 
                Tin_initial: float=30, 
                Tout_median: float= 20,
                Tout_amplitude: float=5,
                Tset_start: int = 25,
                Tset_stop: int = 20,
                Tset_transition: float = 100,
                timestep: float=5, 
                horizon: float=288,):

        self.K = K # thermal conductivity
        self.C = C # thermal capacity
        self.Tin = Tin_initial # Inside Temperature 
        self.Qhvac = Qhvac # Cooling capacity
        self.hvacON = hvacON # control action = 0 (OFF) or 1 (ON)

        self.occupancy = occupancy # 0 (no one in the room) or 1 (somebody in the room)
        self.Phvac = Qhvac # Electric power capacity 

        self.timestep = timestep # minutes
        self.Tout_median = Tout_median # sinewave signal bias for outside temperature flucation
        self.Tout_amplitude = Tout_amplitude # sinewave amplitude for outside temperature flucation
        self.Tset_start = Tset_start # start temperature set point
        self.Tset_stop = Tset_stop # step temperature set point
        self.Tset_transition = Tset_transition # time (in hours) to switch from day to night Tset
        self.horizon = horizon # length of episode in timestep (default=5min) intervals
        self.build_schedule()

        plt.close()
        self.fig, self.ax = plt.subplots(1, 1)

    def build_schedule(self):
        """ define the Tset_schedule, Tout_schedule, the length of schedule, timestep
        """

        # Step function for Tset schedule
        self.Tset_schedule = np.full(self.horizon + 1, self.Tset_start)
        self.Tset_schedule[self.Tset_transition:] = self.Tset_stop
        
        # Sine wave for Tout schedule
        self.Tout_schedule = self.Tout_amplitude * np.sin(np.linspace(-np.pi, np.pi, self.horizon + 1)) + self.Tout_median
        self.occupancy_schedule = np.full(self.horizon, 1)

        self.Tset = self.Tset_schedule[0] # Initial set Temperature
        self.Tout = self.Tout_schedule[0] # Initial outside temperature

        # For plotting only
        self.time_to_plot = [0]
        self.Tin_to_plot = [self.Tin]
        self.Tset_to_plot = [self.Tset]
        self.Tout_to_plot = [self.Tout]

        self.__iter__()

    def update_Tout(self, Tout_new):
        self.Tout = Tout_new # Update to new outside temperature
        
    def update_Tset(self, Tset_new):
        self.Tset = Tset_new # Update to new setpoint temperature

    def update_hvacON(self, hvacONnew):
        self.hvacON = hvacONnew # update to new hvacON

    def update_occupancy(self, occupancy_new):
        self.occupancy = occupancy_new # update to new occupancy
      
    def update_Tin(self):
        """Update inside temperation.
        Describes the inside temperature evolution as a function of all other variables. 
        """
        # Note timestep is converted to seconds here, in order to keep units consistent in SI for update.
        self.Tin = self.Tin - (self.timestep/60) / self.C * (self.K * (self.Tin - self.Tout) + self.Qhvac * self.hvacON)
        
        self.__next__()
        self.Tset_to_plot.append(self.Tset)
        self.Tin_to_plot.append(self.Tin)
        self.Tout_to_plot.append(self.Tout)
        self.time_to_plot.append(self.iteration * 5)

    def get_Power(self):
        COP = 3
        Power = self.Phvac * self.hvacON * COP 
        return Power

    def show(self):

        self.ax.clear()
        self.ax.plot(self.time_to_plot, self.Tin_to_plot, label='Tin')
        self.ax.plot(self.time_to_plot, self.Tset_to_plot, label='Tset')
        self.ax.plot(self.time_to_plot, self.Tout_to_plot, label='Tout')
        self.ax.set_xlabel('Time [min]')
        self.ax.set_ylabel(r'Temperature [$^\circ$C]')
        plt.legend()
        plt.pause(np.finfo(np.float32).eps)
        
 # print the object nicely   
    def __str__(self):
        string_to_print = []
        for key in self.__dict__:
            string_to_print.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(string_to_print)
    
    def __repr__(self):
        return self.__str__() 

    def __iter__(self):
        self.iteration = 0
        return self
    
    def __next__(self):
        if self.iteration <= self.horizon - 5:
            self.iteration += 1
            self.update_Tset(self.Tset_schedule[self.iteration])
            self.update_Tout(self.Tout_schedule[self.iteration])
            self.update_occupancy(self.occupancy_schedule[self.iteration])
        else:
            StopIteration


if __name__ == '__main__':
    import random
    house = House()
    
    for episode in range(1):
        house.build_schedule()
        for i in range(288):
            house.update_hvacON(random.randint(0, 1))
            house.update_Tin()
            # print('Tin : {}'.format(house.Tin))
            house.show()

