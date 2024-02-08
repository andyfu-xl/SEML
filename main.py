#!/usr/bin/env python3
import os
import sys
import csv
import torch
import argparse
# _ = [sys.path.insert(1, os.path.join(root, d)) for root, dirs, _ in os.walk(os.getcwd()) for d in dirs]

from modules.communicator.communicator import Communicator
from modules.dataparser.dataparser import DataParser
from modules.database import Database
from modules.preprocessor import Preprocessor
from modules.model import load_model, inference

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mllp', type=str, help="Port on which to receive HL7 messages via MLLP")
    parser.add_argument('--pager', type=str, help="Port on which to page requests via HTTP")
    flags = parser.parse_args()

    communicator = Communicator(flags.mllp, flags.pager)
    dataparser = DataParser()
    database = Database()
    database.load_csv('./data/history.csv')
    preprocessor = Preprocessor(database)
    model = load_model('./lstm_model_new.pth')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    
    mrn_aki = []
    date_aki = []
    while True:
        # Receive message
        message = communicator.receive()
        if message == None:
            # save_inference_results(mrn_aki, date_aki, "./data/mrn_aki.csv")
            communicator.acknowledge()
            break

        # Pass the message to data parser
        parsed_message = dataparser.parse_message(message)
        mrn = parsed_message.mrn
        if parsed_message.message_type == 'ORU^R01':
            date = parsed_message.obr_timestamp

        # Process message
        preprocessed_message = preprocessor.preprocess(parsed_message)

        # Perform inference
        has_aki = False
        if preprocessed_message is not None:
            has_aki = int(inference(model, preprocessed_message.to(device)))

        # Page (if necessary)
        if has_aki:
            # print(f"ALERT: Patient {mrn} has AKI")
            communicator.page(mrn)
            # mrn_aki.append(mrn)
            # date_aki.append(date)

        # Acknowledge message
        communicator.acknowledge()

def save_inference_results(pred_labels, dates, output_path):
    print("Saving the inference results...")
    w = csv.writer(open(output_path, "w"))
    w.writerow(("mrn","date"))
    for i in range(len(pred_labels)):	
        w.writerow([pred_labels[i], dates[i]])
    print("The inference results have been saved to", output_path)

if __name__ == "__main__":
    main()
