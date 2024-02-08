#!/usr/bin/env python3
import os
import http
import torch
import unittest
import subprocess
import urllib.error
import urllib.request

from modules.communicator.communicator import Communicator
from modules.dataparser.dataparser import DataParser
from modules.preprocessor import Preprocessor
from modules.database import Database
from modules.model import inference, load_model
from simulator_test import ADT_A01, ADT_A03, ORU_R01, TEST_MLLP_PORT, TEST_PAGER_PORT, wait_until_healthy, from_mllp, to_mllp

class SystemIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.ADT_A01_db_entry = {
            "dob": "1984-02-03",
            "gender": 1,
            "last_test": None,
            "name": "ELIZABETH HOLMES",
            "paged": False,
            "test_results": []
        }
        self.ORU_R01_db_entry = {
            "dob": "1984-02-03",
            "gender": 1,
            "last_test": '2024-01-20 22:04:03',
            "name": "ELIZABETH HOLMES",
            "paged": False,
            "test_results": [0, 103.4]
        }

        self.SAVED_MODEL_PATH = "./lstm_model.pth"
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
        communicator.connect(f"localhost:{TEST_MLLP_PORT}")
        while True:
            message = communicator.receive()
            if message == None:
                break
            messages.append(from_mllp(message))
            communicator.acknowledge()
        communicator.close()
        self.assertEqual(messages, [ADT_A01, ORU_R01, ADT_A03])

    def test_integration_successful_page(self):
        communicator = Communicator(pager_address=f"localhost:{TEST_PAGER_PORT}")
        r = communicator.page("1234")
        communicator.close()
        self.assertEqual(r.status, http.HTTPStatus.OK)

    def test_integration_unsuccessful_page(self):
        communicator = Communicator(pager_address=f"localhost:{TEST_PAGER_PORT}")
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

    def test_integration_ADT_A03_keep_patient_record(self):
        db = Database()
        preprocessor = Preprocessor(db)
        preprocessor.preprocess(DataParser().parse_message(to_mllp(ADT_A01)))
        preprocessor.preprocess(DataParser().parse_message(to_mllp(ADT_A03)))
        self.assertEqual(db.get("478237423"), self.ADT_A01_db_entry)

    def test_integration_ORU_R01_add_test_result(self):
        db = Database()
        preprocessor = Preprocessor(db)
        preprocessor.preprocess(DataParser().parse_message(to_mllp(ADT_A01)))
        preprocessor.preprocess(DataParser().parse_message(to_mllp(ORU_R01)))
        self.assertEqual(db.get("478237423"), self.ORU_R01_db_entry)

    # Test integration of whole system
    def test_integration_admission_and_discharge(self):
        communicator = Communicator(mllp_address=f"localhost:{TEST_MLLP_PORT}", pager_address=f"localhost:{TEST_PAGER_PORT}")
        dataparser = DataParser()
        database = Database()
        preprocessor = Preprocessor(database)
        model = load_model(self.SAVED_MODEL_PATH)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        has_aki = False

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
                self.assertEqual(has_aki, False)
            num_message += 1

        communicator.close()

        self.assertEqual(mrn, "478237423")
        self.assertEqual(preprocessed_message, None)
        self.assertEqual(database.get(mrn), self.ORU_R01_db_entry)
        self.assertEqual(has_aki, 0)

    def test_integration_admission_without_aki_no_page(self):
        communicator = Communicator(mllp_address=f"localhost:{TEST_MLLP_PORT}", pager_address=f"localhost:{TEST_PAGER_PORT}")
        dataparser = DataParser()
        database = Database()
        preprocessor = Preprocessor(database)
        model = load_model(self.SAVED_MODEL_PATH)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        has_aki = False
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

