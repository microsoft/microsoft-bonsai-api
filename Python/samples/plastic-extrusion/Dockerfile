# this is one of the cached base images available for ACI
FROM python:3.7.4

# Install libraries and dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential \
  cmake \
  zlib1g-dev \
  swig

# Copy project files
WORKDIR /src
COPY . /src

# Install simulator dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Run the simulator
CMD ["python3", "main.py"]
