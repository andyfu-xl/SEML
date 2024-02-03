from modules.database import Database
# from model import Model
class Preprocessor():
    def __init__(self, data, Database):
        self.data = data
        self.Database = Database

    def preprocess(self):
        ## todo: preprocess data
        return self.data
    
    def save(self, mrn):
        self.Database.save(self.data)

    def load(self, mrn):
        self.data = self.Database.load(mrn)
        return self.data