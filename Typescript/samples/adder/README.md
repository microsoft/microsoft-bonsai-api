# Adder sample using microsoft-bonsai-api
A simple adder sim written using the microsoft-bonsai-api typescript sdk

## Requirements
- Node
- Install microsoft-bonsai-api (only available locally at the moment). You'll need to clone the entire typescript sdk until it is released.

## How to run
The following assumes you've cloned the typescript sdk and are in the Typescript/src/samples/adder directory. Workspace and accesskey must be set before running the simulator. The following options are available to you for setting workspace and accesskey

1. Environment Variables - SIM_WORKSPACE and SIM_ACCESS_KEY
2. Pass in cli args
3. Set workspace and access key in BonsaiClientConfig constructor

Running after setting env vars or setting in BonsaiClientConfig constructor
```
(cd ../../lib/ && npm run build) && npm i && tsc && node dist/adder.js
```

Running using cli args.
```
(cd ../../lib/ && npm run build) && npm i && tsc && node dist/adder.js --workspace=<WORKSPACE> --accesskey=<ACCESSKEY>
```

## Common issues
- (node:76785) UnhandledPromiseRejectionWarning - Check and make sure your bonsai config is using the correct workspace and accesskey.
- Type information not available in VSCode - Try deleting node modules and reinstalling.

## TODOs
- Update docs when microsoft-bonsai-api is available on npm