# Simple Adder - A minimal working example of a Bonsai simulator

This sample is a [minimal working example](https://en.wikipedia.org/wiki/Minimal_working_example) of a Python simulator that can be connected to Bonsai and used to train a brain. You can think of it as Project Bonsai's "Hello World".

This sample is intended to be used for:
* Understanding how the microsoft-bonsai-api Python API works. In just a few lines of code, you can see all the steps of the process.
* Experimentation where you want to get something simple up and running quickly in order to try out an idea.
* A base for reproducing problems. If you can modify this sample to reproduce a bug, this will give you a small program that's easy to share with those who need to investigate the bug.

This sample is not intended to be used for:
* Advanced features of Bonsai.
* A base for creating production code for a simulator. [cartpole](../cartpole/README.md) or the [other samples](../../../README.md#python) contain a richer set of helper code that is likely to be useful for production code.
* An exciting demo with a realistic simulation or a useful brain.

## What is being "simulated"?

The simulation in this sample is intentionally very simple.

| Configuration | Description |
| ----- | ----- |
| initial_value | Value at which the simulation will start. |

| State | Description |
| ----- | ----- |
| value | Current value. |

| Action | Description | 
| ------ | -------------------- |
| addend | Value that will be added to the current value. |

When an episode begins, the simulation's *value* state is set to *initial_value*. *initial_value* is randomly chosen by the Bonsai service based on the range of initial conditions specified in the lesson in [machine_teacher.ink](machine_teacher.ink).

During an episode, at each step, the simulation adds to its *value* state the *addend* action value that was chosen by the brain. Note that *addend* can be negative, which will cause *value* to decrease.

During training, the brain learns to achieve the goal specified in [machine_teacher.ink](machine_teacher.ink). It learns to control the *addend* to achieve a value of 50.

## How to run the sample

### 1. Set up environment variables

Set up the following environment variable on your development PC:

| Environment Variable | Description |
| ----- | ----- |
| SIM_WORKSPACE | The workspace ID from [your workspace details](https://docs.microsoft.com/en-us/bonsai/cookbook/get-workspace-info). |
| SIM_ACCESS_KEY | The access key from [your workspace details](https://docs.microsoft.com/en-us/bonsai/cookbook/get-workspace-info). |

Make sure those environment variables have been applied in the command window that you use for the next steps.

### 2. Set up Python environment

Create a conda environment by:

```
conda create -n simple-adder python=3.7
conda activate simple-adder
pip install -r requirements.txt
```

### 3. Connect local instance of the simulator

Run the simulator locally by:

```
python main.py
```

The output should say `Registered simulator` followed by--every several seconds a lines saying `Last Event: Idle`. Press Ctrl+C to stop the simulator.

### 4. Build simulator package

Scale your simulator by building the Docker container image, pushing it to your registry, and creating a simulator package.
In the following commands, `<SUBSCRIPTION_ID>` and `<ACR_REGISTRY_NAME>` should be replaced with
[your workspace details](https://docs.microsoft.com/en-us/bonsai/cookbook/get-workspace-info).

```
docker build -t simple-adder:latest -f Dockerfile .
docker tag simple-adder:latest <ACR_REGISTRY_NAME>.azurecr.io/simple-adder:latest
az acr login --subscription <SUBSCRIPTION_ID> --name <ACR_REGISTRY_NAME>
docker push <ACR_REGISTRY_NAME>.azurecr.io/simple-adder:latest
bonsai simulator package container create --name simple-adder -u <ACR_REGISTRY_NAME>.azurecr.io/simple-adder:latest --max-instance-count 25 -r 1 -m 1 -p Linux
```

### 5. Train a brain

```
bonsai brain create -n simple-adder
bonsai brain version update-inkling -f machine_teacher.ink -n simple-adder
bonsai brain version start-training -n simple-adder --simulator-package-name simple-adder
```
