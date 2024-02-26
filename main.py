#!/usr/bin/env python3
import argparse
import torch
import http
import logging

from modules.communicator import Communicator
from modules.dataparser import DataParser
from modules.database import Database
from modules.preprocessor import Preprocessor
from modules.model import load_model, inference
from modules.module_logging import main_logger, set_log_path
import modules.metrics_monitoring as monitoring

import signal
import sys

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mllp', type=str, help="Address to receive HL7 messages via MLLP")
    parser.add_argument('--pager', type=str, help="Address to page requests via HTTP")
    parser.add_argument('--history', type=str, help="Path to the history CSV file", default="./data/coursework5-history.csv")
    parser.add_argument('--model', type=str, help="Path to the model file", default="./lstm_model.pth")
    parser.add_argument('--database', type=str, help="Path to the database .db file", default="./data/database.db")
    parser.add_argument('--logs', type=str, help="Path to the log files", default="/app/data/logs")
    flags = parser.parse_args()

    return flags

def main(communicator: Communicator, database: Database, dataparser: DataParser, preprocessor: Preprocessor, flags):

    ### Metrics ###
    main_logger('INFO', 'Server started')
    monitoring.increase_num_of_startup()
    ### Main ###
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(flags.model).to(device)

    ## settle the positives but not paged mrn in the database
    mrns_times = database.settle_positives()
    for mrn, timestamp in mrns_times:
        communicator.page_queue.append((mrn, timestamp))
    while communicator.page_queue:
        mrn, timestamp = communicator.page_queue.pop()
        r = communicator.page(mrn, timestamp)
        if r is not None and r.status == http.HTTPStatus.OK:
            database.paged(mrn)
            monitoring.increase_positive_predictions()
            monitoring.update_positive_prediction_rate()
        else:
            communicator.page_queue.appendleft((mrn, timestamp))
            break

    ## start the server
    while True:
        # Receive message
        message = communicator.receive()
        monitoring.increase_message_received()
        if message == None:
            monitoring.increase_null_messages()
            communicator.connect()
            continue

        # Pass the message to data parser
        parsed_message = dataparser.parse_message(message)
        
        if parsed_message == None:
            monitoring.increase_invalid_messages()
            communicator.acknowledge(accept=False)
            continue
        elif parsed_message.message_type == 'ORU^R01':
            monitoring.increase_blood_test_messages()
            monitoring.increase_sum_blood_test_results(parsed_message.obx_value)
            monitoring.update_running_mean_blood_test_results()

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
            database.is_positive(mrn, timestamp)
            communicator.page_queue.append((mrn, timestamp))
            while communicator.page_queue:
                mrn, timestamp = communicator.page_queue.pop()
                r = communicator.page(mrn, timestamp)
                if r is not None and r.status == http.HTTPStatus.OK:
                    database.paged(mrn)
                    monitoring.increase_positive_predictions()
                    # monitoring.update_positive_prediction_rate()
                else:
                    communicator.page_queue.appendleft((mrn, timestamp))
                    break

        # Acknowledge message
        communicator.acknowledge(accept=True)

def signal_handler(signum, frame):
    main_logger('INFO', 'SIGTERM received, gracefully shutting down')
    monitoring.increase_num_of_shutdown()
    database.close()
    communicator.close()
    # Perform any necessary cleanup here
    # save last received message
    # add log and output metrics
    sys.exit(0)

if __name__ == "__main__":
    # MAIN_LOG = '/logs/main.log'

    try:
        server, t = monitoring.start_monitoring()
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        flags = get_arguments()
        set_log_path(flags.logs)
        communicator = Communicator(flags.mllp, flags.pager)
        database = Database(flags.database, flags.history)
        dataparser = DataParser()
        preprocessor = Preprocessor(database)
        main(communicator, database, dataparser, preprocessor, flags)
    finally:
        server.shutdown()
        t.join()
