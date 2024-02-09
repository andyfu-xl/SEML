import csv
from datetime import datetime

class Database:
    def __init__(self, file_path=None):
        self.data = {}
        if file_path is not None:
            self.load_csv(file_path)
    
    # this function loads the data from a csv file, and stores it in a dictionary
    def load_csv(self, file_path):
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            self.data = {}
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mrn = row[0]
                if mrn not in self.data:
                    test_results, last_test = self.process_dates(row[1:])
                    test_results = [float(x) for x in test_results]
                    self.data[mrn] = {"test_results": test_results, "gender" : None, "dob" : None, "name" : None, "last_test" : last_test, "paged": False}
                else:
                    raise Exception('Duplicate MRN found:', mrn)        

    # this function processes the dates in the csv file, and returns the time difference between the dates
    # the date of the last test is used to update new test results
    # the entire process maintains all the information about each patient, while converted to format that is easy to use
    def process_dates(self, test_results):
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
        return test_results, last_test
        
    # This function returns the patient's data from the database
    def get(self, mrn):
        if mrn in self.data:
            return self.data[mrn]

    # This function adds a new test result to the patient's data
    # We do not accept new test results for patients who are not registered or have no historial test results
    # We also do not accept test results that are not in order
    def set(self, mrn, date, value):
        if mrn not in self.data:
            raise Exception('Error: Trying to set test results for a non-existing patient, MRN not found:', mrn)
        if len(self.data[mrn]["test_results"]) == 0:
            self.data[mrn]["test_results"] = [0, value]
            self.data[mrn]["last_test"] = date
        elif self.data[mrn]["last_test"] is None:
            raise Exception('Error, last test date not found for patient:', mrn)
        elif date > self.data[mrn]["last_test"]:
            strp_new_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            last_date = datetime.strptime(self.data[mrn]["last_test"], '%Y-%m-%d %H:%M:%S')
            self.data[mrn]["test_results"][-2] = (strp_new_date - last_date).total_seconds() / (60*60*24)
            self.data[mrn]["test_results"].append(0)
            self.data[mrn]["test_results"].append(value)
            self.data[mrn]["last_test"] = date
        else:
            raise Exception('Error: Test date is not in order:', date, self.data[mrn]["last_test"])
        # print("Test result added successfully")
            

    def save_csv(self, msg):
        print("saving: " + str(msg.decode('utf-8')))
        with open('new_history.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(msg.decode('utf-8'))

    # This function deletes the patient's data from the database
    def delete(self, mrn):
        if mrn in self.data.keys():
            del self.data[mrn]
        else:
            raise Exception('Error: Trying to discharging test results for a non-existing patient, MRN not found:', mrn)
        # print("Patient discharged successfully")
        
    # This function registers patients.
    # We accept patients who has no test results, or has test results in order
    def register(self, mrn, gender, dob, name):
        if gender not in [0, 1]:
            raise Exception('Error: expected binary gender (0 for male or 1 for female) but found:', gender)
        dob_datetime = datetime.strptime(dob, '%Y-%m-%d')
        age = (datetime.now() - dob_datetime).days
        if age < 0:
            raise Exception('Error: Invalid date of birth:', dob)
        if mrn not in self.data:
            self.data[mrn] = {"test_results": [], "gender": gender, "dob": dob, "name":name, "last_test": None, "paged": False}
        else:
            self.data[mrn]["gender"] = gender
            self.data[mrn]["dob"] = dob
            self.data[mrn]["name"] = name
        # print("Patient registered successfully")
            
    # This function pages the patient, we only have to page a patient once.
    def paged(self, mrn):
        if mrn in self.data:
            self.data[mrn]["paged"] = True
        else:
            raise Exception('Error: Trying to page a non-existing patient, MRN not found:', mrn)