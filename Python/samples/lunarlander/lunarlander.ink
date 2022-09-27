inkling "2.0"
using Math
using Goal
using Number
const ThrottleMax = 1
const ThrottleMin = -1

simulator LunarLanderSim(Action: BrainAction, Config: LunarLanderConfig): SimState {
}

graph (input: ObservableState): BrainAction {
    concept RemovePositionStates(input): ReducedObservableState {
        programmed function (`input`: ObservableState): ReducedObservableState {
            return {
                #x_position: input.x_position,
                #y_position: input.y_position,
                x_velocity: `input`.x_velocity,
                y_velocity: `input`.y_velocity,
                angle: `input`.angle,
                rotation: `input`.rotation,
                left_leg: `input`.left_leg,
                right_leg: `input`.right_leg,
                #ship_landed: `input`.ship_landed,
                #ship_crashed: `input`.ship_crashed,
            }
        }
    }

    concept MoveUp(RemovePositionStates): BrainAction {
        curriculum {
            source LunarLanderSim

            training {
                EpisodeIterationLimit: 150,
                NoProgressIterationLimit: 500000
            }
            # Set of objectives to be met during the training session.
            goal (State: SimState, Action: BrainAction) {
                avoid crash weight 10:
                    State.ship_crashed
                    in Goal.RangeAbove(0.5)

                minimize hor_move weight 10:
                    Math.Abs(State.x_velocity)
                    in Goal.RangeBelow(0.8)

                minimize move_up weight 10:
                    Math.Abs(State.y_velocity - 0.3)
                    in Goal.RangeBelow(0.2)
            }

            lesson `Lesson 1` {
                scenario {
                    randomized_steps: number<20 .. 30 step 1>
                }
            }
        }
    }

    concept MoveRight(RemovePositionStates): BrainAction {
        curriculum {
            source LunarLanderSim

            training {
                EpisodeIterationLimit: 150,
                NoProgressIterationLimit: 500000
            }
            # Set of objectives to be met during the training session.
            goal (State: SimState, Action: BrainAction) {
                avoid crash weight 10:
                    State.ship_crashed
                    in Goal.RangeAbove(0.5)

                minimize ver_move weight 10:
                    Math.Abs(State.y_velocity)
                    in Goal.RangeBelow(0.8)

                minimize move_right weight 10:
                    Math.Abs(State.x_velocity - 0.3)
                    in Goal.RangeBelow(0.2)
            }

            lesson `Lesson 1` {
                scenario {
                    randomized_steps: number<20 .. 30 step 1>
                }
            }
        }
    }

    concept MoveLeft(RemovePositionStates): BrainAction {
        curriculum {
            source LunarLanderSim

            training {
                EpisodeIterationLimit: 150,
                NoProgressIterationLimit: 500000
            }
            # Set of objectives to be met during the training session.
            goal (State: SimState, Action: BrainAction) {
                avoid crash weight 10:
                    State.ship_crashed
                    in Goal.RangeAbove(0.5)

                minimize ver_move weight 10:
                    Math.Abs(State.y_velocity)
                    in Goal.RangeBelow(0.8)

                minimize move_left weight 10:
                    Math.Abs(State.x_velocity + 0.3)
                    in Goal.RangeBelow(0.2)
            }

            lesson `Lesson 1` {
                scenario {
                    randomized_steps: number<20 .. 30 step 1>
                }
            }
        }
    }

    concept MoveDown(RemovePositionStates): BrainAction {
        curriculum {
            source LunarLanderSim

            training {
                EpisodeIterationLimit: 150,
                NoProgressIterationLimit: 500000
            }
            # Set of objectives to be met during the training session.
            goal (State: SimState, Action: BrainAction) {
                avoid crash weight 10:
                    State.ship_crashed
                    in Goal.RangeAbove(0.5)

                minimize hor_move weight 10:
                    Math.Abs(State.x_velocity)
                    in Goal.RangeBelow(0.8)

                minimize move_down weight 10:
                    Math.Abs(State.y_velocity + 0.3)
                    in Goal.RangeBelow(0.2)
            }

            lesson `Lesson 1` {
                scenario {
                    randomized_steps: number<20 .. 30 step 1>
                }
            }
        }
    }

    concept StopEngines(RemovePositionStates): BrainAction {
        programmed function (`input`: ReducedObservableState): BrainAction {
            return {
                engine1: 0,
                engine2: 0
            }
        }
    }

    output concept Land(input): BrainAction {
        select MoveUp
        select MoveDown
        select MoveLeft
        select MoveRight
        select StopEngines
        curriculum {
            source LunarLanderSim

            training {
                EpisodeIterationLimit: 300,
                NoProgressIterationLimit: 1000000
            }
            # Set of objectives to be met during the training session.
            goal (State: SimState, Action: BrainAction) {
                avoid crash weight 100:
                    State.ship_crashed
                    in Goal.RangeAbove(0.5)

                minimize distance_to_land_pod weight 50:
                    Math.Hypot(Math.Abs(State.x_position), Math.Abs(State.y_position))
                    in Goal.RangeBelow(0.17)

                minimize landed weight 10:
                    -(State.left_leg + State.right_leg)
                    in Goal.RangeBelow(-0.67)

                minimize speed weight 1:
                    Math.Hypot(Math.Abs(State.x_velocity), Math.Abs(State.y_velocity))
                    in Goal.RangeBelow(0.33)

                minimize fuel weight 10:
                    Math.Abs(Action.engine1) + Math.Abs(Action.engine2)
                    in Goal.RangeBelow(2.5)

            }

            lesson `Lesson 1` {
                scenario {
                    randomized_steps: number<20 .. 30 step 1>
                }
            }
        }
    }
}
# Full STATE SPACE provided by the simulation.
type SimState {
    # Position of the spaceship.
    x_position: number,
    y_position: number,

    # Velocity of the spaceship.
    x_velocity: number,
    y_velocity: number,

    # Angle and angular speed of the spaceship respect the vertical axis.
    angle: number,
    rotation: number,

    # Flags to indicate if the landing legs of the spaceship
    #  are touching the ground (1) or not (0).
    left_leg: number,
    right_leg: number,

    # Flags to be able to tell when we have crashed or landed.
    ship_crashed: Number.Bool,
    ship_landed: Number.Bool,
}
# STATE SPACE that will be observed by the brain to make decisions.
#  Only variables that are accessible or computable during deployment
#  should be included here.
type ObservableState {
    # Position of the spaceship.
    x_position: number,
    y_position: number,

    # Velocity of the spaceship.
    x_velocity: number,
    y_velocity: number,

    # Angle and angular speed of the spaceship respect the vertical axis.
    angle: number,
    rotation: number,

    # Flags to indicate if the landing legs of the spaceship
    #  are touching the ground (1) or not (0).
    left_leg: number,
    right_leg: number,
}
# ACTIONS to be taken by the brain.
type BrainAction {
    engine1: number<ThrottleMin .. ThrottleMax>,
    engine2: number<ThrottleMin .. ThrottleMax>,
}
# CONFIGURATION used to initialize the simulation
#  at the beginning of a new episode.
type LunarLanderConfig {
    # Number of iterations to randomize actions.
    randomized_steps: number<0 .. 40 step 1>,
}
# STATE SPACE that will be observed by the brain to make decisions.
#  Low-level Concepts will not have visibility over the position of the ship (in x/y directions).
type ReducedObservableState {
    # Velocity of the spaceship.
    x_velocity: number,
    y_velocity: number,

    # Angle and angular speed of the spaceship respect the vertical axis.
    angle: number,
    rotation: number,

    # Flags to indicate if the landing legs of the spaceship
    #  are touching the ground (1) or not (0).
    left_leg: number,
    right_leg: number,

}

#! Visual authoring information
