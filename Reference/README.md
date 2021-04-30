# Simulator interface schema reference materials

This folder contains the [JSON schema](http://json-schema.org/) for the JSON format of the simulator descriptions supported by the Microsoft Bonsai Simulator API.

When a simulator registers with the Bonsai service, it has the option to pass a description parameter that defines the state, action, and config datatypes supported by the simulator. If this information is supplied, brains created from the simulator will automatically generate Inkling structures that are compatible with the simulator.

[simtypes-example.json](simtypes-example.json) contains examples of specifying different variable types. For a complete example, see [the schema for cartpole](../Python/samples/cartpole/cartpole_description.json).

Editors like Visual Studio Code can be set up to validate a description JSON file with respects to a schema.