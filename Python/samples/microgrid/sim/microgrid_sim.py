import csv
from pymgrid import MicrogridGenerator

class MicrogridSim:
    """
    Model to simulate a microgrid.
    """
    def __init__(self):
        # we will use the 4th microgrid architecture in pymgrid25 benchmark set
        # with PV, battery, load and grid
        generator = MicrogridGenerator.MicrogridGenerator(nb_microgrid=25)
        pymgrid25 = generator.load('pymgrid25')
        self.mg = pymgrid25.microgrids[4]
        self.mg._grid_price_import[self.mg._grid_price_import == 0.11] = 0.2 # increase the high grid price value
        self.prev_state = {}
        self.state = {}
        self.control_dict = {}
        self.cost_loss_load = 10 # penalty coefficient for not meeting the load
        self.cost_overgeneration = 1 # penalty coefficient for over-generating
        self.cost_battery = 0.02 # default cost of utilizing the battery
        self.cost_co2 = 0.1 # coefficient penalizing for CO2 usage
        self.episode_length = 24*2
        self.load_ts = None
        self.pv_ts = None
        self.starting_time_step = None
    
    def get_state(self):
        """
        Returns a dictionary with the state variables of the sim along with the microgrid's cost.
        """
        self.prev_state = self.state
        state = self.mg.get_updated_values().copy()
        try:
            co2_emission = self.mg.get_co2()
            state["co2_emission"] = co2_emission
        except IndexError:
            state["co2_emission"] = 0
        state["pv_load_diff"] = state["pv"] - state["load"]
        costs = self.get_calculated_cost()
        state["cost"] = costs[0]
        state["normalized_cost"] = costs[1]
        # initialize the previous states/actions to calculate costs (initializes with 0 if first iteration). 
        state["prev_load"] = self.prev_state.get("load", 0)
        state["prev_pv"] = self.prev_state.get("pv", 0)
        state["prev_grid_price_import"] = self.prev_state.get("grid_price_import", 0)
        state["prev_grid_co2"] = self.prev_state.get("grid_co2", 0)
        state["prev_action_grid_import"] = self.control_dict.get("grid_import", 0)
        state["cost_co2"] = self.cost_co2
        if self.load_ts is not None:
            state["sum_load"] = self.load_ts.sum()
        else:
            state["sum_load"] = 1
        self.state = state
        return state
    
    def episode_start(self, config):
        """
        Resets the sim state and re-initializes the sim with the config parameters.
        """
        # first we reset all the parameters
        self.prev_state = {}
        self.state = {}
        self.control_dict = {}
        self.starting_time_step = config["starting_time_step"]

        if "cost_loss_load" in config:
            self.cost_loss_load = config["cost_loss_load"]
        if "cost_overgeneration" in config:
            self.cost_overgeneration = config["cost_overgeneration"]
        if "cost_battery" in config:
            self.cost_battery = config["cost_battery"]
        if "cost_co2" in config:
            self.cost_co2 = config["cost_co2"]
        if "episode_length" in config:
            self.episode_length = config["episode_length"]        
        
        # reset the sim
        self.mg.reset()
        # The sim originally resets all the data to the 0th index, we would like to reset the sim to any time index
        # TODO: Derive a new class and override the reset instead of accessing the private variables of the object
        self.mg._tracking_timestep = config["starting_time_step"]
        self.mg.update_variables()

        self.mg._df_record_state["load"] = [self.mg.load]
        self.mg._df_record_state["hour"] = [self.mg._tracking_timestep % 24]
        self.mg._df_record_state["pv"] = [self.mg.pv]
        self.mg._df_record_state["grid_status"] = [self.mg.grid.status]
        self.mg._df_record_state["grid_co2"] = [self.mg.grid.co2]
        self.mg._df_record_state["grid_price_import"] = [self.mg.grid.price_import]
        self.mg._df_record_state["grid_price_export"] = [self.mg.grid.price_export]

        self.load_ts = self.mg._load_ts.iloc[self.mg._tracking_timestep:self.mg._tracking_timestep + self.episode_length].values.flatten()
        self.pv_ts = self.mg._pv_ts.iloc[self.mg._tracking_timestep:self.mg._tracking_timestep + self.episode_length].values.flatten()

    def episode_step(self, action):
        control_dict = {"battery_charge": 0,
            "battery_discharge": 0,
            "grid_import": 0,
            "grid_export":0,
            "pv_consummed": 0,
            }
        
        # if battery_power > 0 it means charge the battery, else it means discharge the battery
        if action["battery_power"] > 0:
            control_dict["battery_charge"] = abs(action["battery_power"])
        else:
            control_dict["battery_discharge"] = abs(action["battery_power"])
        
        if "pv_to_consume" in action:
            control_dict["pv_consummed"] = action["pv_to_consume"]
        else:
            control_dict = self.get_pv_to_consume_power(control_dict)

        # if grid_power > 0 it means import from the grid, else it means export to the grid
        if "grid_power" in action:
            if action["grid_power"] > 0:
                control_dict["grid_import"] = abs(action["grid_power"])
            else:
                control_dict["grid_export"] = abs(action["grid_power"])
        else:
            control_dict = self.get_grid_power(control_dict)
        
        _ = self.mg.run(control_dict)
        self.control_dict = control_dict

    def get_grid_power(self, control_dict):
        """
        Calculates how much power to import/export from/to the grid to meet the load.
        """
        state = self.mg.get_updated_values().copy()
        load = state["load"]
        pv = state["pv"]
        capa_to_charge = state["capa_to_charge"]
        capa_to_discharge = state["capa_to_discharge"]
        grid_status = state["grid_status"]
        if grid_status == 0:
            # if there is a blackout we can't import from / export to grid
            control_dict["grid_import"] = 0
            control_dict["grid_export"] = 0
            return control_dict
        
        actual_pv_to_consume = min(pv, control_dict["pv_consummed"])
        actual_battery_charge = min(capa_to_charge, control_dict["battery_charge"])
        actual_battery_discharge = min(capa_to_discharge, control_dict["battery_discharge"]) 

        grid_power = load - (-actual_battery_charge + actual_battery_discharge + actual_pv_to_consume)

        if grid_power > 0:
            control_dict["grid_import"] = grid_power
            control_dict["grid_export"] = 0
        else:
            control_dict["grid_import"] = 0
            control_dict["grid_export"] = -grid_power
        return control_dict
    
    def get_pv_to_consume_power(self, control_dict):
        """
        Calculates how much power we should consume from the grid to meet the load
        """
        state = self.mg.get_updated_values().copy()
        load = state["load"]
        pv = state["pv"]
        capa_to_charge = state["capa_to_charge"]
        capa_to_discharge = state["capa_to_discharge"]
        grid_status = state["grid_status"]

        actual_battery_charge = min(capa_to_charge, control_dict["battery_charge"])
        actual_battery_discharge = min(capa_to_discharge, control_dict["battery_discharge"]) 

        total_load = load + actual_battery_charge - actual_battery_discharge
        # if there is any power deficiency, we cover as much of it as we can from the PV
        # TODO: This calculation doesn't account for the possibility to sell to the grid
        if total_load <= 0:
            control_dict["pv_consummed"] = 0
        else:
            control_dict["pv_consummed"] = min(total_load, pv)
        return control_dict
    
    def get_calculated_cost(self):
        """
        Calculates the cost of running the grid and normalizes it. Returns both the original cost and the normalized cost.
        """
        cost_loss_load = self.cost_loss_load
        cost_overgeneration = self.cost_overgeneration
        cost_battery = self.cost_battery
        cost_co2 = self.cost_co2

        # we haven't incurred any cost yet if we haven't taken an action
        if self.control_dict == {}:
            return 0, 0
        
        cost = cost_loss_load * self.control_dict["loss_load"] + cost_overgeneration * self.control_dict["overgeneration"] \
            + self.prev_state["grid_price_import"] * self.control_dict["grid_import"] \
            + self.prev_state["grid_price_export"] * self.control_dict["grid_export"] \
            + (self.control_dict["battery_charge"] + self.control_dict["battery_discharge"]) * cost_battery \
            + cost_co2 * self.control_dict["grid_import"] * self.prev_state["grid_co2"]
        
        normalized_cost = (cost - self.grid_cost_without_battery()) / self.load_ts.sum()
        return cost, normalized_cost

    def grid_cost_without_battery(self):
        """
        Calculates the cost of the grid in one iteration if we didn't have a battery.
        """
        load_pv = self.prev_state["load"] - self.prev_state["pv"]
        if load_pv <= 0:
            return 0
        grid_cost = self.prev_state["grid_price_import"] * load_pv \
                + self.cost_co2 * load_pv * self.prev_state["grid_co2"]
        return grid_cost
