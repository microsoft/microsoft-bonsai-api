###

# MSFT Bonsai 
# Copyright 2021 Microsoft
# This code is licensed under MIT license (see LICENSE for details)

# A Data Driven Model (DDM) may be trained  when there is no simulator or in 
# place of an actual sim to speed up training of a Bonsai brain. This Inkling 
# uses a state transform to instruct the brain learning of what the desired
# temperature should be as well as the outside temperature is using constants.

###

inkling "2.0"
using Number
using Goal
using Math

const MaxDeviation = 2
const MaxIterations = 288
const T_set = 25
const T_out = 32

type SimState {
    Tin: number,
}

type ObservableState {
    Tset: number,
    Tin: number,
    Tout: number,
}

type SimAction {
    hvacON: Number.Int8 <off=0, on=1,>
}

type SimConfig {
    K: Number.Float32, # Thermal conductivity
    C: Number.Float32, # Thermal Capacity
    Qhvac: Number.Float32, # Heat Flux
    Tin_initial: number, # C
    schedule_index: Number.Int8, # 1 - fixed, 2 - randomized
    number_of_days: number,
    timestep: number, # Min
    max_iterations: number, # Alters schedule generation
}

function TempDiff(Tin:number, Tset:number) {
    return Math.Abs(Tin - Tset)
}

function TransformState(s: SimState): ObservableState {
    return {
        Tset: T_set,
        Tin: s.Tin,
        Tout: T_out,
    }
}

graph (input: ObservableState): SimAction {
    concept SmartHouse(input): SimAction {
        curriculum {
            source simulator (Action: SimAction, Config: SimConfig): SimState {
                package "DDM-House"
                #package "HouseEnergy"
            }

            state TransformState

            goal (State: SimState) {
                minimize `Temp Deviation`:
                    TempDiff(State.Tin, T_set) in Goal.RangeBelow(MaxDeviation)
            }

            training {
                EpisodeIterationLimit: MaxIterations
            }

            lesson `Lesson 1` {
                scenario {
                    K: 0.5,
                    C: 0.3,
                    Qhvac: 9,
                    Tin_initial: number<18 .. 30>,
                    schedule_index: 3,
                    number_of_days: 1,
                    timestep: 5,
                    max_iterations: MaxIterations
                }
            }
        }
    }
}