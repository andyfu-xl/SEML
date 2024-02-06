import unittest
from datetime import datetime
import os
import torch
from preprocessor import Preprocessor, AGE_MEAN, AGE_STD, DATE_MEAN, DATE_STD, VALUE_MEAN, VALUE_STD
from database import Database
import dataparser.messagetypes as messagetypes

class TestPreprocessor(unittest.TestCase):
    def setUp(self):
        # create a simple csv file for testing
        with open('../data/history_test.csv', 'w') as f:
            f.write('mrn,date1,result1,date2,result2,date3,result3\n')
            f.write('1,2020-01-01 00:00:00,1,2020-01-02 00:00:00,2\n')
            f.write('2,2020-01-01 00:00:00,1,2020-01-02 00:00:00,2,2020-01-03 00:00:00,3\n')
            f.write('10,2020-01-01 00:00:00,1,2020-01-02 00:00:00,2,2020-01-03 00:00:00,3,2020-01-04 00:00:00,4,2020-01-05 00:00:00,5,2020-01-06 00:00:00,6,2020-01-07 00:00:00,7,2020-01-08 00:00:00,8,2020-01-09 00:00:00,9,2020-01-10 00:00:00,10\n')
        self.db = Database('../data/history_test.csv')
        # delete the test file
        os.remove('../data/history_test.csv')
        self.preprocessor = Preprocessor(self.db)
        # register
        message1 = messagetypes.Adt_a01()
        # delete
        message2 = messagetypes.Adt_a03()
        # register
        message3 = messagetypes.Adt_a01()
        # test result
        message4 = messagetypes.Oru_r01()
        # register
        message5 = messagetypes.Adt_a01()
        # test result
        message6 = messagetypes.Oru_r01()
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||497030||ROSCOE DOHERTY||19870515|M']
        self.result1 = message1.process_message(message_segments)
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5', 
                            'PID|1||497030']
        self.result2 = message2.process_message(message_segments)
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||1||ROSCOE DOHERTY||19870515|M']
        self.result3 = message3.process_message(message_segments)
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20200103000000||ORU^R01|||2.5', 
                            'PID|1||1', 'OBR|1||||||20200103000000', 'OBX|1|SN|CREATININE||3.0']
        self.result4 = message4.process_message(message_segments)
        message_segments = ['MSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5', 
                            'PID|1||10||ROSCOE DOHERTY||19870515|M']
        self.result5 = message5.process_message(message_segments)
        message_segments = ['MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20200103000000||ORU^R01|||2.5', 
                            'PID|1||10', 'OBR|1||||||20200111000000', 'OBX|1|SN|CREATININE||3.0']
        self.result6 = message6.process_message(message_segments)

    def test_preprocess(self):
        # test if the preprocessor raises the expected exception for non-registered patients
        with self.assertRaises(Exception) as context:
            self.preprocessor.preprocess(self.result4)
        self.assertTrue("Error: empty gender or dob, please register patient first" in str(context.exception))

        # test if the preprocessor returns None for ADT^A01 and ADT^A03 messages
        self.assertEqual(self.preprocessor.preprocess(self.result1), None)
        self.assertEqual(self.preprocessor.preprocess(self.result2), None)
        self.preprocessor.preprocess(self.result3)

        # test if the preprocessor returns the correct tensor
        output_tensor = self.preprocessor.preprocess(self.result4)
        self.assertIsInstance(output_tensor, torch.Tensor)
        self.assertEqual(output_tensor.shape, torch.Size([3, 4]))
        # standardized age
        age = (datetime.now() - datetime.strptime(self.result3.dob, '%Y-%m-%d')).days / 365.25
        standardized_age = (age - AGE_MEAN) / AGE_STD
        # standardized time interval
        time_interval = (1 - DATE_MEAN) / DATE_STD
        # standardized test result
        standardized_test_result1 = (1.0 - VALUE_MEAN) / VALUE_STD
        standardized_test_result2 = (2.0 - VALUE_MEAN) / VALUE_STD
        standardized_test_result3 = (3.0 - VALUE_MEAN) / VALUE_STD
        expected_tensor = torch.tensor([[standardized_age, 0, time_interval, standardized_test_result1],
                                        [standardized_age, 0, time_interval, standardized_test_result2],
                                        [standardized_age, 0, (0-DATE_MEAN)/DATE_STD, standardized_test_result3]])
        self.assertTrue(torch.allclose(output_tensor, expected_tensor, atol=1e-8))

        # test if the preprocessor limits the number of test results to 9
        self.preprocessor.preprocess(self.result5)
        output_tensor = self.preprocessor.preprocess(self.result6)
        self.assertEqual(output_tensor.shape, torch.Size([9, 4]))




if __name__ == '__main__':
    unittest.main()

    