# Base this container on the Python slim container image available from ACI.
# See Image Variants at https://hub.docker.com/_/python for information about different flavors of Python containers.
FROM python:3.7.4-slim

# Set up the simulator
WORKDIR /src

# Copy simulator files to /src
COPY . /src

# Install simulator dependencies
RUN pip3 install -e .

WORKDIR /src/samples/simple-adder

# This will be the command to run the simulator
CMD ["python3", "main_noprint.py"]
