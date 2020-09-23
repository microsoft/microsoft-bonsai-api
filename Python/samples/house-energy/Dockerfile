FROM python:3.7.4

# Install libraries and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install libraries and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends

# Set up the simulator
WORKDIR /src

# Copy simulator files to /src
COPY . /src

# Install simulator dependencies
RUN pip3 install -r requirements.txt

# # This will be the command to run the simulator
CMD ["python3", "main.py"]