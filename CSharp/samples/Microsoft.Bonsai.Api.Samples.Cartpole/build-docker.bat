@echo off
if [%1]==[] goto usage
if [%2]==[] goto usage
 
SET container_registry=%1
SET image_name=%2
SET version=latest

if [%3]==[] (
    SET version=latest
)
else (
    SET version=%3
)

ECHO Building image %image_name%

docker build -t %image_name%  .

ECHO Logging in to %container_registry%

cmd /c az acr login --name %container_registry%

ECHO Tagging %image_name% and pushing to %container_registry%.azurecr.io/%image_name%:%version%

docker tag %image_name% %container_registry%.azurecr.io/%image_name%:%version%
docker push %container_registry%.azurecr.io/%image_name%:%version%

ECHO Complete
exit /B 0

:usage
@echo Usage: %0 ^<container_registry_name^> ^<docker_image_name^> [^<version^>]
exit /B 1