# Cartpole with Project Bonsai

## Objective

Starting with the pendulum upright, prevent the system from falling down by moving the cart left or right. 

![](https://docs.bons.ai/images/cart-pole-balance.gif)

# States, Actions, and available Configuration

See `machine_teacher.ink`.

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

You can run the simulator with random actions (without connecting to a brain):

```bash
python main.py --test-random --render
```

## Connecting a local instance of the simulator to a brain

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

Use `python main.py -h` to see more options.

## Running the simulator with an exported brain

Export a trained brain and run it locally using docker. Then, run the following:

```bash
python main.py --test-exported
```

or

```bash
python main.py --test-exported 5001
```

if your exported brain isn't running on the default port of 5000.


## Building Simulator Packages

Using the `azure-cli`, you can build the provided dockerfile to create a simulator package:

```azurecli
az acr build --image <IMAGE_NAME>:<IMAGE_VERSION> --file Dockerfile --registry <ACR_REGISTRY> .
```

`<IMAGE_NAME>:<IMAGE_VERSION>` could be e.g. `carts_and_poles:v1`. You can look up `<ACR_REGISTRY>` in the workspace info in the Bonsai UI.

If you get an error like this:

```
The resource with name <ACR_REGISTRY_NAME> and type 'Microsoft.ContainerRegistry/registries' could not be found in subscription '<something>'
```

look up your subscription id in the workspace info in the Bonsai UI, and run 

```azurecli
az account set --subscription <SUBSCRIPTION_ID>
```
