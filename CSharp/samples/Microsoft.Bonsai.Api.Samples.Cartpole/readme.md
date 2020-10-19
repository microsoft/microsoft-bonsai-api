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

Alternatively, you can use the `build-docker.bat` file to build, tag and push the container to your Azure container registry.

To run the container locally after it is built, run:

```
docker run --rm -it -e SIM_WORKSPACE="%SIM_WORKSPACE%" -e SIM_ACCESS_KEY="%SIM_ACCESS_KEY%" -e SIM_API_HOST="https://api.bons.ai"   csharp-cartpole
```

where 

- **%SIM_WORKSPACE%** either exists in your environment variables, or is your workspace ID
- **%SIM_ACCESS_KEY%** either exists in your environment variables, or is your access key
- **csharp-cartpole** is your docker image name

# Assessment
Assessment is run similar to training, except you run `Start Assessment` in the Bonsai UI instead of `Start Training`. 

# Prediction

After assessing and exporting your brain, you can use the same classes to run against the prediction endpoint, which defaults to http://localhost:5000/v1/prediction in the export instructions.

Run the command:

``` 
dotnet bin/Release/netcoreapp3.1/publish/Microsoft.Bonsai.Api.Samples.Cartpole.dll predict http://localhost:5000/v1/prediction
```