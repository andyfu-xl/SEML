import os
import sys
import torch
import time
_ = [sys.path.insert(1, os.path.join(root, d)) for root, dirs, _ in os.walk(os.getcwd()) for d in dirs]

from modules.communicator.communicator import Communicator
from modules.dataparser.dataparser import DataParser
from modules.database import Database
from modules.preprocessor import Preprocessor
from modules.model import load_model, inference

def main():
    communicator = Communicator("localhost", 8440, 8441)
    dataparser = DataParser()
    database = Database()
    preprocessor = Preprocessor(database)
    model = load_model('./lstm_model.pth')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    iteration_timings = []
    while True:
        # Receive message
        start = time.time()
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
            has_aki = int(inference(model, preprocessed_message, device))

        # Page (if necessary)
        if has_aki:
            # print(f"ALERT: Patient {mrn} has AKI")
            communicator.page(mrn)

        # Acknowledge message
        communicator.acknowledge()
        end = time.time()
        execution_time = end - start
        iteration_timings.append(execution_time)
    
    print(f"Fastest iteration: {min(iteration_timings)}")
    print(f'Average iteration: {sum(iteration_timings) / len(iteration_timings)}')
    print(f"Slowest iteration: {max(iteration_timings)}")
if __name__ == "__main__":
    main()
