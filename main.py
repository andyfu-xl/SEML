#!/usr/bin/env python3
import argparse
import torch

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
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model('./lstm_model.pth').to(device)

    while True:
        # Receive message
        message = communicator.receive()
        if message == None:
            communicator.close()
            break

        # Pass the message to data parser
        parsed_message = dataparser.parse_message(message)
        
        mrn = parsed_message.mrn

        # Process message
        preprocessed_message = preprocessor.preprocess(parsed_message)

        # Perform inference
        has_aki = False
        if preprocessed_message is not None:
            has_aki = int(inference(model, preprocessed_message.to(device)))
        
        # Page (if necessary)
        if has_aki:
            communicator.page(mrn)
            database.paged(mrn)

        # Acknowledge message
        communicator.acknowledge()

if __name__ == "__main__":
    main()
