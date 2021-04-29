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


type SimState {
    # Position of the cart with and without noise
    x_position: Number.Float32,
    x_position_no_noise: Number.Float32,

    # Velocity of the cart with and without noise
    x_velocity: Number.Float32,
    x_velocity_no_noise: Number.Float32,
    
    # Angle position of the cart with and without noise (zero at vertical position)
    angle_position: Number.Float32,
    angle_position_no_noise: Number.Float32,
    
    # Angle velocity of the cart with and without noise
    angle_velocity: Number.Float32,
    angle_velocity_no_noise: Number.Float32
}

type ObservableState {
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
    length: number,
    noise: number
}

graph (input: ObservableState): Action {
    concept BalancePole(input): Action {
        curriculum {
            source simulator (Action: Action, Config: SimConfig): SimState {
            }
            goal (State: SimState) {
                avoid FallOver:
                    Math.Abs(State.angle_position_no_noise) in Goal.RangeAbove(MaxPoleAngle)
                avoid OutOfRange:
                    Math.Abs(State.x_position_no_noise) in Goal.RangeAbove(TrackLength / 2)
            }
            lesson BalanceFixedNoise {
                # Specify the configuration parameters that should be varied
                # from one episode to the next during this lesson.
                scenario {
                    masspole: number<0.05 .. 0.3>,
                    length: number<0.3 .. 0.7>
                    noise: 0,
                }
            }
        }
    }
}