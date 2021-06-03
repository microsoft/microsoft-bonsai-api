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

[bonsai-common](https://github.com/microsoft/bonsai-common) - A python framework for interfacing with the bonsai platform.

[cartpole](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/cartpole) - Classic CartPole simulator in Python. Balancing an inverted pendulum on a moving cart.

[house-energy](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/house-energy) - Control the temperature inside of a house according to the desired set temperatures just like a thermostat.

[quanser-qube](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/quanser-qube) - Simulation of the real hardware, academic learning tool: Quanser Qube. Swing Up and Balancing an inverted pendulum with a rotary base.

[house-energy](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/house-energy) - Simulator for controlling the temperature inside of a house to a desired temperatures, just like a thermostat.

[highway-env](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Python/samples/gym-highway) - Make decisions to speed up, slow down, change lanes, etc with a multi-lane highway. This sample uses arrays in Inkling for states and demonstrates usage of using an element of the array in the reward.

### C#

[cartpole](https://github.com/microsoft/microsoft-bonsai-api/tree/main/CSharp/samples/Microsoft.Bonsai.Api.Samples.Cartpole) - Classic CartPole simulator in C#. Balancing an inverted pendulum on a moving cart.

### Java

[cartpole](https://github.com/microsoft/cartpole-java) - Classic CartPole simulator in Java. Balancing an inverted pendulum on a moving cart.

### Typescript

[adder](https://github.com/microsoft/microsoft-bonsai-api/tree/main/Typescript/samples/adder) - Simple simulator that adds numbers and computes a reward based on the result.

## Simulator Integration Checklist & Best Practices
- [ ] Make sure workspace is registered & correct.
- [ ] **Error handling**: Any cloud service can have transient errors and our SDK have Retry policy in place, but not all errors can be retried, so a good error handling logic will make your sim sessions more robust.
- [ ] **Enable logging**: If you are hitting issues. Enable logging in BonsaiClientConfig. And set the right LogLevel to get more information.
