autorest --input-file=Swagger/swagger_swashbuckle.json --csharp --output-folder=Swashbuckle/CSharp --namespace=Bonsai.SimulatorApi
autorest --input-file=Swagger/swagger_swashbuckle.json --python --output-folder=Swashbuckle/Python --namespace=Bonsai.SimulatorApi --package-name=Bonsai.SimulatorApi
autorest --input-file=Swagger/swagger_swashbuckle.json --java --output-folder=Swashbuckle/Java --namespace=Bonsai.SimulatorApi 
autorest --input-file=Swagger/swagger_swashbuckle.json --typescript --output-folder=Swashbuckle/Typescript --namespace=Bonsai.SimulatorApi