import unittest
import dataparser as dataparser

class DataparserUnitTest(unittest.TestCase):
    def setUp(self):
        self.obj = dataparser.DataParser()

    ### For remove_start_and_end function
    def test_remove_start_and_end_start_end_bytes_present(self):
        message = b'\x0bHello\x1c'
        expected_result = b'Hello'
        result = self.obj.remove_start_and_end(message)
        self.assertEqual(result, expected_result)

    def test_remove_start_and_end_multiple_start_and_end_bytes(self):
        message = b'\x0b\x0bHello\x1c\x1c'
        expected_result = b'\x0bHello\x1c'
        result = self.obj.remove_start_and_end(message)
        self.assertEqual(result, expected_result)

    def test_remove_start_and_end_multiple_start_and_end_bytes_2(self):
        message = b'\x0b\x0b\x0bHello\x1c\x1c\x1c'
        expected_result = b'\x0b\x0bHello\x1c\x1c'
        result = self.obj.remove_start_and_end(message)
        self.assertEqual(result, expected_result)

    def test_remove_start_and_end_multiple_start_and_end_bytes_3(self):
        message = b'\x0b\x0bHello\x1c\x1c\x1c'
        expected_result = b'\x0bHello\x1c\x1c'
        result = self.obj.remove_start_and_end(message)
        self.assertEqual(result, expected_result)

    ### For segment_message function
    def test_segment_message_empty(self):
        message = ''
        expected_segments = []
        result = self.obj.segment_message(message)
        self.assertEqual(result, expected_segments)

    def test_segment_message_single_segment(self):
        message = 'MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5'
        expected_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5']
        result = self.obj.segment_message(message)
        self.assertEqual(result, expected_segments)

    def test_segment_message_ADT_A01(self):
        message = 'MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5\rPID|1||497030||ROSCOE DOHERTY||19870515|M\r\r'
        expected_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                             'PID|1||497030||ROSCOE DOHERTY||19870515|M']
        result = self.obj.segment_message(message)
        self.assertEqual(result, expected_segments)

    def test_segment_message_ADT_A03(self):
        message = 'MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5\rPID|1||829339\r\r'
        expected_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5', 
                             'PID|1||829339']
        result = self.obj.segment_message(message)
        self.assertEqual(result, expected_segments)

    def test_segment_message_ORU(self):
        message = 'MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5\rPID|1||257406\rOBR|1||||||20240331113300\rOBX|1|SN|CREATININE||92.95579346699137\r\r'
        expected_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5',
                             'PID|1||257406',
                             'OBR|1||||||20240331113300',
                             'OBX|1|SN|CREATININE||92.95579346699137']
        result = self.obj.segment_message(message)
        self.assertEqual(result, expected_segments)

    def test_segment_message_with_new_separator(self):
        message = 'MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5\nPID|1||829339\n\n'
        expected_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5',
                             'PID|1||829339']
        result = self.obj.segment_message(message, segment='\n')
        self.assertEqual(result, expected_segments)

    ### For get_message_type function
    def test_get_message_type_ORU(self):
        message_segment = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5']
        expected_result = 'ORU^R01'
        result = self.obj.get_message_type(message_segment)
        self.assertEqual(result, expected_result)

    def test_get_message_type_ADT_A01(self):
        message_segment = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5']
        expected_result = 'ADT^A01'
        result = self.obj.get_message_type(message_segment)
        self.assertEqual(result, expected_result)

    def test_get_message_type_ADT_A03(self):
        message_segment = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5']
        expected_result = 'ADT^A03'
        result = self.obj.get_message_type(message_segment)
        self.assertEqual(result, expected_result)

    def test_get_message_type_invalid(self):
        message_segment = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A04|||2.5']
        with self.assertRaises(ValueError):
            self.obj.get_message_type(message_segment)

    def test_get_message_type_empty(self):
        message_segment = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800|||||2.5']
        with self.assertRaises(ValueError):
            self.obj.get_message_type(message_segment)

    def test_get_message_type_no_message_type(self):
        message_segment = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||||2.5']
        with self.assertRaises(ValueError):
            self.obj.get_message_type(message_segment)

    ### For process_message function
    def test_process_message_ORU_R01(self):
        message = b'\x0bMSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5\rPID|1||257406\rOBR|1||||||20240331113300\rOBX|1|SN|CREATININE||92.95579346699137\r\x1c\r'
        expected_result = 'ORU^R01'
        result = self.obj.parse_message(message)
        self.assertEqual(result.message_type, expected_result)

    def test_process_message_ADT_A01(self):
        message = b'\x0bMSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5\rPID|1||497030||ROSCOE DOHERTY||19870515|M\r\x1c\r'
        expected_result = 'ADT^A01'
        result = self.obj.parse_message(message)
        self.assertEqual(result.message_type, expected_result)

    def test_process_message_ADT_A03(self):
        message = b'\x0bMSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5\rPID|1||829339\r\x1c\r'
        expected_result = 'ADT^A03'
        result = self.obj.parse_message(message)
        self.assertEqual(result.message_type, expected_result)


if __name__ == '__main__':
    unittest.main()