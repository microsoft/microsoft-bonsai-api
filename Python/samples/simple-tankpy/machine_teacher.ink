inkling "2.0"
using Goal

type SimConfig {
    initial_value: number,
}

type SimState {
    value: number
}

type Action {
    addend: number<-10..10>
}

graph (input: SimState): Action {
    concept Concept(input): Action {
        curriculum {
            source simulator (Action: Action, Config: SimConfig): SimState {
            }

            training {
                EpisodeIterationLimit: 10
            }

            goal (state: SimState) {
                reach Goal: state.value in Goal.Range(49.9, 50.1)
            }

            lesson `learn 1` {
                scenario { 
                    initial_value: number<0 .. 100>,
                }
            }
        }
    }
}
