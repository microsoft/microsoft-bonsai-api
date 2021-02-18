# https://docs.bons.ai/references/inkling2-reference.html
inkling "2.0"
using Number
using Math
using Goal

# The maximum angle (in radians) before fallover or failure
const MaxPoleAngle = (12 * 2 * Math.Pi) / 360
# Length of the cartpole track in meters
const TrackLength = 2.0
const MaxPosition = TrackLength / 2


# These are all the values the sim produces
type SimState {
    cart_position: number,  # (m). 0 is the center of the track
    cart_velocity: number,  # (m/s)
    pole_angle: number,  # (rad). 0 is vertical.
    pole_angular_velocity: number,  # (rad/s)
    pole_center_position: number,  # (m) -- x position of the center of the pole 
    pole_center_velocity: number,  # (m/s) -- x velocity of the center of the pole
    target_pole_position: number,  # (m)

    # physical params from the config are available too
    cart_mass: number,  # (kg)
    pole_mass: number,  # (kg)
    pole_length: number,  # (m)
}

# This is a subset of the SimState that we'll make available to the brain
# (these should all be values that will be available to a deployed brain)
type ObservedState {
    cart_position: number,  # (m). 0 is the center of the track
    cart_velocity: number,  # (m/s)
    pole_angle: number,  # (rad). 0 is vertical.
    pole_angular_velocity: number,  # (rad/s)
}

type Action {
    # Force to apply, up to the max force magnitude (1 Newton by default)
    command: number<-1..1>
}

# Configuration variables for the simulator
type SimConfig {
    # Mass of cart in kg (default is 0.31)
    cart_mass: number,
    # Mass of pole in kg (default is 0.055)
    pole_mass: number,
    # Length of the pole in m (default is 0.4)
    pole_length: number,
    # Initial position of cart on the x axis in meters (0 is center)
    initial_cart_position: number<-MaxPosition .. MaxPosition>,
    # Initial velocity of cart in meters/sec
    initial_cart_velocity: number,
    # Initial angle of pole in radians
    initial_pole_angle: number,
    # Initial angular velocity of pole in radians/sec
    initial_angular_velocity: number,
    # Where we want the pole to be in m
    target_pole_position: number<-MaxPosition .. MaxPosition>,
}

graph (input: ObservedState): Action {
    concept BalancePole(input): Action {
        curriculum {
            source simulator (Action: Action, Config: SimConfig): SimState {
            }
            goal (SimState: SimState) {
                avoid FallOver:
                    Math.Abs(SimState.pole_angle) in Goal.RangeAbove(MaxPoleAngle)
                avoid OutOfRange:
                    Math.Abs(SimState.cart_position) in Goal.RangeAbove(MaxPosition)
            }
        }
    }
}

# Special string to hook up the simulator visualizer
# in the web interface.
const SimulatorVisualizer = "/cartpoleviz/"