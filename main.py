#!/usr/bin/env python3
import argparse
import torch
import logging

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
    parser.add_argument('--history', type=str, help="Path to the history CSV file", default="./data/coursework5-history.csv")
    parser.add_argument('--model', type=str, help="Path to the model file", default="./lstm_model.pth")
    parser.add_argument('--database', type=str, help="Path to the database .db file", default="./data/database.db")
    parser.add_argument('--log', type=str, help="Path to the logging file", default="./logs/error.log")
    flags = parser.parse_args()
    print("Flags:", flags)

    logging.basicConfig(filename=flags.log, level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    communicator = Communicator(flags.mllp, flags.pager)
    dataparser = DataParser()
    database = Database(flags.database)
    # database.load_csv(flags.history, flags.database)
    preprocessor = Preprocessor(database)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(flags.model).to(device)

    print("AKI detection system started.")

    while True:
        print("Waiting for message...")
        # Receive message
        message = communicator.receive()
        print(message)
        if message == None:
            print("No message received. Trying to reconnect...")
            communicator.connect()
            continue

        # Pass the message to data parser
        parsed_message = dataparser.parse_message(message)
        
        if parsed_message == None:
            print("Invalid message format. Skipping...")
            communicator.acknowledge()
            continue

        mrn = parsed_message.mrn
        timestamp = parsed_message.msg_timestamp

        # Process message
        preprocessed_message = preprocessor.preprocess(parsed_message)

        # Perform inference
        has_aki = False
        if preprocessed_message is not None:
            has_aki = inference(model, preprocessed_message.to(device))
        
        print(f"Patient {mrn} has AKI? {'Yes' if has_aki else 'No'}")
        # Page (if necessary)
        if has_aki:
            communicator.page(mrn, timestamp)
            database.paged(mrn)
            print(f"Patient {mrn} has been paged.")

        # Acknowledge message
        communicator.acknowledge()
        print("Message acknowledged.")

if __name__ == "__main__":
    main()
