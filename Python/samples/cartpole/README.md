# Cartpole with Project Bonsai

## Objective

Starting with the pendulum upright, prevent the system from falling down by moving the cart left or right. 

![](https://docs.bons.ai/images/cart-pole-balance.gif)

## States

| State                    | Range         |
| ------------------------ | ------------- |
| cart position            | [-2.4..2.4]   |
| cart velocity            | [-Inf..Inf]   |
| pendulum angle           | [-41.8..41.8] |
| pendulum velocity at tip | [-Inf..Inf]   |

## Actions

| Action          | Discrete Value |
| --------------- | -------------- |
| Push Cart Left  | 0              |
| Push Cart Right | 1              |

## Configuration Parameters

- masspole
- length of pole

## Simulator API - Python

- `cartpole`
    - `reset()`
    - `step()`
- `viewer`
    - `update()`

## Building Simulator Packages

Using the `azure-cli`, you can build the provided dockerfile to create a simulator package:

```
az acr build --image <IMAGE_NAME>:<IMAGE_VERSION> --file Dockerfile --registry <ACR_REGISTRY> .
```