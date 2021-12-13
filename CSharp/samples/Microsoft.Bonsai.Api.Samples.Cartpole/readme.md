# Cartpole C#

This example uses the Bonsai SDK for .NET Standard and is built using .NET Core 3.1. 

The inkling used for this example is the same that is found in the Bonsai Cartpole example in the portal.

# Publishing

This example ships with a default publish profile called FilePublisher that will push the output to `bin\Release\netcoreapp3.1\publish\`. If you change this location, you will also need to change the Dockerfile for the updated path.

See <a href="https://docs.microsoft.com/en-us/dotnet/core/tutorials/publishing-with-visual-studio#:~:text=%20Tutorial%3A%20Publish%20a%20.NET%20Core%20console%20application,default%2C%20the%20publishing%20process%20creates%20a...%20More%20">here</a> for assistance with publishing a .NET Core app.

# Training - Local
You can run the default debug profiler (F5) to start the application and then connect to the brain in the Bonsai UI.

# Training - Platform
After confirming functionality locally, you can then register the simulation with the platform as a managed simulator that can be scaled in a container. 

## Containerization

You can build the example container directly using the command:

```
docker build -t csharp-cartpole .
```

in the directory with the `Dockerfile`. 

Alternatively, you can use the `build-docker.bat` file to build, tag and push the container to your Azure Container Registry.

To run the container locally after it is built, run:

```
docker run --rm -it -e SIM_WORKSPACE="%SIM_WORKSPACE%" -e SIM_ACCESS_KEY="%SIM_ACCESS_KEY%" -e SIM_API_HOST="https://api.bons.ai"   csharp-cartpole
```

where 

- **%SIM_WORKSPACE%** either exists in your environment variables, or is your workspace ID
- **%SIM_ACCESS_KEY%** either exists in your environment variables, or is your access key
- **csharp-cartpole** is your docker image name

If you don't have Docker installed or you don't want to build it on your local machine first, you can use the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/) with the following command to build the provided Dockerfile that creates a simulator package directly on Azure Container Registry (note the trailing period!):

```azurecli
az acr build --image <IMAGE_NAME>:<IMAGE_VERSION> --file Dockerfile --registry <ACR_REGISTRY> .
```

`<IMAGE_NAME>:<IMAGE_VERSION>` could be e.g. `cartpole_csharp:v1`. You can look up `<ACR_REGISTRY>` in the workspace info in the Bonsai UI.

If you get an error like this:

```
The resource with name <ACR_REGISTRY_NAME> and type 'Microsoft.ContainerRegistry/registries' could not be found in subscription '<something>'
```

look up your subscription id in the workspace info in the Bonsai UI, and run 

```azurecli
az account set --subscription <SUBSCRIPTION_ID>
```

## Training

Once you've built the simulator package and pushed it to Azure Container Registry, you can use the Bonsai Web UI to import the simulator.

Go to your [workspace](https://preview.bons.ai/) and look for the `+ Add sim` button in the bottom left corner. Alternatively, you can use the [`bonsai-cli`](https://pypi.org/project/bonsai-cli/) to add the simulator with the [bonsai simulator package container create](https://docs.microsoft.com/en-us/bonsai/cli/simulator/package/add) command.

Finally, use the Inkling code from `machine-teaching.ink` to train a brain using the simulator package created above. Be sure to add the package name to `source simulator{}` in your training concept graph on line 46.


# Assessment
To assess your brain during or after training is complete, click "New assessment" on the `Train` tab in the Bonsai Web UI t create a new custom assessment. Alternatively, you can use the `bonsai-cli` to [start an assessment](https://docs.microsoft.com/en-us/bonsai/cli/brain/version/assessment/start).

# Prediction

After assessing and exporting your brain, you can use the same classes to run against the prediction endpoint, which defaults to http://localhost:5000/v1/prediction in the export instructions.

Run the command:

``` 
dotnet bin/Release/netcoreapp3.1/publish/Microsoft.Bonsai.Api.Samples.Cartpole.dll predict http://localhost:5000/v1/prediction
```