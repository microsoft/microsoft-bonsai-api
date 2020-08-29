inkling "2.0"

# Inkling code for adding two values

using Number

experiment {
    backend_type: "pdp-stub",
    custom_algo: "ADDER",
    num_workers: "3",
}

type GameState {
   value1: Number.UInt8<0 .. 9>,
   value2: Number.UInt8<0 .. 9>,
   _reward: Number.UInt8<0, 1,>,
}

type Action {
   sum: Number.UInt8<0 .. 20>,
   garbage: Number.UInt8
}

type AdderConfig {
   episode_length: 1,
   deque_size: 1
}

function Reward(obs: GameState) {
  return 1
}

simulator the_simulator(action: Action, config: AdderConfig): GameState {
    # package "adder"
}

graph (input: GameState): Action {
    concept addition(input): Action {
        curriculum {
            reward Reward
            source the_simulator
        }
    }
    output addition
}
