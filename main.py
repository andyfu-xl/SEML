#!/usr/bin/env python3
import argparse
import torch
import http
import logging
from prometheus_client import Counter, Gauge, start_http_server

from modules.communicator.communicator import Communicator
from modules.dataparser.dataparser import DataParser
from modules.database import Database
from modules.preprocessor import Preprocessor
from modules.model import load_model, inference

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

    # Messages metrics
    messages_received = Counter('messages_received', 'Number of messages received')
    null_messages = Counter('null_messages', 'Number of null messages received')
    invalid_messages = Counter('invalid_messages', 'Number of invalid messages received')
    num_blood_test_results = Counter('blood_test_messages', 'Number of blood test results received')

    # Connection metrics
    connection_attempts = Counter('connection_attempts', 'Number of connection attempts')
    page_failures = Counter('page_failures', 'Number of page failures')
    communicator_logs = {'connect': connection_attempts, 'page_failures': page_failures}

    # Prediction metrics
    sum_blood_test_results = Counter('sum_blood_test_results', 'Sum of blood test results')
    running_mean_blood_test_results = Gauge('running_mean_blood_test_results', 'Running mean of blood test results')
    positive_predictions = Counter('positive_predictions', 'Number of positive predictions')
    positive_prediction_rate = Gauge('positive_prediction_rate', 'Positive prediction rate')

    ### Main ###
    communicator = Communicator(flags.mllp, flags.pager, communicator_logs=communicator_logs)
    dataparser = DataParser()
    database = Database(flags.database)
    # database.load_csv(flags.history, flags.database)
    preprocessor = Preprocessor(database)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(flags.model).to(device)

    while True:
        # Receive message
        message = communicator.receive()
        messages_received.inc()
        if message == None:
            null_messages.inc()
            communicator.connect()
            continue

        # Pass the message to data parser
        parsed_message = dataparser.parse_message(message)
        
        if parsed_message == None:
            invalid_messages.inc()
            communicator.acknowledge()
            continue
        elif parsed_message.message_type == 'ORU^R01':
            num_blood_test_results.inc()
            sum_blood_test_results.inc(parsed_message.obx_value)
            running_mean_blood_test_results.set(sum_blood_test_results._value.get() / num_blood_test_results._value.get())

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

            positive_predictions.inc()
            positive_prediction_rate.set(positive_predictions._value.get() / num_blood_test_results._value.get())

        # Acknowledge message
        communicator.acknowledge()

if __name__ == "__main__":
    try:
        server, t = start_http_server(8000)
        main()
    finally:
        print("Server stopped")
        server.shutdown()
        t.join()
