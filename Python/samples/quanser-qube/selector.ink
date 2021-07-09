###
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Multi-concept with learned selector architecture using Quanser Qube.
# Train the SwingUp Concept
# Programmed Balance Concept using LQR (Linear Quadratic Regulator) Controller

###

inkling "2.0"
using Number
using Math
using Goal

# Constant threshold for desired region of pendulum, where 0 is vertical
const alpha_balance_threshold = 12 

# Constant threshold for defining terminal condition of motor
const theta_rotation_threshold = 90

# State from the sim and for the brain
type ObservableState {
    theta: number, # radians, motor angle
    alpha: number, # radians, pendulum angle
    theta_dot: number, # radians / s, motor angular velocity
    alpha_dot: number, # radians / s, pendulum angular velocity
}

# Action type definition is the same for both concepts
type BrainAction {
    Vm: Number.Float32<-3 .. 3> # Voltage of motor
}

# Simulator configuration 
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
    initial_theta: number, # radians, motor angle
    initial_alpha: number, # radians, pendulum angle. 0 : vertical, pi : down
    initial_theta_dot: number, # radians / s, motor angular velocity
    initial_alpha_dot: number, # radians / s, pendulum angular velocity
}

# Function to convert Degrees to Radians for constants given in Degrees 
function DegreesToRadians (Degrees: number): number {
    return Degrees * Math.Pi / 180
}

# Function for Linear Quadratic Regulator (Programmed Controller not used)
function LQR(State: ObservableState): BrainAction {
    var K = [-2.0, 35.0, -1.5, 3.0]
    return {
        Vm: K[0] * State.theta + K[1] * State.alpha + K[2] * State.theta_dot + K[3] * State.alpha_dot,
    }
}

# Simulator definition of simulator for both concepts
simulator QQ (action: BrainAction, config: SimConfig): ObservableState {
    package "QuanserQube"
}

# Define a concept graph with two learned concepts and a programmed 
# selector concept.
graph (input: ObservableState) {
    # Programmed concept using control theory designed around equilibrium point
    concept Balance(input): BrainAction {
        programmed LQR
    }

    # Learned concept for SwingUp with initial conditions near rest
    concept SwingUp(input): BrainAction {
        curriculum {
            source QQ
            
            training {
                EpisodeIterationLimit: 640, # 8 sec
            }

            # Incentivize for swing up 
            goal (State: ObservableState) {
                reach Swing:
                    Math.Abs(State.alpha) in Goal.RangeBelow(DegreesToRadians(alpha_balance_threshold))
                avoid `Hit Motor Limit`:
                    Math.Abs(State.theta) in Goal.RangeAbove(DegreesToRadians(theta_rotation_threshold))
            }

            lesson `Start At Rest` {
                scenario {
                    Lp: 0.129,
                    mp: 0.024,
                    Rm: 8.4,
                    kt: 0.042,
                    km: 0.042,
                    mr: 0.095,
                    Lr: 0.085,
                    Dr: 0.00027,
                    Dp: 0.00005,
                    frequency: 80,
                    initial_theta: number<-0.27 .. 0.27>,
                    initial_alpha: number<Math.Pi-0.05 .. Math.Pi+0.05>,  # reset at rest
                    initial_theta_dot: number <-0.05 .. 0.05>,
                    initial_alpha_dot: number<-0.05 .. 0.05>,
                }
            }
        }
    }

    # Learned concept to pick between strategies
    concept SwitchControlStrategy(input): BrainAction {
        select SwingUp
        select Balance
        curriculum {
            source QQ

            training {
                EpisodeIterationLimit: 640, # 8 sec
                NoProgressIterationLimit: 750000
            }
            
            goal (State: ObservableState) {
                drive `Pendulum Angle`:
                    Math.Abs(State.alpha) in Goal.RangeBelow(DegreesToRadians(alpha_balance_threshold))
                avoid `Motor Limit`:
                    Math.Abs(State.theta) in Goal.RangeAbove(DegreesToRadians(theta_rotation_threshold))
                minimize Center:
                    Math.Abs(State.theta) in Goal.RangeBelow(DegreesToRadians(20)) 
            }

            lesson `Start At Rest` {
                scenario {
                    Lp: 0.129,
                    mp: 0.024,
                    Rm: 8.4,
                    kt: 0.042,
                    km: 0.042,
                    mr: 0.095,
                    Lr: 0.085,
                    Dr: 0.00027,
                    Dp: 0.00005,
                    frequency: 80,
                    initial_theta: number<-0.27 .. 0.27>,
                    initial_alpha: number<Math.Pi-0.05 .. Math.Pi+0.05>,  # reset at rest
                    initial_theta_dot: number <-0.05 .. 0.05>,
                    initial_alpha_dot: number<-0.05 .. 0.05>,
                }
            }
        }
    }
    
    # Set the output concept out of the graph
    output SwitchControlStrategy
}