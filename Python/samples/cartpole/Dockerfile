# this is one of the cached base images available for ACI
FROM python:3.7.4

# Install libraries and dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential \
  cmake \
  zlib1g-dev \
  swig

# Set up the simulator
WORKDIR /src

# Copy simulator files to /src
COPY . /src

# Install simulator dependencies
RUN pip3 install -r requirements.txt

# This will be the command to run the simulator
CMD ["python3", "main.py"]

# This command runs the simulator with a 3s delay + uniform variance +/-1
#CMD ["python3", "main.py", "--sim-speed", "3", "--sim-speed-variance", "1"]