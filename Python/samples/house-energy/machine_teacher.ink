inkling "2.0"
using Number
using Goal
using Math

const MaxDeviation = 2

type ObservableState {
    Tset: Number.Float32,
    Tin: Number.Float32,
    Tout: Number.Float32,
}

type SimAction {
    hvacON: Number.Int8 <0,1,>
}

type SimConfig {
    K: Number.Float32,
    C: Number.Float32,
    Qhvac: Number.Float32,
    Tin_initial: number,
    schedule_index: Number.Int8,
    number_of_days: number,
    timestep: number,
    max_iterations: number,
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
        }
    }
}
