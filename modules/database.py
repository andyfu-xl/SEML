import csv

class Database:
    def __init__(self, file_path=None):
        self.data = {}
        if file_path is not None:
            self.load_csv(file_path)
    
    def load_csv(self, file_path):
        with open('history.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            self.data = {}
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mrn = row[0]
                if mrn not in self.data:
                    self.data[mrn] = patientinfo = {"test_results": row[1:], "gender" : None, "dob" : None}
                else:
                    raise Exception('Duplicate MRN found:', mrn)

    def get(self, mrn):
        if mrn in self.data:
            return self.data[mrn]

    def set(self, mrn, date, value):
        if mrn in self.data:
            self.data[mrn]["test_results"].append((date, value))
        else:
            raise Exception('Error: Trying to set test results for a non-existing patient, MRN not found:', mrn)
        print("Test result added successfully")
            

    def delete(self, mrn):
        if mrn in self.data:
            del self.data[mrn]
        else:
            raise Exception('Error: Trying to discharging test results for a non-existing patient, MRN not found:', mrn)
        print("Patient discharged successfully")
        

    def register(self, mrn, gender, dob):
        if mrn not in self.data:
            self.data[mrn] = {"test_results": [], "gender": gender, "dob": dob}
        else:
            self.data[mrn]["gender"] = gender
            self.data[mrn]["dob"] = dob
        print("Patient registered successfully")