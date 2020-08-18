# https://docs.bons.ai/references/inkling2-reference.html
inkling "2.0"
using Number
using Math
using Goal

# The maximum angle (in radians) before fallover or failure
const MaxPoleAngle = (12 * 2 * Math.Pi) / 360
# Length of the cartpole track in meters
const TrackLength = 0.8

# constants describing the actions by the brain
const left: Number.Int8 = 0
const right: Number.Int8 = 1


type State {
    x_position: Number.Float32,
    x_velocity: Number.Float32,
    angle_position: Number.Float32,
    angle_velocity: Number.Float32
}

type Action {
    command: Number.Int8<left, right,>
}

# Configuration variables for the simulator
# These can be accessed by the event loop in your client code.
# masspole: the mass of the pole to balance
# length: the length of the pole to balance
type SimConfig {
    masspole: number,
    length: number
}

graph (input: State): Action {
    concept BalancePole(input): Action {
        curriculum {
            source simulator (Action: Action, Config: SimConfig): State {
            }
            goal (State: State) {
                avoid FallOver:
                    Math.Abs(State.angle_position) in Goal.RangeAbove(MaxPoleAngle)
                avoid OutOfRange:
                    Math.Abs(State.x_position) in Goal.RangeAbove(TrackLength / 2)
            }
        }
    }
}