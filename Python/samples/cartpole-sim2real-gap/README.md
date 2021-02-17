# Cartpole - Sim2Real Gap with Project Bonsai

## Objective

Starting with the pendulum upright, prevent the system from falling down by moving the cart left or right. 

In this variant of the common Cartpole problem, the objective is bridging the sim2real gap through two approaches:
- Adding gaussian noise to all state readouts
- Domain randomization

These are known techniques to make more robust DRL (Deep Reinforcement Learning) controls. They help pushing
brains to abstract more complex relationships between states, minimizing the risk of overfitting to simulated dynamics.

[disclaimer] The goal of this example is showing how to bridge the sim2real gap. Nonetheless, note that
Cartpole has simple enough dynamics to not require such techniques to avoid overfitting.

![](https://docs.bons.ai/images/cart-pole-balance.gif)

## Sim2Real Gap

The sim2real gap reflects on the often times encountered difficulties of deploying a brain on the
real world. It so can happen that a brain overachieves during simulation, but fails to succeed
during inference (e.g: when deployed in production).

The goal of using a simulation is to prepare and train the brain for real-world applications.
Thus, we need to engineer ways to prepare the agent to be robust enough to overcome possible
differences between simulation and production (the real world).

### Sim2Real Gap Solution: Adding noise

An initial solution to avoid overfitting to perfect state measurament is adding noise. Gaussian noise
in our case, added to each input state, is used to force the agent to look into soft-response dynamics.
It prevents it from taking rough changes based on each single measurement.

Check 'machine_teaching_1.ink' to see how the Inkling file is configured. Key differences from common Cartpole:
- Definition of Observable vs Sim State.
- Using non-noisy states to reward the agent. (further explained bellow, on 'Rewarding Approach' section).

### Sim2Real Gap Solution: Domain Randomization

Another solution to overcome overfitting is randomizing the dynamics of the simulation. Changing
the configuration specs in between episodes, such as pole length or gravity, will help the brain
see patterns that extend beyond the specifics of any given scenario.

If the brain successfully learns how to operate during different environment configurations,
it will be more robust to real-world dynamic differences from simulation to deployment.

Check 'machine_teaching_2.ink' to see how the Inkling file is configured. Key differences from common Cartpole:
- Definition of a lesson with ranges for desired configuration parameters.

## States

| State                             | Range           |
| --------------------------------- | --------------- |
| cart position                     | [-2.4 .. 2.4]   |
| cart position no noise            | [-2.4 .. 2.4]   |
| cart velocity                     | [-Inf .. Inf]   |
| cart velocity no noise            | [-Inf .. Inf]   |
| pendulum angle                    | [-41.8 .. 41.8] |
| pendulum angle no noise           | [-41.8 .. 41.8] |
| pendulum velocity at tip          | [-Inf .. Inf]   |
| pendulum velocity at tip no noise | [-Inf .. Inf]   |

This Cartpole variation has 8 states, instead of 4 existing on common Cartpole. This simulation
provides the 4 states required to describe the position of the cart/pole combo, plus their equivalents
without added gaussian noise (since we are engineering the gaussian noise addition).

The noisy inputs are assumed to be the ones that must be used for inference. Thus, our Observable State
is formed by the noisy states only. The greater set of 8 variables will be aggregated under the Sim State.
The clean ("no noise") states will be useful for rewarding the brain during training. Section 'Rewarding
Approach' explains how to exploit the Sim State.

## Actions

| Action          | Discrete Value |
| --------------- | -------------- |
| Push Cart Left  | 0              |
| Push Cart Right | 1              |

Actions do not change from common Cartpole example.

## Configuration Parameters

- masspole
- length of pole

The configuration parameters are the same as in common Cartpole.

## Rewarding Approach

The objectives are the same as in common Cartpole:
- Avoid moving the cart out of range.
- Avoid dropping the pole to an invalid high angle.
- Minimize the pole angle, mainting the pole as vertical as possible.

As indicated earlier, the Observable State is formed by the noisy states. In other words,
during brain inference (e.g: in production), the brain will only have access to the noisy readouts.

During brain training, though, the brain can have access to an additional set of states that can be
used to reward the agent. In this Cartpole variant, the Sim State includes both noisy and non-noisy states.
To ease brain training, the non-noisy states are the ones used to reward the agent:
- AVOID abs("cart position no noise") >= "max position"
- AVOID abs("pendulum angle no noise") >= "max angle"
- MINIMIZE abs("pendulum angle no noise") <= "target angle"

## Simulator API - Python

- `cartpole`
    - `reset()`
    - `step()`
- `viewer`
    - `update()`

## Testing Simulator Locally

You can test the simulator integration by running:

```bash
pytest tests/
```

or by testing the function `test_random_policy` in `main.py`.

## Running the Simulator Locally

Run the simulator locally by:

```bash
python main.py
```

and then attach to your brain:

```
bonsai simulator unmanaged connect \                          
    -b <brain_name> \
    -a Train \
    -c BalancePole \
    --simulator-name Cartpole 
```

## Building Simulator Packages

Using the `azure-cli`, you can build the provided dockerfile to create a simulator package:

```
az acr build --image <IMAGE_NAME>:<IMAGE_VERSION> --file Dockerfile --registry <ACR_REGISTRY> .
```