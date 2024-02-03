from preprocessor import Preprocessor

class DataParser():
    def __init__(self, message, Database):
        self.message = message
        self.Database = Database
        self.preprocessor = Preprocessor(self.message, self.Database)
        pass
    def parse(self):
        pass