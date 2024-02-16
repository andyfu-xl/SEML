import unittest
from database import Database
from datetime import datetime
import os

class TestDatabase(unittest.TestCase):
    def setUp(self):
        with open('./data/history_test.csv', 'w') as f:
            f.write('mrn,date1,result1,date2,result2,date3,result3\n')
            f.write('1,2020-01-01 00:00:00,1,2020-01-02 00:00:00,2,2020-01-03 00:00:00,3\n')
            f.write('2,2020-01-01 00:00:00,1,2020-01-02 00:00:00,2,2020-01-03 00:00:00,3\n')
        
        # remove the test file if it exists
        if os.path.exists('./data/history_test.db'):
            os.remove('./data/history_test.db')
        self.db = Database('./data/history_test.db')
        self.db.load_csv('./data/history_test.csv', './data/history_test.db')
        # delete the test file
        os.remove('./data/history_test.csv')
        

    def test_get(self):
        patient = self.db.get('1')
        self.assertIsNotNone(patient)
        self.assertIsNone(self.db.get('123'))
        test_results = patient['test_results'].split(',')
        test_results = [float(x) for x in test_results]
        self.assertEqual(test_results, [1.0, 2.0, 3.0])
        test_dates = patient['test_dates'].split(',')
        test_dates = [float(x) for x in test_dates]
        self.assertEqual(test_dates, [1.0, 1.0, 0.0])
        

    def test_process_date(self):
        # test with incorrectly ordered dates
        with self.assertRaises(Exception) as context:
            self.db.process_dates(['2020-02-01 00:00:00', '1', '2020-01-02 00:00:00', '2', '2010-01-03 00:00:00', '3'])
        self.assertTrue('Dates are not in order:' in str(context.exception))
        # test with empty test results
        with self.assertRaises(Exception) as context:
            self.db.process_dates([])
        self.assertTrue('Invalid test results length:' in str(context.exception))
        # test with imcomplete test results
        with self.assertRaises(Exception) as context:
            self.db.process_dates(['2020-01-01 00:00:00'])
        self.assertTrue('Invalid test results length:' in str(context.exception))
        
        # test with only one test result
        test_results, test_dates, last_test = self.db.process_dates(['2020-01-01 00:00:00', '1'])
        self.assertEqual(test_results, ["1"])
        self.assertEqual(test_dates, [0])
        self.assertEqual(last_test, '2020-01-01 00:00:00')

        # test with wrong date formats
        self.assertRaises(ValueError, self.db.process_dates, ['2020/01/01', '1'])
        self.assertRaises(ValueError, self.db.process_dates, ['2020.01.01', '1'])
        self.assertRaises(ValueError, self.db.process_dates, ['20-1-1', '1'])

    def test_set(self):
        # test with non-existing patient
        self.db.set('123', '2020-01-01 00:00:00', 1)
        patient = self.db.get('123')
        self.assertIsNotNone(patient)
        self.assertEqual(patient['last_test'], '2020-01-01 00:00:00')
        self.assertEqual(float(patient['test_results']), 1.0)
        self.assertEqual(float(patient['test_dates']), 0.0)

        # test with invalid new test date
        self.db.set('1', '2019-01-01 00:00:00', 1)
        self.assertIsNotNone(self.db.get('1'))
        # test with valid new test date
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.db.set('1', '2020-01-04 00:00:00', 4)
        patient = self.db.get('1')
        test_results = patient['test_results'].split(',')
        test_results = [float(x) for x in test_results]
        test_dates = patient['test_dates'].split(',')
        test_dates = [float(x) for x in test_dates]
        self.assertEqual(test_results, [1.0, 2.0, 3.0, 1.0, 4.0])
        self.assertEqual(test_dates[-1], 0)
        # 3 is the maximum allowed latency, we write two consecutive tests with 3 seconds
        self.assertLessEqual(test_dates[-2], 3/(24*60*60))
        self.assertEqual(test_dates[:2], [1.0, 1.0])
        self.assertLessEqual(patient['last_test'], now)

    def test_register(self):
        # register a new patient with no historial test results
        self.db.register('30', 0, '1990-01-01', 'John Doe')
        self.assertIsNotNone(self.db.get('30'))
        patient = self.db.get('30')
        self.assertEqual(patient['name'], 'John Doe')
        self.assertEqual(patient["gender"], 0)
        self.assertEqual(patient["dob"], '1990-01-01')
        self.assertEqual(patient["last_test"], '')
        self.assertEqual(patient["test_results"], '')

        # register a new patient with historial test results
        self.db.register('1', 1, '1990-01-01', 'Jane Doe')
        self.assertIsNotNone(self.db.get('1'))
        patient = self.db.get('1')
        self.assertEqual(patient['name'], 'Jane Doe')
        self.assertEqual(patient['gender'], 1)
        self.assertEqual(patient['dob'], '1990-01-01')
        self.assertEqual(patient['last_test'], '2020-01-03 00:00:00')
        test_results = patient['test_results'].split(',')
        test_results = [float(x) for x in test_results]
        self.assertEqual(test_results, [1.0, 2.0, 3.0])
        test_dates = patient['test_dates'].split(',')
        test_dates = [float(x) for x in test_dates]
        self.assertEqual(test_dates, [1.0, 1.0, 0.0])


    def test_paging(self):
        self.db.paged('1')
        self.assertTrue(self.db.get('1')['paged'])
    

if __name__ == '__main__':
    unittest.main()
