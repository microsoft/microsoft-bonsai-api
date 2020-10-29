inkling "2.0"
using Number
using Goal
using Math

const MaxDeviation = 2

type ObservableState {
    Tset: number,
    Tin: number,
    Tout: number,
}

type SimAction {
    hvacON: number <0,1,>
}

type SimConfig {
    K: number,
    C: number,
    Qhvac: number,
    Tin_initial: number,
    schedule_index: number,
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
