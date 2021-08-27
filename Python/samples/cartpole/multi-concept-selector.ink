# An example of using multiple concepts to solve a variant of the cartpole task:
# keeping the pole balanced on the cart while moving the cart to a specified point.
#
# This example breaks that task into 4 concepts:
#   - ComputeDelta: transform the state to compute the difference between the
#     current and target positions. This makes the policy independent of the
#     specific position of the cart, so it is easier and faster to learn.
#   - GoLeft: this applies when the cart is to the right of the target position, and learns
#     how to move the cart left without dropping the pole.
#   - GoRight: this applies when the cart is to the left of the target position, and learns
#     how to move the cart right without dropping the pole.
#   - PickOne: a selector concept that learns how to move the cart to the target position
#     and stabilize it there without dropping the pole, as appropriate for the current state.
#
# https://docs.microsoft.com/en-us/bonsai/inkling/basics
inkling "2.0"

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
    target_pole_position: number,
}

# We get a cart position and a target position, but it's more natural to compute the delta.
# Going to assume that the target position is always in-bounds, so won't worry about a goal of leaving the region
type LearningState {
    distance_to_target: number,   # target - current
    cart_velocity: number,
    pole_angle: number,
    pole_angular_velocity: number,
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

simulator CartpoleSim (Action: Action, Config: SimConfig): SimState {
    # To use managed simulators to train, upload the sim
    # (see README.md) and specify the package name here.
    # package "MyCartpole"
}

function SimplifyState(obs: ObservedState): LearningState {
    # Replace target position and cart position with the difference
    return {distance_to_target: obs.target_pole_position - obs.cart_position,
            cart_velocity: obs.cart_velocity,
            pole_angle: obs.pole_angle,
            pole_angular_velocity: obs.pole_angular_velocity,}
}

graph (input: ObservedState): Action {
    concept ComputeDelta(input): LearningState {
        programmed SimplifyState
    }

    concept GoLeft(ComputeDelta): Action {
        curriculum {
            source CartpoleSim
            goal (state: SimState) {
                avoid FallOver:
                    Math.Abs(state.pole_angle) in Goal.RangeAbove(MaxPoleAngle)

                # There isn't a specific "close enough" threshold, so using
                # Goal.RangeBelow(0) to encourage the system to minimize as well as it can
                minimize DistToTarget:
                    Math.Abs(state.target_pole_position - state.cart_position) in Goal.RangeBelow(0)
            }
            training {
                EpisodeIterationLimit: 200,
            }
            lesson One {
                # Because we're using relative positions, just need to randomize initial position to be far and close to the target.
                # "GoLeft" starts the cart to the right of the target.
                scenario {
                    initial_cart_position: number<0 .. MaxPosition>,
                    target_pole_position: 0
                }
            }
        }
    }

    concept GoRight(ComputeDelta): Action {
        curriculum {
            source CartpoleSim
            goal (state: SimState) {
                avoid FallOver:
                    Math.Abs(state.pole_angle) in Goal.RangeAbove(MaxPoleAngle)

                # There isn't a specific "close enough" threshold, so using
                # Goal.RangeBelow(0) to encourage the system to minimize as well as it can
                minimize DistToTarget:
                    Math.Abs(state.target_pole_position - state.cart_position) in Goal.RangeBelow(0)
            }
            training {
                EpisodeIterationLimit: 200,
            }
            lesson One {
                # Because we're using relative positions, just need to randomize initial position to be far and close to the target.
                # "GoRight" starts the cart to the left of the target.
                scenario {
                    initial_cart_position: number<-MaxPosition .. 0>,
                    target_pole_position: 0
                }
            }
        }
    }

    output concept PickOne(ComputeDelta): Action {
       select GoRight
       select GoLeft
       curriculum {
            source CartpoleSim
            training {
                EpisodeIterationLimit: 200,
                NoProgressIterationLimit: 1000000,
            }
            goal (state: SimState) {
                avoid FallOver: Math.Abs(state.pole_angle) in Goal.RangeAbove(MaxPoleAngle)
                minimize DistToTarget: Math.Abs(state.target_pole_position - state.cart_position) in Goal.RangeBelow(0)
            }
            lesson One {
                # Because we're using relative positions, just need to randomize initial position to be far and close to the target
                # "PickOne" starts at a random position within the full range.
                scenario {
                    initial_cart_position: number<-MaxPosition .. MaxPosition>,
                    target_pole_position: 0
                }
            }
       }


    }
}

# Special string to hook up the simulator visualizer
# in the web interface.
const SimulatorVisualizer = "/cartpoleviz/"