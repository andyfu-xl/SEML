import os
import time
import http
import unittest
import subprocess
import urllib.error
import urllib.request

from communicator.communicator import Communicator
from simulator_test import ADT_A01, ADT_A03, ORU_R01, TEST_MLLP_PORT, TEST_PAGER_PORT, wait_until_healthy
import subprocess

class SystemIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        relative_path = "../data/test_messages.mllp"
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
