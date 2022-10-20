# Lunar Lander Sample

## Objective

This environment is a classic rocket trajectory optimization problem.

According to Pontryagin's maximum principle, it is optimal to fire the engine at full throttle or turn it off. Yet, to be able to generalize to other control use cases, we use the continuous version of this problem. Our environment has continuous actions for both lateral and main engines.

The objective of our lander is landing on the landing pad without crashing. Config parameters allow to add randomness to the initial position of the ship, which by default is right over the landing pad.

The landing pad is always at coordinates (0,0). Landing outside of the landing pad is possible. Fuel is infinite.



![](https://raw.githubusercontent.com/cpow-89/Extended-Deep-Q-Learning-For-Open-AI-Gym-Environments/master/images/Lunar_Lander_v2.gif)


### Acknowledgments

[Gym Lunar Lander docs](https://gym.openai.com/envs/LunarLander-v2/)

```dotnetcli
@misc{lunarlander-v2-continuous,
  author = {Schneider, Jonas - OpenAI},
  title = {An Environment for Autonomous Rocket Trajectory Optimization},
  year = {2016},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/openai/gym/blob/master/gym/envs/box2d/lunar_lander.py}},
}
```

## Action

Action has three floats [main engine, left engine, right engine].
- Main engine: -1..0 off, 0..+1 throttle from 50% to 100% power. Engine can't work with less than 50% power.
- Left-right:  0..0.5 off, 0.5..1 fire (left or right) engine. Engine can't work with less than 50% power.

| Action | Discrete |  Description  |
| ------ | ---------------- | ------- |
| engine1 | 0 .. 1    |  Main engine thrust |
| engine_left | 0 .. 1    |  Lateral left engine thrust |
| engine_right | 0 .. 1    |  Lateral right engine thrust |

### Action v2

Alternatively, the ship can be controlled with only two floats [main engine, lateral engine].
- Main engine: -1..0 off, 0..+1 throttle from 50% to 100% power. Engine can't work with less than 50% power.
- Left-right:  -1.0..-0.5 fire left engine, +0.5..+1.0 fire right engine, -0.5..0.5 off

| Action | Discrete |  Description  |
| ------ | ---------------- | ------- |
| engine1 | 0 .. 1    |  Main engine thrust |
| engine2 | -1 .. 1    |  [-1, -0.5] LEFT engine thrust; [0.5, 1] RIGHT engine thrust |

## States

The state is an 8-dimensional vector: the coordinates of the lander in `x` & `y`, its linear
velocities in `x` & `y`, its angle, its angular velocity, and two booleans
that represent whether each leg is in contact with the ground or not.

Additionally, there are 2 sim states that are not observed during training. These 2 flags indicate if the ship crashed or effectively landed.

| State     | Type     | Description                                             |
| --------- | --------- | ------------------------------------------------------- |
| x_position     | -1.5 .. 1.5     | Horizontal position of the ship.                      |
| y_position     | -1.5 .. 1.5     | Vertical position of the ship.                        |
| x_velocity     | -5.0 .. 5.0     | Horizontal speed of the ship.                         |
| y_velocity     | -5.0 .. 5.0     | Vertical speed of the ship.                           |
| angle          | -PI .. PI       | Angle of the ship respect the vertical axis.          |
| rotation       | -5.0 .. 5.0     | Vertical speed of the ship.                           |
| left_leg       | boolean         | Flag that indicates left leg is touching ground.      |
| right_leg      | boolean         | Flag that indicates left leg is touching ground.      |
| ship_crashed   | boolean         | (not observed) Flag that indicates ship has crashed in the ground.   |
| ship_landed    | boolean         | (not observed) Flag that indicates ship has effectively landed.      |


## Terminal Conditions

- Colliding with the ground, indicated by the ship_crashed boolean.
- Fully turning over its axis, or reaching the range limits of any state variable.

## Configuration Parameters

| Configuration     | Type     | Description                                             |
| --------- | --------- | ------------------------------------------------------- |
| randomized_steps      | int <0..40>    | Number of random actions to apply during episode reset.              |
| randomized_strength   | float <0..1>   | Strength to apply to random actions applied during episode reset.    |
| delta_action          | boolean          | Whether to apply actions as given (0), or interpret them as a suggested increment from past action. Note, action is thresholded to whichever values are valid if hitting an action boundary.               |
| rolling_action_weight   | float <0..1>   | When enabled, the actions received are rolled over across iterations. 0 == No rolling window applied; 0.9 == 90% prev + 10% new. Note, rolling action is disabled when enabling delta actions.    |

## Install Requirements

1. Download **either** [miniconda](https://conda.io/miniconda.html) or [Anaconda](https://www.anaconda.com/download/)
2. Open Anaconda / miniconda command prompt
3. Change directory to the parent directory
    ```cmd
    cd Python/samples/gym-highway
    pip install -r requirements.txt
    ```

## Running the Simulator Locally

Run the simulator locally by the following command and setting environment variables for SIM_WORKSPACE and SIM_ACCESS_KEY.

```bash
python main.py
```

and then attach to your brain:

```bash
bonsai simulator unmanaged connect \                          
    -b <brain_name> \
    -a Train \
    -c <concept_name> \
    --simulator-name LunarLanderSim
```


## Evaluation of Trained Brain

The platform does not yet support assessment of programmed concepts, so export the brain and use it with the sim using main.py. Logs will be saved to `/logs` as csv format. The episode configuration(s) are pulled from the `test_scenarios.json` file.

```sh
export SIM_WORKSPACE=<your-workspace-id>
export SIM_ACCESS_KEY=<your-access-key>
az login
az acr login -n <acr-name>
docker pull <brain-uri>
docker run -d -p 5000:<PORT> <brain-uri>
python main.py --test-exported <port> --render
```

> An example: python main.py --test-exported 5005 --render --custom-assess assess_config.json

## Building Simulator Packages

Using the `azure-cli`, you can build the provided dockerfile to create a simulator package:

```bash
az acr build --image <IMAGE_NAME>:<IMAGE_VERSION> --file Dockerfile --registry <ACR_REGISTRY> .
```

## Useful Resources

- [Bonsai Docs](https://docs.microsoft.com/en-us/bonsai/)