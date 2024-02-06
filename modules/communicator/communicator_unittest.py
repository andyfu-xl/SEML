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

    def tearDown(self):
        self.communicator.close()

    def test_to_mllp(self):
        mllp = self.communicator.to_mllp(self.ACK_segments)
        self.assertEqual(mllp, self.ACK_mllp)

    def test_from_mllp(self):
        segments = self.communicator.from_mllp(self.ACK_mllp)
        self.assertEqual(segments, self.ACK_segments)

if __name__ == "__main__":
    unittest.main()
