# SEML_CW3

## AKI Detection for Southside Hospital

## Introduction
This repository contains the codebase for a system designed to detect Acute Kidney Injury (AKI) using a Long Short-Term Memory (LSTM) model. AKI is a critical condition that requires timely detection for effective treatment and management. The LSTM model implemented here aims to predict the onset of AKI based on relevant patient data.

## Installation
To set up the system locally, follow these steps:
```
git clone git@gitlab.doc.ic.ac.uk:af723/seml_cw3.git
```
CD into the project directory and build the docker image
```
docker build -t [YOUR_IMAGE_NAME] .
```

In the project directory, to run the simulator. simulator.py should be listening to port 8440 and port 8441 if no explicit ports are provided.
This runs the simulator on your local machine
```
python simulator.py --messages=data/messages.mllp
```

To run the AKI detection system as a Docker Container
```
docker run -it --env MLLP_ADDRESS=host.docker.internal:8440 --env PAGER_ADDRESS=host.docker.internal:8441 [YOUR_IMAGE_NAME]
```

## Authors
This project is created for Imperial College London COMP70102: Software Engineering for Machine Learning. 
The Authors are: 
* Bao Zi Yuan, Lance
* Andy Fu
* Esmanda Wong
* Lee Penn Han
