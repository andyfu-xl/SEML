import csv

class Database:
    def __init__(self, file_path=None):
        self.data = {}
        if file_path is not None:
            self.load_csv(file_path)
    
    def load_csv(self, file_path):
        with open('history.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            # initialize empyt dictionary, the key is patient's mrn and the value is patient's history
            self.data = {}
            # Iterate over each row in the CSV file
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mrn = row[0]
                if mrn not in self.data:
                    self.data[mrn] = row[1:]
                else:
                    raise Exception('Duplicate MRN found:', mrn)

    def get(self, mrn):
        if mrn in self.data:
            return self.data[mrn]

    def set(self, key, value):
        pass

    def delete(self, key):
        pass

    def register(self, key):
        pass