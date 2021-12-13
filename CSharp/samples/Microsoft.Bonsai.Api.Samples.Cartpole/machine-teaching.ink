# This sample demonstrates how to teach a policy for controlling
# a cartpole (inverted pendulum) device.

inkling "2.0"

using Math
using Goal

# Length of the cartpole track in meters
const TrackLength = 0.5

# Maximum angle of pole in radians before it has fallen
const MaxPoleAngle = (12 * Math.Pi) / 180


# Type that represents the per-iteration state returned by simulator
type SimState {
    # Position of cart in meters
    cart_position: number,

    # Velocity of cart in meters/sec
    cart_velocity: number,

    # Current angle of pole in radians
    pole_angle: number,

    # Angular velocity of the pole in radians/sec
    pole_angular_velocity: number,
}

# Type that represents the per-iteration action accepted by the simulator
type SimAction {
    # Amount of force in x direction to apply to the cart.
    command: number<-1 .. 1>
}

# Define a concept graph with a single concept
graph (input: SimState): SimAction {
    concept BalancePole(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator
            # that takes an action as an input and outputs a state.
            source simulator (Action: SimAction): SimState {
                # Automatically launch the simulator with this
                # registered package name.
                # package "cartpole_csharp"
            }

            training {
                # Limit the number of iterations per episode to 120. The default
                # is 1000, which makes it much tougher to succeed.
                EpisodeIterationLimit: 120
            }

            # The objective of training is expressed as a goal with two
            # subgoals: don't let the pole fall over, and don't move
            # the cart off the track.
            goal (State: SimState) {
                avoid `Fall Over`:
                    Math.Abs(State.pole_angle)
                    in Goal.RangeAbove(MaxPoleAngle)
                avoid `Out Of Range`:
                    Math.Abs(State.cart_position)
                    in Goal.RangeAbove(TrackLength / 2)
            }
        }
    }
}

# Special string to hook up the simulator visualizer
# in the web interface.
const SimulatorVisualizer = "/cartpoleviz/"
