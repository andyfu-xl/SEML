FROM ubuntu:jammy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3
COPY modules/simulator.py /simulator/
COPY modules/simulator_test.py /simulator/
WORKDIR /simulator
# RUN ./simulator_test.py
COPY data/messages.mllp /data/
EXPOSE 8440
EXPOSE 8441
CMD /simulator/simulator.py --messages=/data/messages.mllp
CMD python main.py