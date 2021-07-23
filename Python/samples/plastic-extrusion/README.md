# Plastic Extrusion Demo

## Overview

![Components of a plastic extruder](https://upload.wikimedia.org/wikipedia/commons/1/18/Extruder_section.jpg)

(Diagram reproduced from [Wikipedia's *Extrusion*](https://en.wikipedia.org/wiki/Extrusion) article.)

The plastic extrusion process has several key components:

- the *hopper*, which feeds plastic material (e.g. pellets) into the barrel;
- the rotating *screw*, which agitates and melts the plastic and pushes it through the die;
- the *die*, which determines the shape of the extruded material; and
- the *cutter* (not pictured), which slices the extruded material into sections.

[Polyvinyl chloride](https://en.wikipedia.org/wiki/Polyvinyl_chloride) (PVC) is the third most commonly produced synthetic plastic polymer and has many applications, including vinyl records and the ubiquitous pipe tubing.

In this demo, we train a deep reinforcement learning system to optimize production of PVC rods with a specified length and tolerance.

A trained Bonsai brain can make continuous adjustments to optimize product quality and throughput.  Brains are also more flexible and can deal with random fluctuations (see simulation details) and system drift.  This provides significant advantages over busy human operators and traditional PID or MPC control systems.

## Quickstart / Setup Guide

### Installation Requirements

- Access to a Bonsai workspace (see [Microsoft account setup for Bonsai](https://docs.microsoft.com/en-us/bonsai/guides/account-setup)), including [workspace ID](https://docs.microsoft.com/en-us/bonsai/cookbook/get-workspace-info) and [access key](https://docs.microsoft.com/en-us/bonsai/cookbook/get-access-key)

- Python 3.7+

- [Bonsai API](https://github.com/microsoft/microsoft-bonsai-api)
- [Bonsai CLI](https://docs.microsoft.com/en-us/bonsai/cli/)

Note: installing the Bonsai API, CLI, and supporting packages in a virtual environment, e.g. with `conda` or `virtualenv`, is strongly recommended.

### Running the Simulator Locally

1. Clone the repo to your local machine.
2. Create a new `.env` file in the root of the repo and add your workspace credentials.  See `template.env` for an example.
3. Run `python main.py`.

You can now create and train a new brain with the Bonsai web interface or the CLI using the locally running simulator.

### Building the Simulator Image

Local simulations can only run a single simulation instance for brain training.  To scale up the simulation, we will need to package it into a Docker container.

Creating a Bonsai workspace automatically provisions an Azure Container Registry (ACR) instance.

```sh
az acr login --name $RegistryName

az acr build \
    --image $ImageName \
    --registry $RegistryName \
    --file Dockerfile .

bonsai simulator package container create \
    --name $SimulatorName \
    --image-uri "$RegistryName.azurecr.io/$ImageName" \
    --instance-count 25 \
    --max-instance-count 25 \
    --cores-per-instance 1 \
    --memory-in-gb-per-instance 1 \
    --os-type Linux
```

- `$RegistryName` is the name of your ACR instance,
- `$ImageName` is the name and tag of your container image, e.g. `extrusion:v1`, and
- `$SimulatorName` is the name of your simulator in the Bonsai workspace.

Note: On PowerShell, replace the backslash ("\\") with a backtick ("`").

### Brain Training

Now that the simulator is connected to the Bonsai platform, we can use it to train a brain.  First, create a new brain with the UI or the CLI.

```sh
bonsai brain create --name $BrainName
```

Next, upload the Inkling file (either `single.ink` for the single concept version, or `multi.ink` for the multi-concept version).

```sh
bonsai brain version update-inkling \
    --name $BrainName \
    --file $InklingFile
```

Finally, start a brain training session.

```sh
bonsai brain version start-training \
    --name $BrainName \
    --simulator-package-name $SimulatorName
```

Note: when training multiconcept brains, you'll also need to specify the concept with `--concept-name $ConceptName`.

## Keywords

Extruder, barrel, screw, die, cutter, manufacturing processes, throughput, yield, rheology, non-Newtonian flow, flow rate, shear rate, viscosity, power law, temperature.

## Simulation Overview

To a first order approximation, the material throughput is directly proportional to screw speed.  This makes intuitive sense: the faster the screw turns in the barrel, the more material it can push through the system.

Similarly, for a given throughput and product cross section, the part length is inversely proportional to cutter frequency.  The less often the cutter slices the material, the more material passes the cutter before it is sliced.  This naturally results in a longer product length.

See the [model docs](docs/model.md) for the full details.

## Brain Design

### Control Actions

- Screw angular speed
- Cutter frequency

### Environment States

- Temperature
- Flow rate
- Product length
- Manufacturing yield

### Concept Design - Optimize Length

For a single concept (i.e. monolithic) brain design, we'll teach the brain to optimize the product length.  For this example, the desired product length is 1 foot, with a tolerance of 0.1 inches.

The `drive` statement instructs the brain to reach the desired state (the product length within tolerance) and stay there.  The `within` statement adds an additional requirement that the desired state be reached in the given number of iterations.  Since our simulation time step is 1 second, the brain must reach the desired state in 2 minutes or less for the episode to be successful.

```text
drive LengthWithinTolerance:
    State.product_length
    in Goal.Range(LengthTarget - LengthTolerance, LengthTarget + LengthTolerance)
    within 2 * 60
```

### Lesson Design

The example curriculum has 3 lessons, each with random values for initial parameters.

The first lesson trains the brain over a narrow range of initial screw angular speeds (34-37 RPM) and commensurate initial cutter frequencies.

The subsequent lessons widen the range of initial screw angular speeds by a factor of 5.

### Concept Design - Optimize Yield

Parts with the desired length can be produced by a range of screw angular speeds and cutter frequencies.  However, the production rate will vary depending on the screw speed.  We can add a second concept to teach the brain to also optimize the manufacturing yield.

The optimize yield concept adds 2 additional goals:

1) *keep the screw angular speed within 30-40 RPM* (the industry-standard rule of thumb for maintaining material quality of rigid PVC extrudate), and
2) *maximize manufacturing yield*, i.e. the number of "good" parts per iteration, where good is defined as within the given tolerance for product length.

## Brain Training Results

Training the *Optimize Length* concept at the provided settings takes about an hour, and training the *Optimize Yield* concept takes around 90 minutes.  At this point the first 2 lessons (*RandomizeStartNarrow* and *RandomizeStartMedium*) should have achieved 100% goal satisfaction, and the final lesson (*RandomizeStartWide*) should have achieved near-100% goal satisfaction.

## References

See [References](./docs/references.md) for details.

## Acknowledgements

Many thanks to the following people for helpful comments and suggestions throughout the development of this demo:

- Kence Anderson (Microsoft)
- David Coe (Microsoft)
- Doc Derwin (Neal Analytics)
- Olivier Fontana (Neal Analytics)
- Chris Kahrs (Microsoft)
- Irena Lusnyakyan (Microsoft)
- Victor Shnayder (Microsoft)
- Zach Perkel (Neal Analytics)
- Ryan Ratcliffe (Neal Analytics)
- Jayson Stemmler (Neal Analytics)
- Edwin Webster (Neal Analytics)
