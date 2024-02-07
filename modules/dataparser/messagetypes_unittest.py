import unittest
import messagetypes

class MessageTypesUnitTest(unittest.TestCase):
    def setUp(self):
        self.obj1 = messagetypes.Adt_a01()
        self.obj2 = messagetypes.Adt_a03()
        self.obj3 = messagetypes.Oru_r01()

    ### ADT^A01
    def test_process_message_adt_a01(self):
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||497030||ROSCOE DOHERTY||19870515|M']
        result = self.obj1.process_message(message_segments)
        self.assertEqual(result.message_type, 'ADT^A01')
        self.assertEqual(result.name, 'ROSCOE DOHERTY')
        self.assertEqual(result.dob, '1987-05-15')
        self.assertEqual(result.gender, 0)
        self.assertEqual(result.mrn, '497030')

    def test_process_invalid_adt_a01_missing_msg_timestamp(self):
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||||ADT^A01|||2.5', 
                            'PID|1||497030||ROSCOE DOHERTY||19870515|M']
        with self.assertRaises(ValueError): 
            self.obj1.process_message(message_segments)
    
    def test_process_invalid_adt_a01_missing_mrn(self):
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||||ROSCOE DOHERTY||19870515|M']
        with self.assertRaises(ValueError):
            self.obj1.process_message(message_segments)

    def test_process_invalid_adt_a01_missing_name(self):
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||497030||||19870515|M']
        with self.assertRaises(ValueError):
            self.obj1.process_message(message_segments)

    def test_process_invalid_adt_a01_missing_dob(self):
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||497030||ROSCOE DOHERTY|||M']
        with self.assertRaises(ValueError):
            self.obj1.process_message(message_segments)

    def test_process_invalid_adt_a01_missing_gender(self):
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||497030||ROSCOE DOHERTY||19870515|']
        with self.assertRaises(ValueError):
            self.obj1.process_message(message_segments)

    ### ADT^A03
    def test_process_message_adt_a03(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5', 
                            'PID|1||829339']
        result = self.obj2.process_message(message_segments)
        self.assertEqual(result.message_type, 'ADT^A03')
        self.assertEqual(result.mrn, '829339')

    def test_process_invalid_adt_a03_missing_msg_timestamp(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||||ADT^A03|||2.5', 
                            'PID|1||829339']
        with self.assertRaises(ValueError):
            self.obj2.process_message(message_segments)

    def test_process_invalid_adt_a03_missing_mrn(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5', 
                            'PID|1||']
        with self.assertRaises(ValueError):
            self.obj2.process_message(message_segments)

    ### ORU^R01
    def test_process_message_oru_r01(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5', 
                            'PID|1||257406', 'OBR|1||||||20240331113300', 'OBX|1|SN|CREATININE||92.95579346699137']
        result = self.obj3.process_message(message_segments)
        self.assertEqual(result.message_type, 'ORU^R01')
        self.assertEqual(result.mrn, '257406')
        self.assertEqual(result.obr_timestamp, '2024-03-31 11:33:00')
        self.assertEqual(result.obx_type, 'CREATININE')
        self.assertEqual(result.obx_value, 92.95579346699137)

    def test_process_invalid_oru_r01_missing_msg_timestamp(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||||ORU^R01|||2.5', 
                            'PID|1||257406', 'OBR|1||||||20240331113300', 'OBX|1|SN|CREATININE||92.95579346699137']
        with self.assertRaises(ValueError):
            self.obj3.process_message(message_segments)

    def test_process_invalid_oru_r01_missing_mrn(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5', 
                            'PID|1||', 'OBR|1||||||20240331113300', 'OBX|1|SN|CREATININE||92.95579346699137']
        with self.assertRaises(ValueError):
            self.obj3.process_message(message_segments)

    def test_process_invalid_oru_r01_missing_obr_timestamp(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5', 
                            'PID|1||257406', 'OBR|1||||||', 'OBX|1|SN|CREATININE||92.95579346699137']
        with self.assertRaises(ValueError):
            self.obj3.process_message(message_segments)

    def test_process_invalid_oru_r01_missing_obx_type(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5', 
                            'PID|1||257406', 'OBR|1||||||20240331113300', 'OBX|1|SN|||92.95579346699137']
        with self.assertRaises(ValueError):
            self.obj3.process_message(message_segments)

    def test_process_invalid_oru_r01_missing_obx_value(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5', 
                            'PID|1||257406', 'OBR|1||||||20240331113300', 'OBX|1|SN|CREATININE||']
        with self.assertRaises(ValueError):
            self.obj3.process_message(message_segments)

if __name__ == '__main__':
    unittest.main()