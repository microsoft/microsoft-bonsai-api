# this is one of the cached base images available for ACI
FROM python:3.7.4

# Set up the simulator
WORKDIR /src

# Copy simulator files to /src
COPY . /src

# Install simulator dependencies
RUN pip3 install -r requirements.txt

# This will be the command to run the simulator
CMD ["python3", "main.py"]
