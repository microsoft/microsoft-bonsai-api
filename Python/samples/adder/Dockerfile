# this is one of the cached base images available for ACI
FROM python:3.7.4

# Copy simulator files to /sim
COPY samples/adder/requirements.txt /bonsai/
COPY samples/adder/adder.py /bonsai/
COPY samples/adder/adder_description.json /bonsai/

# Use pip to install packaged dependencies.
WORKDIR /bonsai
RUN pip install -U pip
RUN pip install -r requirements.txt

# This will be the command to run the simulator
CMD ["python", "adder.py", "--verbose"]
