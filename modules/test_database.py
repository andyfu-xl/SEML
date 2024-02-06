import unittest
from modules.database import Database
from datetime import datetime
import os

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # create a simple csv file for testing
        with open('data/history_test.csv', 'w') as f:
            f.write('mrn,date1,result1,date2,result2,date3,result3\n')
            f.write('1,2020-01-01 00:00:00,1,2020-01-02 00:00:00,2,2020-01-03 00:00:00,3\n')
            f.write('2,2020-01-01 00:00:00,1,2020-01-02 00:00:00,2,2020-01-03 00:00:00,3\n')
        self.db = Database('data/history_test.csv')
        # delete the test file
        os.remove('data/history_test.csv')

    def test_load_csv(self):
        db = Database('data/history.csv')
        # all gender, dob and name should be None
        for _, patient in db.data.items():
            self.assertIsNone(patient["gender"])
            self.assertIsNone(patient["dob"])
            self.assertIsNone(patient["name"])
            self.assertIsNotNone(patient["test_results"])
            # the last test should always be string in '%Y-%m-%d %H:%M:%S' format
            self.assertIsInstance(patient["last_test"], str)
            try:
                datetime.strptime(patient["last_test"], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                self.fail(f'{patient["last_test"]} is not in the correct format')
            self.assertEqual(patient["test_results"][-2], 0)
            for each in patient["test_results"]:
                self.assertIsInstance(each, float)
                self.assertGreaterEqual(each, 0)
            self.assertEqual(len(patient["test_results"]) % 2, 0)
        

    def test_get(self):
        patient = self.db.get('1')
        self.assertIsNotNone(patient)
        self.assertIsNone(self.db.get('123'))
        self.assertEqual(patient['test_results'], [1.0, 1.0, 1.0, 2.0, 0.0, 3.0])
        

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
        test_results, last_test = self.db.process_dates(['2020-01-01 00:00:00', '1'])
        self.assertEqual(test_results, [0.0, "1"])
        self.assertEqual(last_test, '2020-01-01 00:00:00')

        # test with wrong date formats
        self.assertRaises(ValueError, self.db.process_dates, ['2020/01/01', '1'])
        self.assertRaises(ValueError, self.db.process_dates, ['2020.01.01', '1'])
        self.assertRaises(ValueError, self.db.process_dates, ['20-1-1', '1'])

    def test_set(self):
        # test with non-existing patient
        with self.assertRaises(Exception) as context:
            self.db.set('123', '2020-01-01 00:00:00', 1)
        self.assertTrue('Error: Trying to set test results for a non-existing patient, MRN not found:' in str(context.exception))
        # test with missing last test date
        last_test = self.db.data['1']['last_test']
        self.db.data['1']['last_test'] = None
        with self.assertRaises(Exception) as context:
            self.db.set('1', '2020-01-01 00:00:00', 1)
        self.assertTrue('Error, last test date not found for patient:' in str(context.exception))
        self.db.data['1']['last_test'] = last_test
        # test with invalid new test date
        with self.assertRaises(Exception) as context:
            self.db.set('1', '2019-01-01 00:00:00', 1)
        self.assertTrue('Error: Test date is not in order:' in str(context.exception))
        # test with valid new test date
        self.db.set('1', '2020-01-04 00:00:00', 4)
        self.assertEqual(self.db.data['1']['test_results'], [1.0, 1.0, 1.0, 2.0, 1.0, 3.0, 0.0, 4.0])
        self.assertEqual(self.db.data['1']['last_test'], '2020-01-04 00:00:00')

    def test_register(self):
        # register a new patient with no historial test results
        self.db.register('30', 0, '1990-01-01', 'John Doe')
        self.assertIsNotNone(self.db.get('30'))
        patient = self.db.get('30')
        self.assertEqual(patient['name'], 'John Doe')
        self.assertEqual(patient["gender"], 0)
        self.assertEqual(patient["dob"], '1990-01-01')
        self.assertIsNone(patient["last_test"])
        self.assertEqual(patient["test_results"], [])

        # register a new patient with historial test results
        self.db.register('1', 1, '1990-01-01', 'Jane Doe')
        self.assertIsNotNone(self.db.get('1'))
        patient = self.db.get('1')
        self.assertEqual(patient['name'], 'Jane Doe')
        self.assertEqual(patient['gender'], 1)
        self.assertEqual(patient['dob'], '1990-01-01')
        self.assertEqual(patient['last_test'], '2020-01-03 00:00:00')
        self.assertEqual(patient['test_results'], [1.0, 1.0, 1.0, 2.0, 0.0, 3.0])

        # test with invalid dob or gender
        with self.assertRaises(Exception) as context:
            self.db.register('40', 555, '1990-01-01', 'John Doe')
        self.assertTrue('Error: expected binary gender (0 for male or 1 for female) but found:' in str(context.exception))
        with self.assertRaises(Exception) as context:
            self.db.register('40', 0, '3990-01-01', 'John Doe')
        self.assertTrue('Error: Invalid date of birth:' in str(context.exception))


    def test_delete(self):
        self.db.delete('1')
        self.assertIsNone(self.db.get('1'))
        self.assertIsNotNone(self.db.get('2'))
        self.db.delete('2')
        self.assertIsNone(self.db.get('2'))
    

if __name__ == '__main__':
    unittest.main()

