inkling "2.0"
using Goal

type SimState {
    state_config_val: number,
    state_action_val: number,
    total: number,
}

type Action {
    action_val: number<0..10 step 1>,
}

type SimConfig {
    config_val: number,
}

graph (input: SimState): Action {
    concept Concept(input): Action {
        curriculum {
            source simulator (Action: Action, Config: SimConfig): SimState {
            }

            training {
                EpisodeIterationLimit: 5,
            }

            goal (state: SimState) {
                drive HighTotal:
                    state.total in Goal.Range(29.9, 30.1)
            }

            lesson `learn 1` {
                scenario { 
                    config_val: number<0 .. 29 step 1>,
                }
            }
        }
    }
}
