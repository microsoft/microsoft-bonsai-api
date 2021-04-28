inkling "2.0"
using Number
using Goal
using Math

const MaxDeviation = 2
const MaxIterations = 288

type ObservableState {
    Tset: Number.Float32,
    Tin: Number.Float32,
    Tout: Number.Float32,
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


graph (input: ObservableState): SimAction {
    concept SmartHouse(input): SimAction {
        curriculum {
            source simulator (Action: SimAction, Config: SimConfig): ObservableState {

            }
            goal (State: ObservableState) {
                minimize `Temp Deviation`:
                    TempDiff(State.Tin, State.Tset) in Goal.RangeBelow(MaxDeviation)
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
                    schedule_index: 2,
                    number_of_days: 1,
                    timestep: 5,
                    max_iterations: MaxIterations
                }
            }
        }
    }
}