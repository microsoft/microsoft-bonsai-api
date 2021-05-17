inkling "2.0"
using Number

type SimState{
    vehicle1: number[6],
    vehicle2: number[6],
    vehicle3: number[6],
    vehicle4: number[6],
    vehicle5: number[6],
    gym_reward: number,
    gym_terminal: Number.Bool
}

type GameState {
    vehicle1: number[6],
    vehicle2: number[6],
    vehicle3: number[6],
    vehicle4: number[6],
    vehicle5: number[6],
}

function Reward(State: SimState) {

    return State.gym_reward
}

function Terminal(State: SimState) {

    return State.gym_terminal
}

type CarSteer {
    steer: number<0..4 step 1>,
}

type HighwayConfig {
    controlled_vehicles: number,
    ego_spacing: number,
    vehicles_count: number,
    lanes_count: number
}

simulator HighwaySimulator(action: CarSteer, config: HighwayConfig): SimState {
}

graph (input: GameState) {
    concept Drive(input): CarSteer {
        curriculum {
            source HighwaySimulator
            reward Reward
            terminal Terminal

            lesson `More Cars` {
                scenario {
                    vehicles_count: number<50..100 step 1>,
                    lanes_count: number<4..22 step 1>
                }
            }
        }
    }
    output Drive
}
