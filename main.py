import os
import sys
import csv
import torch
_ = [sys.path.insert(1, os.path.join(root, d)) for root, dirs, _ in os.walk(os.getcwd()) for d in dirs]

from modules.communicator.communicator import Communicator
from modules.dataparser.dataparser import DataParser
from modules.database import Database
from modules.preprocessor import Preprocessor
from modules.model import load_model, inference, save_inference_results

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    communicator = Communicator("localhost", 8440, 8441)
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
            print(f"ALERT: Patient {mrn} has AKI")
            communicator.page(mrn)
            database.paged(mrn)

        # Acknowledge message
        communicator.acknowledge()


if __name__ == "__main__":
    main()
