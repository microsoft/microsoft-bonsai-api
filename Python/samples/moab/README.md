# Cartpole with Project Bonsai

## Objective

Starting with the horizontal plate and ball in some random positions and velocities with some initial roll and pitch of the actuator within bounds prevents the system from terminating. 

![](https://microsoft.github.io/moab/img/tutorials/1/moab-photo.png)

## States

| State                    | Range         |
| ------------------------ | ------------- |
| ball_x           | [-Radius_of_plate..Radius_of_plate]   |
| ball_vel_x       | [-1.0..1.0]   |
| ball_y           | [-Radius_of_plate..Radius_of_plate]  |
| ball_vel_y       | [-1.0..1.0]   |

## Actions

| Action          | Discrete Value |
| --------------- | -------------- |
| input_roll      | [-1.0..1.0]    |
| input_pitch     | [-1.0..1.0]    |

## Configuration Parameters

- initial_x, initial_y
- initial_vel_x, initial_vel_y
- initial_pitch, initial_roll

## Simulator API - Python

- `moab_model`
    - `reset()`
    - `step()`

## Testing Simulator Locally

You can test the simulator integration by running:

```bash
test_moab_model.py
test_moab_perf.py
test_moab_sim.py
```

or by testing the function `test_random_policy` in `main.py`.

## Running the Simulator Locally

Run the simulator locally by:

```bash
python moab_main.py
```

and then attach to your brain:

```
bonsai simulator unmanaged connect \                          
    -b <brain_name> \
    -a Train \
    -c MoveToCenter \
    --simulator-name Cartpole 
```

## Building Simulator Packages

Using the `azure-cli`, you can build the provided dockerfile to create a simulator package:

```
az acr build --image <IMAGE_NAME>:<IMAGE_VERSION> --file Dockerfile --registry <ACR_REGISTRY> .
```
