import os
import sys
import torch
_ = [sys.path.insert(1, os.path.join(root, d)) for root, dirs, _ in os.walk(os.getcwd()) for d in dirs]

from modules.communicator.communicator import Communicator
from modules.dataparser.dataparser import DataParser
from modules.database import Database
from modules.preprocessor import Preprocessor
from modules.model import LSTMModel
from modules.model_utils import inference

def main():
    communicator = Communicator("localhost", 8440)
    dataparser = DataParser()
    database = Database()
    preprocessor = Preprocessor(database)
    model = LSTMModel(input_dim=4, hidden_dim=64, output_dim=2, num_layers=2, model_path="./lstm_model.pth")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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
        if preprocessed_message is not None:
            has_aki = int(inference(model, preprocessed_message, device))

        # Page (if necessary)
        if has_aki:
            communicator.page(mrn)

        # Acknowledge message
        communicator.acknowledge()

if __name__ == "__main__":
    main()
