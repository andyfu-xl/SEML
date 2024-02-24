import socket
import time
import unittest

from communicator import Communicator

class CommunicatorTest(unittest.TestCase):
    def setUp(self):
        self.ACK_segments = [
            "MSH|^~\&|||||20240129093837||ACK|||2.5",
            "MSA|AA",
        ]
        self.ACK_mllp = b"\x0bMSH|^~\&|||||20240129093837||ACK|||2.5\rMSA|AA\r\x1c\r"
        self.communicator = Communicator()
        self.mllp_message = b"\x0bMSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||202401201630||ADT^A01|||2.5\r\
                                  PID|1||478237423||ELIZABETH HOLMES||19840203|F\r\
                                  NK1|1|SUNNY BALWANI|PARTNER\r\x1c\r"

        self.TEST_SERVER_PORT = 12345
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('localhost', self.TEST_SERVER_PORT))
        self.server_socket.listen(1)
        self.communicator.connect(f"localhost:{self.TEST_SERVER_PORT}")
        self.client, _ = self.server_socket.accept()

    def tearDown(self):
        self.communicator.close()
        self.server_socket.close()

    def test_receive_full_message(self):
        self.client.sendall(self.mllp_message)
        message = self.communicator.receive()

        self.assertEqual(message, self.mllp_message)

    def test_receive_partial_message(self):
        self.client.sendall(self.mllp_message[:len(self.mllp_message)//2])
        time.sleep(1)
        self.client.sendall(self.mllp_message[len(self.mllp_message)//2:])

        message = self.communicator.receive()

        self.assertEqual(message, self.mllp_message)

    def test_acknowledge(self):
        self.communicator.acknowledge()
        message = self.client.recv(1024)
        segments =  message.split(b"\r")
        segment_types = [s.split(b"|")[0] for s in segments]
        self.assertIn(b"\x0bMSH", segment_types)
        self.assertIn(b"MSA", segment_types)
        fields = segments[segment_types.index(b"MSA")].split(b"|")
        self.assertEqual(fields[1], b"AA")

    def test_to_mllp(self):
        mllp = self.communicator.to_mllp(self.ACK_segments)
        self.assertEqual(mllp, self.ACK_mllp)

if __name__ == "__main__":
    unittest.main()
