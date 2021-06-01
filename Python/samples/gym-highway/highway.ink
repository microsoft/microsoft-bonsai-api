###

# MSFT Bonsai 
# Copyright 2021 Microsoft
# This code is licensed under MIT license (see LICENSE for details)

# Gym Highway Env demonstrating usage of arrays in sim state type definition
# and selecting elements in the writing of a reward function.

###

inkling "2.0"
using Number

# Using kinematic observations where vehicle1 is the ego
# "presence", "x", "y", "vx", "vy", "cos_h", "sin_h"
# Vehicles 2-5 are other vehicles as actors with their own behaviors
type SimState {
    vehicle1: number[7],
    vehicle2: number[7],
    vehicle3: number[7],
    vehicle4: number[7],
    vehicle5: number[7],
    collision: number,
    gym_reward: number,
    gym_terminal: Number.Bool
}

# Each vehicle has an array of fixed length of 7
# https://highway-env.readthedocs.io/en/latest/observations/index.html
type GameState {
    vehicle1: number[7],
    vehicle2: number[7],
    vehicle3: number[7],
    vehicle4: number[7],
    vehicle5: number[7],
}

# Reward for higher velocity and penalize for collisions
# Note how the reward takes the third element, since arrays in Inkling are 
# zero based.
function Reward(State: SimState) {
    var a = 0.4
    var b = 1
    var v_min = 20 # m/s
    var v_max = 30 # m/s
    var v = State.vehicle1[3]

    return a * ((v - v_min) / (v_max - v_min)) - b * State.collision
}

# Use provided simulator's terminal condition for collisions
function Terminal(State: SimState) {

    return State.gym_terminal
}

# 0: 'LANE_LEFT',
# 1: 'IDLE',
# 2: 'LANE_RIGHT',
# 3: 'FASTER',
# 4: 'SLOWER'
# https://highway-env.readthedocs.io/en/latest/actions/index.html
type CarSteer {
    steer: number<0..4 step 1>,
}

# Change the highway environment difficulty
type HighwayConfig {
    controlled_vehicles: number,
    ego_spacing: number,
    vehicles_count: number,
    lanes_count: number
}

# Specify the simulator
simulator HighwaySimulator(action: CarSteer, config: HighwayConfig): SimState {
}

# Graph with single learned concept over varying number of vehicles and lanes
graph (input: GameState) {
    concept Drive(input): CarSteer {
        curriculum {
            source HighwaySimulator
            reward Reward
            terminal Terminal

            lesson `Vary Highway Scenario` {
                scenario {
                    vehicles_count: number<25..50 step 1>,
                    lanes_count: number<4..6 step 1>
                }
            }
        }
    }
    output Drive
}