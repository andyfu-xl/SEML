import os
import sys
import csv
import time
import http
import torch
import unittest
import subprocess
import urllib.error
import urllib.request
[sys.path.insert(1, os.path.join(root, d)) for root, dirs, _ in os.walk(os.getcwd()) for d in dirs]

from modules.communicator.communicator import Communicator
from modules.dataparser.dataparser import DataParser
from modules.preprocessor import Preprocessor
from modules.database import Database
from modules.model import inference, load_model, save_inference_results
from simulator_test import ADT_A01, ADT_A03, ORU_R01, TEST_MLLP_PORT, TEST_PAGER_PORT, wait_until_healthy, from_mllp, to_mllp

class SystemIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.ADT_A01_db_entry = {
            "dob": "1984-02-03",
            "gender": 1,
            "last_test": None,
            "name": "ELIZABETH HOLMES",
            "test_results": []
        }
        self.ORU_R01_db_entry = {
            "dob": "1984-02-03",
            "gender": 1,
            "last_test": '2024-01-20 22:04:03',
            "name": "ELIZABETH HOLMES",
            "test_results": [0, 103.4]
        }

        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        relative_path = "data/test_messages.mllp"
        test_mllp_messages_filepath = os.path.join(self.current_directory, relative_path)
        simulator_filepath = os.path.join(self.current_directory, "simulator.py")
        self.simulator = subprocess.Popen([
            simulator_filepath,
            f"--mllp={TEST_MLLP_PORT}",
            f"--pager={TEST_PAGER_PORT}",
            f"--messages={test_mllp_messages_filepath}"
        ])
        self.assertTrue(wait_until_healthy(self.simulator, f"localhost:{TEST_PAGER_PORT}"))

    # Test integration between Communicator and Simulator
    def test_integration_receive_all_messages_with_ack(self):
        messages = []
        communicator = Communicator()
        communicator.connect("localhost", TEST_MLLP_PORT)
        while True:
            message = communicator.receive()
            if message == None:
                break
            messages.append(communicator.from_mllp(message))
            communicator.acknowledge()
        communicator.close()
        self.assertEqual(messages, [ADT_A01, ORU_R01, ADT_A03])

    def test_integration_successful_page(self):
        communicator = Communicator(host="localhost", pager_port=TEST_PAGER_PORT)
        r = communicator.page("1234")
        communicator.close()
        self.assertEqual(r.status, http.HTTPStatus.OK)

    def test_integration_unsuccessful_page(self):
        communicator = Communicator(host="localhost", pager_port=TEST_PAGER_PORT)
        try:
            communicator.page("NHS1234")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.status, http.HTTPStatus.BAD_REQUEST)
        else:
            self.fail("Expected /page to return an error with a bad MRN")
        finally:
            communicator.close()

    # Test integration between Preprocessor and Database
    def test_integration_ADT_A01_register_patient(self):
        db = Database()
        preprocessor = Preprocessor(db)
        preprocessor.preprocess(DataParser().parse_message(to_mllp(ADT_A01)))
        self.assertEqual(db.get("478237423"), self.ADT_A01_db_entry)

    def test_integration_ADT_A03_delete_patient(self):
        db = Database()
        preprocessor = Preprocessor(db)
        preprocessor.preprocess(DataParser().parse_message(to_mllp(ADT_A01)))
        preprocessor.preprocess(DataParser().parse_message(to_mllp(ADT_A03)))
        self.assertEqual(db.get("478237423"), None)

    def test_integration_ORU_R01_add_test_result(self):
        db = Database()
        preprocessor = Preprocessor(db)
        preprocessor.preprocess(DataParser().parse_message(to_mllp(ADT_A01)))
        preprocessor.preprocess(DataParser().parse_message(to_mllp(ORU_R01)))
        self.assertEqual(db.get("478237423"), self.ORU_R01_db_entry)

    # Test integration of whole system
    def test_integration_admission_and_discharge(self):
        communicator = Communicator("localhost", TEST_MLLP_PORT, TEST_PAGER_PORT)
        dataparser = DataParser()
        database = Database()
        preprocessor = Preprocessor(database)
        model = load_model("./lstm_model.pth")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        has_aki = None

        num_message = 0
        while True:
            message = communicator.receive()
            if message == None:
                break
            parsed_message = dataparser.parse_message(message)
            mrn = parsed_message.mrn
            preprocessed_message = preprocessor.preprocess(parsed_message)
            if preprocessed_message is not None:
                has_aki = inference(model, preprocessed_message, device)
            communicator.acknowledge()

            if num_message == 0:
                self.assertEqual(mrn, "478237423")
                self.assertEqual(preprocessed_message, None)
                self.assertEqual(database.get(mrn), self.ADT_A01_db_entry)
                self.assertEqual(has_aki, None)
            num_message += 1

        communicator.close()

        self.assertEqual(mrn, "478237423")
        self.assertEqual(preprocessed_message, None)
        self.assertEqual(database.get(mrn), None)
        self.assertEqual(has_aki, 0)

    def test_integration_admission_without_aki_no_page(self):
        communicator = Communicator("localhost", TEST_MLLP_PORT, TEST_PAGER_PORT)
        dataparser = DataParser()
        database = Database()
        preprocessor = Preprocessor(database)
        model = load_model("./lstm_model.pth")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        has_aki = None
        page_response = None

        for _ in range(2):
            message = communicator.receive()
            if message == None:
                assert False
            parsed_message = dataparser.parse_message(message)
            mrn = parsed_message.mrn
            preprocessed_message = preprocessor.preprocess(parsed_message)
            if preprocessed_message is not None:
                has_aki = inference(model, preprocessed_message, device)
            if has_aki:
                page_response = communicator.page(mrn)
            communicator.acknowledge()
        communicator.close()

        self.assertEqual(mrn, "478237423")
        self.assertEqual(database.get(mrn), self.ORU_R01_db_entry)
        self.assertEqual(has_aki, 0)
        self.assertEqual(page_response, None)

    # TODO: Find ORU R01 message with AKI
    # def test_integration_admission_with_aki_page(self):
    #     communicator = Communicator("localhost", TEST_MLLP_PORT, TEST_PAGER_PORT)
    #     dataparser = DataParser()
    #     database = Database()
    #     preprocessor = Preprocessor(database)
    #     model = load_model("./lstm_model.pth")
    #     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #     has_aki = None
    #     page_response = None

    #     for _ in range(2):
    #         message = communicator.receive()
    #         if message == None:
    #             assert False
    #         parsed_message = dataparser.parse_message(message)
    #         mrn = parsed_message.mrn
    #         preprocessed_message = preprocessor.preprocess(parsed_message)
    #         if preprocessed_message is not None:
    #             has_aki = inference(model, preprocessed_message, device)
    #         if has_aki:
    #             page_response = communicator.page(mrn)
    #         communicator.acknowledge()
    #     communicator.close()

    #     self.assertEqual(mrn, "478237423")
    #     self.assertEqual(database.get(mrn), self.ORU_R01_db_entry)
    #     self.assertEqual(has_aki, 1)
    #     self.assertEqual(page_response.status, http.HTTPStatus.OK)

    def test_integration_model(self): # python3 -m unittest integration_test.SystemIntegrationTest.test_integration_model
        communicator = Communicator("localhost", 8440, 8441)
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
                save_inference_results(mrn_aki, date_aki, "mrn_aki.csv")
                break

            # Pass the message to data parser
            parsed_message = dataparser.parse_message(message)
            mrn = parsed_message.mrn
            if parsed_message.message_type == 'ORU^R01':
                date = parsed_message.obr_timestamp

            # Process message
            preprocessed_message = preprocessor.preprocess(parsed_message)
            # if mrn == "701783" and parsed_message.message_type == 'ORU^R01':
            #     print(preprocessed_message, date)

            # Perform inference
            has_aki = False
            if preprocessed_message is not None:
                has_aki = int(inference(model, preprocessed_message, device))
            
            # Page (if necessary)
            if has_aki and mrn not in mrn_aki:
                print(f"ALERT: Patient {mrn} has AKI")
                communicator.page(mrn)
                mrn_aki.append(mrn)
                date_aki.append(date)

            # Acknowledge message
            communicator.acknowledge()

    def test_check_accuracy(self, pred_file_path="mrn_aki.csv", positive_file_path = "data/aki.csv"):
        pred = set()
        with open(pred_file_path, "r") as f:
            for line in f:
                pred.add(line.strip())#.split(",")[0])
        positive = set()
        with open(positive_file_path, "r") as f:
            for line in f:
                positive.add(line.strip())#.split(",")[0])
        
        true_positives = []
        false_positives = []

        for p in pred:
            if p in positive:
                true_positives.append(p)
                #positive.remove(p)
            else:
                false_positives.append(p)
        beta = 3
        #print(positive)
        precision = len(true_positives) / (len(true_positives) + len(false_positives))
        recall = len(true_positives) / len(positive)
        f3 = ((1 + beta**2) * (precision * recall)) / ((beta**2 * precision) + recall)
        print(f"True positives: {len(true_positives)}")
        print(f"False positives: {len(false_positives)}")
        print(f"Precision: {precision}")
        print(f"Recall: {recall}")
        print(f"F3 Score: {f3}")

    def tearDown(self):
        try:
            r = urllib.request.urlopen(f"http://localhost:{TEST_PAGER_PORT}/shutdown")
            self.assertEqual(r.status, http.HTTPStatus.OK)
            self.simulator.wait()
            self.assertEqual(self.simulator.returncode, 0)
        finally:
            if self.simulator.poll() is None:
                self.simulator.kill()


if __name__ == "__main__":
    unittest.main()

