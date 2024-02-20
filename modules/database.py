import csv
from datetime import datetime
import sqlite3

class Database:
    def __init__(self, file_path=None):
        '''
        Main class for reading and storing the data, the data is stored in cache
        Attributes:
            data (dict): A dictionary of the data, with MRN as the key
                        Each patient's data is stored as a dictionary with the following
                        keys: test_results, gender, dob, name, last_test, paged
                        Where paged is a flag for avoiding paging the same patient multiple times
        '''
        if file_path is not None:
            self.conn = sqlite3.connect(file_path)
            self.curs = self.conn.cursor()
        else:
            raise Exception('Error: Have to provide a file path for the database')
        self.curs.execute('''CREATE TABLE IF NOT EXISTS patients_info (
               mrn INTEGER PRIMARY KEY,
               dob TEXT,
               gender INTEGER,
               name TEXT,
               last_test TEXT,
               test_results TEXT,
               test_dates TEXT,
               paged INTEGER)''')
        self.conn.commit()
        

    def load_csv(self, file_path, db_path):
        '''
        Load data from a csv file and store it in the data attribute
        Args:
            file_path (str): The path to the csv file
        '''
        conn = sqlite3.connect(db_path)
        curs = conn.cursor()
        curs.execute('''CREATE TABLE IF NOT EXISTS patients_info (
                mrn INTEGER PRIMARY KEY,
                dob TEXT,
                gender INTEGER,
                name TEXT,
                last_test TEXT,
                test_results REAL,
                test_dates REAL,
                paged INTEGER)''')
        conn.commit()
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mrn = row[0]
                test_results, test_dates, last_test = self.process_dates(row[1:])
                test_results = ','.join(test_results)
                test_dates = [str(x) for x in test_dates]
                test_dates = ','.join(test_dates)
                data_template = (mrn, '', '', '', last_test, test_results, test_dates, 0)
                curs.execute("INSERT INTO patients_info (mrn, dob, gender, name, last_test, test_results, test_dates, paged) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data_template)      
                conn.commit()   

    def process_dates(self, test_results):
        '''
        Process the dates in the test results and return the time difference between the dates
        this function processes the dates in the csv file, and returns the time difference between the dates
        the date of the last test is used to update new test results
        the entire process maintains all the information about each patient, while converted to format that is easy to use
        Args:
            test_results (list): A list of test results
        Returns:
            test_results (list): A list of test results with the time difference between the dates
            last_test (str): The date of the last test
        '''
        if len(test_results) < 2 or len(test_results) % 2 != 0:
            raise Exception('Invalid test results length:', test_results)
        curr_date = test_results[0]
        curr_date = datetime.strptime(curr_date, '%Y-%m-%d %H:%M:%S')
        # remove all emtpy strings
        test_results = [x for x in test_results if x != '']
        for i in range(0, len(test_results)-3, 2):
            if test_results[i+2] == '':
                test_results[i+2] = 0
                break
            next_date = test_results[i+2]
            next_date = datetime.strptime(next_date, '%Y-%m-%d %H:%M:%S')
            if next_date < curr_date:
                raise Exception('Dates are not in order:', curr_date, next_date)
            # compute time difference, in seconds
            diff = (next_date - curr_date).total_seconds() / (60*60*24)
            test_results[i] = diff
            curr_date = next_date
        last_test = test_results[-2]
        test_results[-2] = 0
        test_dates = test_results[::2]
        test_results = test_results[1::2]
        return test_results, test_dates, last_test

    def get(self, mrn):
        '''
        Get the patient's data from the database
        Args:
            mrn (str): The medical record number of the patient
        Returns:
            dict: The patient's data    
        '''
        self.curs.execute("SELECT * FROM patients_info WHERE mrn=?", (mrn,))
        result = self.curs.fetchone()
        # this should never be triggered, used for debugging, delete after testing
        if result is None:
            return None
        else:
            return {
                "mrn": result[0],
                "dob": result[1],
                "gender": result[2],
                "name": result[3],
                "last_test": result[4],
                "test_results": result[5],
                "test_dates": result[6],
                "paged": result[7]
            }
        


    def set(self, mrn, date, value):
        '''
        Add a new test result to the patient's data
        We do not accept new test results for patients who are not registered or have no historial test results
        We also do not accept test results that are not in order
        Args:
            mrn (str): The medical record number of the patient
            date (str): The date of the test
            value (float): The value of the test
        '''        
        self.curs.execute("SELECT COUNT(*) FROM patients_info WHERE mrn=?", (mrn,))
        result = self.curs.fetchone()
        if result[0] == 1:
            self.curs.execute("SELECT test_results, test_dates, last_test FROM patients_info WHERE mrn=?", (mrn,))
            existing_data = self.curs.fetchone()
            test_results, test_dates, last_test = existing_data
            if last_test != '':
                
                last_date = datetime.strptime(last_test, '%Y-%m-%d %H:%M:%S')
                strp_new_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                # error handling: when the new test date is in incorrect order, change the test date to the current date
                # TODO: in data parser, we could set the date to a very old date to trigger the if statement
                # or we can let the data parser to convert the date to the current date
                if strp_new_date < last_date:
                    strp_new_date = datetime.now()
                    date = strp_new_date.strftime('%Y-%m-%d %H:%M:%S')
                test_results = test_results + ',' + str(value) if test_results else str(value)
                test_dates = test_dates.split(',')
                test_dates[-1] = (strp_new_date - last_date).total_seconds() / (60*60*24)
                test_dates.append(0)
                test_dates = ','.join([str(x) for x in test_dates])
                self.curs.execute("UPDATE patients_info SET test_results=?, test_dates=?, last_test=? WHERE mrn=?", (test_results, test_dates, date, mrn))
            else:
                test_results = str(value)
                test_dates = str(0)
                self.curs.execute("UPDATE patients_info SET test_results=?, test_dates=?, last_test=? WHERE mrn=?", (test_results, test_dates, date, mrn))
            self.conn.commit()
        elif result[0] == 0:
            # register the patient first
            data_template = (mrn, "", "", "", str(date), str(value), str(0), 0)
            self.curs.execute("INSERT INTO patients_info (mrn, dob, gender, name, last_test, test_results, test_dates, paged) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data_template)
            self.conn.commit()
        else:
            # this should never be triggered if our implementation is correct, used for debugging
            raise Exception('Error: Multiple patients found with the same MRN:', mrn)
        

    def register(self, mrn, gender, dob, name):
        '''
        Register a new patient in the database
        This function registers patients.
        We accept patients who has no test results, or has test results in order
        Args:
            mrn (str): The medical record number of the patient
        '''
        # dob_datetime = datetime.strptime(dob, '%Y-%m-%d')
        # age = (datetime.now() - dob_datetime).days
        # TODO: improve error handling, when age is negative, we should use another model that does not require age or use mean age
        self.curs.execute("SELECT COUNT(*) FROM patients_info WHERE mrn=?", (mrn,))
        result = self.curs.fetchone()
        if result[0] == 1:
            self.curs.execute("UPDATE patients_info SET gender = ?, dob = ?, name = ? WHERE mrn = ?", (gender, dob, name, mrn))
        elif result[0] == 0:
            data_template = (mrn, dob, gender, name, '', '', '', 0)
            self.curs.execute("INSERT INTO patients_info (mrn, dob, gender, name, last_test, test_results, test_dates, paged) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data_template)
        else:
            # this should never be triggered if our implementation is correct, used for debugging
            raise Exception('Error: Multiple patients found with the same MRN:', mrn)
        self.conn.commit()
        
        
    def paged(self, mrn):
        '''
        This function pages the patient, we only have to page a patient once.
        Args:
            mrn (str): The medical record number of the patient
        '''
        self.curs.execute("SELECT COUNT(*) FROM patients_info WHERE mrn=?", (mrn,))
        result = self.curs.fetchone()
        if result[0] == 1:
            self.curs.execute("UPDATE patients_info SET paged = ? WHERE mrn = ?", (1, mrn))
            self.conn.commit()
        elif result[0] == 0:
            # this should never be triggered, should be deleted after testing
            raise Exception('Error: Trying to page a non-existing patient, MRN not found:', mrn)
        else:
            # this should never be triggered if our implementation is correct, used for debugging
            raise Exception('Error: Multiple patients found with the same MRN:', mrn)