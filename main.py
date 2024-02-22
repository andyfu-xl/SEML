#!/usr/bin/env python3
import argparse
import torch
import http
import logging

from modules.communicator.communicator import Communicator
from modules.dataparser.dataparser import DataParser
from modules.database import Database
from modules.preprocessor import Preprocessor
from modules.model import load_model, inference
from modules.metrics_monitoring import start_monitoring, message_metrics, communicator_metrics, prediction_metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mllp', type=str, help="Address to receive HL7 messages via MLLP")
    parser.add_argument('--pager', type=str, help="Address to page requests via HTTP")
    parser.add_argument('--history', type=str, help="Path to the history CSV file", default="./data/coursework5-history.csv")
    parser.add_argument('--model', type=str, help="Path to the model file", default="./lstm_model.pth")
    parser.add_argument('--database', type=str, help="Path to the database .db file", default="./data/database.db")
    parser.add_argument('--log', type=str, help="Path to the logging file", default="./logs/error.log")
    flags = parser.parse_args()

    ### Metrics ###
    logging.basicConfig(filename=flags.log, level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ### Main ###
    communicator = Communicator(flags.mllp, flags.pager, communicator_logs=communicator_metrics)
    dataparser = DataParser()
    database = Database(flags.database)
    # database.load_csv(flags.history, flags.database)
    preprocessor = Preprocessor(database)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(flags.model).to(device)

    while True:
        # Receive message
        message = communicator.receive()
        message_metrics['message_received'].inc()
        if message == None:
            message_metrics['null_messages'].inc()
            communicator.connect()
            continue

        # Pass the message to data parser
        parsed_message = dataparser.parse_message(message)
        
        if parsed_message == None:
            message_metrics['invalid_messages'].inc()
            communicator.acknowledge()
            continue
        elif parsed_message.message_type == 'ORU^R01':
            message_metrics['num_blood_test_results'].inc()
            prediction_metrics['sum_blood_test_results'].inc(parsed_message.obx_value)
            prediction_metrics['running_mean_blood_test_results'].set(prediction_metrics['sum_blood_test_results']._value.get() 
                                                                      / message_metrics['num_blood_test_results']._value.get())

        mrn = parsed_message.mrn
        timestamp = parsed_message.msg_timestamp

        # Process message
        preprocessed_message = preprocessor.preprocess(parsed_message)

        # Perform inference
        has_aki = False
        if preprocessed_message is not None:
            has_aki = inference(model, preprocessed_message.to(device))
        
        # Page (if necessary)
        if has_aki:
            database.paged(mrn)
            communicator.page(mrn, timestamp)

            prediction_metrics['positive_predictions'].inc()
            prediction_metrics['positive_prediction_rate'].set(prediction_metrics['positive_predictions']._value.get() 
                                                                / message_metrics['num_blood_test_results']._value.get())

        # Acknowledge message
        communicator.acknowledge()

if __name__ == "__main__":
    try:
        server, t = start_monitoring()
        main()
    finally:
        print("Server stopped")
        server.shutdown()
        t.join()
