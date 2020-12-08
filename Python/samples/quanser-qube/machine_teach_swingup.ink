###
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
###

inkling "2.0"
using Number
using Math
using Goal

# Constant threshold for desired region of pendulum, where 0 is vertical
const alpha_balance_threshold = 12 

# Constant threshold for defining terminal condition of motor
const theta_rotation_threshold = 90

type ObservableState {
    state_theta: number, # radians, motor angle
    state_alpha: number, # radians, pendulum angle
    state_theta_dot: number, # radians / s, motor angular velocity
    state_alpha_dot: number, # radians / s, pendulum angular velocity
}

type BrainAction {
    action_Vm: Number.Float32<-3 .. 3>
}

# simulator configuration 
type SimConfig {
    Lp: number, # m, length of pole
    mp: number, #kg, mass of pole
    Rm: number, # Resistance
    kt: number, # Current-torque (N-m/A)
    km: number, # Back-emf constant (V-s/rad)
    mr: number, # Mass (kg)
    Lr: number, # Total length (m)
    Dr: number, # Equivalent viscous damping coefficient (N-m-s/rad)
    Dp: number, # Equivalent viscous damping coefficient (N-m-s/rad)
    frequency: number, # Hertz
    inital_theta: number, # radians, motor angle
    initial_alpha: number, # radians, pendulum angle. 0 : vertical, pi : down
    initial_theta_dot: number, # radians / s, motor angular velocity
    initial_alpha_dot: number, # radians / s, pendulum angular velocity
}

# Function to convert Degrees to Radians for constants given in Degrees 
function DegreesToRadians (Degrees: number): number {
    return Degrees * Math.Pi / 180
}

function TerminalSwingUp (State: ObservableState) {
    var terminal:Number.Bool
    terminal = false
    
    # Passed the rotation limit for rotation of the motor
    if Math.Abs(State.state_theta) > DegreesToRadians(theta_rotation_threshold) {
        terminal = true
    }

    return terminal
}

# Reward function that is evaluated after each iteration
function RewardSwingUp (State: ObservableState) {
    var r = 1 - ((0.8 * Math.Abs(State.state_alpha) + 0.2 * Math.Abs(0 - State.state_theta)) / Math.Pi)
    var t = TerminalSwingUp(State)
    if t == true {
        return r - 100
    }
    return r 
}

graph (input: ObservableState) {
    concept SwingUp(input): BrainAction {
        curriculum {
            source simulator (action: BrainAction, config: SimConfig): ObservableState {
            }
            
            # Commented out because goal clause is used in place of reward/terminal
            #terminal TerminalSwingUp
            #reward RewardSwingUp

            training {
                EpisodeIterationLimit: 640, # 8 sec
            }

            # goal for swing up 
            goal (State: ObservableState) {
                reach Swing:
                    Math.Abs(State.state_alpha) in Goal.RangeBelow(DegreesToRadians(alpha_balance_threshold))
                avoid `Hit Motor Limit`:
                    Math.Abs(State.state_theta) in Goal.RangeAbove(DegreesToRadians(theta_rotation_threshold))
            }
        }
    }
}