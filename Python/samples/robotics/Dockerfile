# this is one of the cached base images available for ACI
FROM python:3.7.4

# Install libraries and dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential \
  cmake \
  zlib1g-dev \
  curl \
  swig

# Additional build tools
RUN apt-get update -q \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y \
  libgl1-mesa-dev \
  libgl1-mesa-glx \
  libglew-dev \
  libosmesa6-dev \
  software-properties-common \
  net-tools \
  xpra \
  xserver-xorg-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# patchelf
RUN curl -o /usr/local/bin/patchelf https://s3-us-west-2.amazonaws.com/openai-sci-artifacts/manual-builds/patchelf_0.9_amd64.elf \
  && chmod +x /usr/local/bin/patchelf

# Set up the simulator
WORKDIR /src

# Copy simulator files to /src
COPY . /src

# install MuJoCo
RUN mkdir -p /root/.mujoco \
  && wget https://www.roboti.us/download/mujoco200_linux.zip -O mujoco.zip \
  && unzip mujoco.zip -d /root/.mujoco \
  && mv /root/.mujoco/mujoco200_linux /root/.mujoco/mujoco200 \
  && rm mujoco.zip

RUN wget -O /root/.mujoco/mjkey.txt https://www.roboti.us/mjkey.txt
ENV LD_LIBRARY_PATH /root/.mujoco/mujoco200/bin:${LD_LIBRARY_PATH}


# Install simulator dependencies
RUN pip3 install -r requirements.txt


# This will be the command to run the simulator
CMD ["python3", "fetch.py"]

# This command runs the simulator with a 3s delay + uniform variance +/-1
#CMD ["python3", "main.py", "--sim-speed", "3", "--sim-speed-variance", "1"]