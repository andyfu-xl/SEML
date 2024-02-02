FROM ubuntu:jammy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3
CMD docker pull mysql
CMD docker run --name mysql-server -e MYSQL_ROOT_PASSWORD=password -d -p 127.0.0.1:3306:3306 mysql:tag
# COPY simulator.py /simulator/
# COPY simulator_test.py /simulator/
# WORKDIR /simulator
# RUN ./simulator_test.py
# COPY messages.mllp /data/
# EXPOSE 8440
# EXPOSE 8441
COPY docker.py /docker/
CMD /docker/docker.py
# CMD /simulator/simulator.py --messages=/data/messages.mllp