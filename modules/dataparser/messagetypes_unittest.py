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
        self.assertEqual(result, True)
        self.assertEqual(self.obj1.message_type, 'ADT^A01')
        self.assertEqual(self.obj1.name, 'ROSCOE DOHERTY')
        self.assertEqual(self.obj1.dob, '1987-05-15')
        self.assertEqual(self.obj1.gender, 0)
        self.assertEqual(self.obj1.mrn, '497030')

    def test_process_invalid_adt_a01_missing_msg_timestamp(self):
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||||ADT^A01|||2.5', 
                            'PID|1||497030||ROSCOE DOHERTY||19870515|M']
        
        is_processed = self.obj1.process_message(message_segments)
        self.assertEqual(is_processed, False)
    
    def test_process_invalid_adt_a01_missing_mrn(self):
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||||ROSCOE DOHERTY||19870515|M']
        
        is_processed = self.obj1.process_message(message_segments)
        self.assertEqual(is_processed, False)

    def test_process_invalid_adt_a01_missing_name(self):
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||497030||||19870515|M']
        
        is_processed = self.obj1.process_message(message_segments)
        self.assertEqual(is_processed, False)

    def test_process_invalid_adt_a01_missing_dob(self):
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||497030||ROSCOE DOHERTY|||M']
        
        is_processed = self.obj1.process_message(message_segments)
        self.assertEqual(is_processed, False)

    def test_process_invalid_adt_a01_missing_gender(self):
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||497030||ROSCOE DOHERTY||19870515|']
        
        is_processed = self.obj1.process_message(message_segments)
        self.assertEqual(is_processed, False)

    ### ADT^A03
    def test_process_message_adt_a03(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5', 
                            'PID|1||829339']
        result = self.obj2.process_message(message_segments)
        self.assertEqual(result, True)
        self.assertEqual(self.obj2.message_type, 'ADT^A03')
        self.assertEqual(self.obj2.mrn, '829339')

    def test_process_invalid_adt_a03_missing_msg_timestamp(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||||ADT^A03|||2.5', 
                            'PID|1||829339']
        
        is_processed = self.obj2.process_message(message_segments)
        self.assertEqual(is_processed, False)

    def test_process_invalid_adt_a03_missing_mrn(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5', 
                            'PID|1||']
        
        is_processed = self.obj2.process_message(message_segments)
        self.assertEqual(is_processed, False)

    ### ORU^R01
    def test_process_message_oru_r01(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5', 
                            'PID|1||257406', 'OBR|1||||||20240331113300', 'OBX|1|SN|CREATININE||92.95579346699137']
        result = self.obj3.process_message(message_segments)
        self.assertEqual(result, True)
        self.assertEqual(self.obj3.message_type, 'ORU^R01')
        self.assertEqual(self.obj3.mrn, '257406')
        self.assertEqual(self.obj3.obr_timestamp, '2024-03-31 11:33:00')
        self.assertEqual(self.obj3.obx_type, 'CREATININE')
        self.assertEqual(self.obj3.obx_value, 92.95579346699137)

    def test_process_invalid_oru_r01_missing_msg_timestamp(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||||ORU^R01|||2.5', 
                            'PID|1||257406', 'OBR|1||||||20240331113300', 'OBX|1|SN|CREATININE||92.95579346699137']
        
        is_processed = self.obj3.process_message(message_segments)
        self.assertEqual(is_processed, False)

    def test_process_invalid_oru_r01_missing_mrn(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5', 
                            'PID|1||', 'OBR|1||||||20240331113300', 'OBX|1|SN|CREATININE||92.95579346699137']
        
        is_processed = self.obj3.process_message(message_segments)
        self.assertEqual(is_processed, False)

    def test_process_invalid_oru_r01_missing_obr_timestamp(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5', 
                            'PID|1||257406', 'OBR|1||||||', 'OBX|1|SN|CREATININE||92.95579346699137']
        
        is_processed = self.obj3.process_message(message_segments)
        self.assertEqual(is_processed, False)

    def test_process_invalid_oru_r01_missing_obx_type(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5', 
                            'PID|1||257406', 'OBR|1||||||20240331113300', 'OBX|1|SN|||92.95579346699137']
        
        is_processed = self.obj3.process_message(message_segments)
        self.assertEqual(is_processed, False)

    def test_process_invalid_oru_r01_missing_obx_value(self):
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5', 
                            'PID|1||257406', 'OBR|1||||||20240331113300', 'OBX|1|SN|CREATININE||']
        
        is_processed = self.obj3.process_message(message_segments)
        self.assertEqual(is_processed, False)

    

if __name__ == '__main__':
    unittest.main()