#!/usr/bin/env python3
import argparse
import torch
import time
from modules.communicator.communicator import Communicator
from modules.dataparser.dataparser import DataParser
from modules.database import Database
from modules.preprocessor import Preprocessor
from modules.model import load_model, inference

def main():
    print("Starting AKI detection system...")
    parser = argparse.ArgumentParser()
    parser.add_argument('--mllp', type=str, help="Address to receive HL7 messages via MLLP")
    parser.add_argument('--pager', type=str, help="Address to page requests via HTTP")
    parser.add_argument('--history', type=str, help="Path to the history CSV file", default="./data/history.csv")
    parser.add_argument('--model', type=str, help="Path to the model file", default="./lstm_model.pth")
    parser.add_argument('--database', type=str, help="Path to the database .db file", default="./data/database.sqlite")
    flags = parser.parse_args()
    print("Flags:", flags)

    communicator = Communicator(flags.mllp, flags.pager)
    dataparser = DataParser()
    database = Database(flags.database)
    database.load_csv(flags.history, flags.database)
    preprocessor = Preprocessor(database)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(flags.model).to(device)

    print("AKI detection system started.")

    while True:
        print("Waiting for message...")
        # Receive message
        # start_time = time.time()
        message = communicator.receive()
        print(message)
        if message == None:
            print("No message received. Exiting...")
            communicator.close()
            break

        # Pass the message to data parser
        parsed_message = dataparser.parse_message(message)
        
        if parsed_message == None:
            print("Invalid message format. Skipping...")
            communicator.acknowledge()
            continue

        mrn = parsed_message.mrn

        # Process message
        preprocessed_message = preprocessor.preprocess(parsed_message)

        # Perform inference
        has_aki = False
        if preprocessed_message is not None:
            has_aki = inference(model, preprocessed_message.to(device))
        # Page (if necessary)
        if has_aki:
            communicator.page(mrn)
            database.paged(mrn)
        # Acknowledge message
        communicator.acknowledge()
        # runtime = time.time() - start_time
        # if runtime >= 3:
        # print(f"Processed message for MRN {mrn} in {runtime:.2f} seconds")

if __name__ == "__main__":
    main()
