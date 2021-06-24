# https://docs.microsoft.com/en-us/bonsai/inkling/basics
inkling "2.0"

const data_length = 8760 # there are 8760 data points in the sim for a microgrid (1 year data captured at every hour)
const episode_length = 24*2 # episodes are two days long
const horizon = 24 # this is the number of hours we will forecast the data (pv, load) if we add forecasts to states (not yet implemented)

const upper_starting_index = data_length - episode_length - horizon - 1 # we will reset the sim to a random time index, this variable is the upper bound on the initial time index

# These are all the values the sim produces
type SimState {
    load: number<5000..50000>,
    hour: number<0..24>,
    pv: number<0..75000>,
    battery_soc: number<0..1>,
    capa_to_charge: number<0..65305>,
    capa_to_discharge: number<0..65305>,
    grid_status: number<0, 1,>,
    grid_co2: number<0..0.4>,
    grid_price_import: number<0.075..0.205>,
    grid_price_export: number<0..1>,
    pv_load_diff: number<-45000..65000>,
    cost: number,
    co2_emission: number,
    prev_load: number,
    prev_pv: number,
    prev_grid_price_import: number,
    prev_grid_co2: number,
    prev_action_grid_import: number,
    sum_load: number,
    cost_co2: number,
}

# This is a subset of the SimState that we'll make available to the brain
# (these should all be values that will be available to a deployed brain)
type ObservedState {
    load: number<5000..50000>,
    hour: number<0..24>,
    pv: number<0..75000>,
    capa_to_charge: number<0..65305>,
    capa_to_discharge: number<0..65305>,
    grid_status: number<0, 1,>,
    grid_co2: number<0..0.4>,
    grid_price_import: number<0.075..0.205>,
}

type Action {
    # if positive it means charge the battery, else means discharge
    battery_power: number<-16327..16327>,
}

# Configuration variables for the simulator
type SimConfig {
    starting_time_step: number<0..upper_starting_index>,
    cost_overgeneration: number,
    cost_loss_load: number,
    cost_battery: number,
    cost_co2: number,
    episode_length: number
}

function GridCostWithoutBattery(load: number, pv: number, grid_price_import: number, 
    cost_co2: number, grid_co2: number) {
    var load_pv_diff = load - pv
    if load_pv_diff <= 0 {
        return 0
    }
    return grid_price_import * load_pv_diff + cost_co2 * load_pv_diff * grid_co2
}

function GetNormalizedCost(grid_price_import: number, grid_import: number, 
     cost_co2: number, grid_co2: number, load: number, pv: number, sum_load: number) {
    # calculates the normalized cost of running the grid. 
    # To normalize, we first subtract the cost if we didn't have a battery then divide the result by the total load
    # throughout the whole episode
    # assumes there is no cost associated with using the battery
    var cost =  grid_price_import * grid_import + cost_co2 * grid_import * grid_co2
    return (cost - GridCostWithoutBattery(load, pv, grid_price_import, cost_co2, grid_co2)) / sum_load
}

function GetReward(s: SimState){
    # calculate the reward based on previous states and actions
    var normalized_cost = GetNormalizedCost(s.prev_grid_price_import, s.prev_action_grid_import,
        s.cost_co2, s.prev_grid_co2, s.prev_load, s.prev_pv, s.sum_load)
    return - normalized_cost * 1000

}

graph (input: ObservedState): Action {
    concept OptimizeGrid(input): Action {
        curriculum {
            source simulator (Action: Action, Config: SimConfig): SimState {
                #package "mgridsim-demo"
            }
            algorithm {
                Algorithm: "SAC"
            }
            training {
                EpisodeIterationLimit: episode_length,
                NoProgressIterationLimit: 500000,
            }
            reward GetReward

            lesson StartMGrid {
                scenario {
                    # we take a step size of 11, to make sure the two episodes brains sees are not very similar
                    starting_time_step: number<0..upper_starting_index step 11>,
                    cost_battery: 0,
                    cost_loss_load: 10,
                    cost_co2: 0.1,
                    cost_overgeneration: 1,
                    episode_length: episode_length
                }
            }
        }
    }
}
