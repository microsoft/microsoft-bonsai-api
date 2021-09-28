# Bonsai Python Sim - Min Template

## Set up Python environment

Create a conda environment by:

```
conda create -n minbonsai python=3.7
conda activate minbonsai
pip install -r requirements.txt
```

## Connect a local instance of the simulator

Run the simulator locally by:

```
python main.py
```

## Build simulator package

Scale your simulator by building the Docker container image, pushing it to your registry, and creating a simulator package.
In the following commands, `<SUBSCRIPTION_ID>` and `<ACR_REGISTRY_NAME>` should be replaced with
[your workspace details](https://docs.microsoft.com/en-us/bonsai/cookbook/get-workspace-info).

```
docker build -t bonsai-python-sim:latest -f Dockerfile .
docker tag bonsai-python-sim:latest <ACR_REGISTRY_NAME>.azurecr.io/bonsai-python-sim:latest
docker push <ACR_REGISTRY_NAME>.azurecr.io/bonsai-python-sim:latest
bonsai simulator package container create --name bonsai-python-sim -u <ACR_REGISTRY_NAME>.azurecr.io/bonsai-python-sim:latest --max-instance-count 25 -r 1 -m 1 -p Linux
```

## Train a brain

```
bonsai brain create -n bonsai-python-sim
bonsai brain version update-inkling -f machine_teacher.ink -n bonsai-python-sim
bonsai brain version start-training -n bonsai-python-sim --simulator-package-name bonsai-python-sim
```
