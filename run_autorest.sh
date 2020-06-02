autorest --input-file=Swagger/swagger.json --csharp --output-folder=CSharp --namespace=Microsoft.Bonsai.SimulatorApi 
autorest --input-file=Swagger/swagger.json --python --output-folder=Python --namespace=microsoft_bonsai_api.simulator --package-name=microsoft-bonsai-api --use=@autorest/python@5.0.0-preview.7
autorest --input-file=Swagger/swagger.json --java --output-folder=Java --namespace=Microsoft.Bonsai.SimulatorApi 
autorest --input-file=Swagger/swagger.json --typescript --output-folder=Typescript --namespace=Microsoft.Bonsai.SimulatorApi