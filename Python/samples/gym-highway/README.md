# Gym Highway Multi-Lesson

## Objective

Demonstrate how curriculum learning with multiple lessons can benefit as a Machine Teaching strategy. An agent must drive on a high way with multiple lanes, trying to reach a high speed without collisions with other vehicles. Increasing the number of lanes and cars makes the problem more difficult.

![](https://raw.githubusercontent.com/eleurent/highway-env/gh-media/docs/media/highway.gif)

## Action

| Action | Discrete |  Description  |
| ------ | ---------------- | ------- |
| steer     | [0, 1, 2, 3, 4]    |  0: 'LANE_LEFT', 1: 'IDLE', 2: 'LANE_RIGHT '3: 'FASTER', 4: 'SLOWER' |

## States

| State     | Type     | Description                                             |
| --------- | --------- | ------------------------------------------------------- |
| vehicle1     | array[6]     | ["x", "y", "vx", "vy", "cos_h", "cos_y"] for ego vehicle     |
| vehicle2     | array[6]     | ["x", "y", "vx", "vy", "cos_h", "cos_y"] for nearest vehicle     |
| vehicle3     | array[6]     | ["x", "y", "vx", "vy", "cos_h", "cos_y"] for nearest vehicle     |
| vehicle4     | array[6]     | ["x", "y", "vx", "vy", "cos_h", "cos_y"] for nearest vehicle     |
| vehicle5     | array[6]     | ["x", "y", "vx", "vy", "cos_h", "cos_y"] for nearest vehicle     |

## Terminal Conditions

- Colliding with another vehicle

## Configuration Parameters

| Configuration     | Type     | Description                                             |
| --------- | --------- | ------------------------------------------------------- |
| vehicles_count     | [int]     | Number of vehicles on the road                 |
| lane_count     | [int]     | Number of lanes                  |

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
    --simulator-name highway-v0
```

Optionally, run the simulator locally with a visualization:

```bash
python main.py --render
```

## Evaluation

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