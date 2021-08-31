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
    K: number, # Thermal conductivity
    C: number, # Thermal Capacity
    Qhvac: Number.Float32, # Heat Flux
    Tin_initial: number, # C
    Tout_initial: number, # C, sinewave signal bias
    Tset_temp_transitions: number[1][2],
    Tset_time_transitions: number[1][2],
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
                    Tout_initial: number<18 .. 22>, # C, sinewave signal bias
                    Tset_temp_transitions: [20, 25],
                    Tset_time_transitions: [0, 12],
                }
                }
            }
        }
    }
}