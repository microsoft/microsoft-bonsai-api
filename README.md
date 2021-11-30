# Bonsai Platform API

This folder contains support libraries for connecting to the Bonsai Azure Service.

## Microsoft Open Source Code of Conduct

This repository is subject to the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct).

## Contributing Samples

Please read the Microsoft contributing [guidelines](CONTRIBUTING.md).

Submit a PR adding a brief description of the code you wish to be included and add an appropriate hyperlink to the sample code section. If the sample you wish to code is small and self contained it can be added to the samples directory for the language it is written. For example Python samples can be found in Python/samples.

## Sample Code

Samples that show how to use microsoft-bonsai-api and connect with the Bonsai platform.

### Python

[cartpole](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/cartpole) - Classic CartPole simulator in Python. Balancing an inverted pendulum on a moving cart.

[gym-highway](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/gym-highway) - Make decisions to speed up, slow down, change lanes, etc with a multi-lane highway. This sample uses arrays in Inkling for states and demonstrates usage of using an element of the array in the reward.

[house-energy](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/house-energy) - Control the temperature inside of a house according to the desired set temperatures just like a thermostat.

[microgrid](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/microgrid) - Control a local energy grid to meet the load by charging or discharging the battery, importing or exporting energy from the traditional grid, and consuming generated PV power.

[plastic-extrusion](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/plastic-extrusion) - Control a plastic extruder to optimize production of PVC rods with a specified length and tolerance.

[quanser-qube](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/quanser-qube) - Simulation of the real hardware, academic learning tool: Quanser Qube. Swing Up and Balancing an inverted pendulum with a rotary base.

[simple-adder](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/simple-adder) - A minimal working example of a Python simulator that can be connected to Bonsai and used to train a brain. You can think of it as Project Bonsai's "Hello World".

### C#

[cartpole](https://github.com/microsoft/microsoft-bonsai-api/tree/main/CSharp/samples/Microsoft.Bonsai.Api.Samples.Cartpole) - Classic CartPole simulator in C#. Balancing an inverted pendulum on a moving cart.

### Java

[cartpole](https://github.com/microsoft/cartpole-java) - Classic CartPole simulator in Java. Balancing an inverted pendulum on a moving cart.

### Typescript

[adder](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Typescript/samples/adder) - Simple simulator that adds numbers and computes a reward based on the result.

### Other Bonsai repositories

[bonsai-common](https://github.com/microsoft/bonsai-common) - A Python framework for interfacing with the bonsai platform.

[bonsai-sim-connector-template](https://github.com/microsoft/bonsai-sim-connector-template) - A template for creating Bonsai Connectors. It can serve as a starting point for making a simulation platform work with Bonsai.

[moabsim-py](https://github.com/microsoft/moabsim-py) - Simulator for balancing a ball on a plate, based on hardware. Tutorial 2 is meant for deployment. Additional Inkling samples can be found in `/Machine-Teaching-Examples`.

## Simulator Integration Checklist & Best Practices
- [ ] Make sure workspace is registered & correct.
- [ ] **Error handling**: Any cloud service can have transient errors and our SDK have Retry policy in place, but not all errors can be retried, so a good error handling logic will make your sim sessions more robust.
- [ ] **Enable logging**: If you are hitting issues. Enable logging in BonsaiClientConfig. And set the right LogLevel to get more information.
