FROM ubuntu:jammy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3 python3-pip
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

# Copy Simulator
# COPY simulator.py /app/
# COPY simulator_test.py /app/
# WORKDIR /simulator
# RUN ./simulator_test.py

# Copy Model
COPY lstm_model_new.pth /app/
COPY main.py /app/
COPY integration_test.py /app/

# Copy Data
COPY data /app/data

# Copy Modules
COPY modules /app/modules

RUN chmod +x /app/main.py
EXPOSE 8440
EXPOSE 8441
WORKDIR /app/
CMD ./main.py --mllp=$MLLP_ADDRESS --pager=$PAGER_ADDRESS