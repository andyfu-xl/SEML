FROM ubuntu:jammy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3 python3-pip
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

# Copy Model
COPY lstm_model.pth /app/
COPY main.py /app/
COPY integration_test.py /app/

# Copy Data
COPY data /app/data
COPY data/database.db /data/database.db

# Copy Logs
COPY logs /app/logs

# Copy Modules
COPY modules /app/modules

RUN chmod +x /app/main.py
EXPOSE 8440
EXPOSE 8441
CMD /app/main.py --mllp=$MLLP_ADDRESS --pager=$PAGER_ADDRESS --history="/app/data/history.csv" --model="/app/lstm_model.pth" --database="/app/data/database.db" --log="/app/logs/error.log"