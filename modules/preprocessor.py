from database import Database
from datetime import datetime
import torch

VALUE_MEAN = 105.94255738333332
VALUE_STD= 39.19610255401994
AGE_MEAN = 37.040219
AGE_STD = 21.681311572666875
DATE_MEAN = 19.595264259014705
DATE_STD = 56.37914791297929

STANDARDIZE_MEAN = [AGE_MEAN, 0, DATE_MEAN, VALUE_MEAN]
STANDARDIZE_STD = [AGE_STD, 1, DATE_STD, VALUE_STD]

class Preprocessor():
    def __init__(self, Database):
        self.database = Database

    def preprocess(self, message):
        self.message = message
        self.check_message()
        # switch case for message type
        if self.message.message_type == 'ADT^A01':
            self.database.register(self.message.mrn, self.message.gender, self.message.dob, self.message.name)
            return
        elif self.message.message_type == 'ADT^A03':
            self.database.delete(self.message.mrn)
            return
        elif self.message.message_type == 'ORU^R01':
            patient_data = self.database.get(self.message.mrn)
            gender = patient_data['gender']
            dob = patient_data['dob']
            self.database.set(self.message.mrn, self.message.obr_timestamp, self.message.obx_value)
            test_results = patient_data['test_results']
            input_tensor = self.to_tensor(gender=gender, dob=dob, test_results=test_results)
            return input_tensor
    
    def check_message(self):
        if self.message.mrn is None:
            raise Exception('Error: MRN not found in the message')
        if self.message.message_type == 'ADT^A01':
            if self.message.gender is None:
                raise Exception('Error: Invalid message: no gender found')
            if self.message.dob is None:
                raise Exception('Error: Invalid message: no date of birth found')
            if self.message.name is None:
                raise Exception('Error: Invalid message: no name found')
        elif self.message.message_type == 'ADT^A03':
            if self.message.mrn is None:
                raise Exception('Error: Invalid message: no MRN found')
        elif self.message.message_type == 'ORU^R01':
            if not self.message.obx_type == "CREATININE":
                raise Exception('Error: Invalid message: invalid test type:', self.message.obx_type)
            elif self.message.obx_value is None:
                raise Exception('Error: Invalid message: no test value found')
            elif self.message.obr_timestamp is None:
                raise Exception('Error: Invalid message: no test date found')
        else:
            raise Exception('Error: Invalid message type:', self.message.message_type)

    def to_tensor(self, gender, dob, test_results):
        dob = datetime.strptime(dob, '%Y-%m-%d')
        # convert info to 2D tensor with [gender, dob, date, value]
        age = (datetime.now() - dob).days / 365.25
        static_data = torch.tensor([age, gender], dtype=torch.float32)
        test_results = [float(x) for x in test_results]
        static_data = static_data.repeat(int(len(test_results)/2), 1)
        test_results = torch.tensor(test_results, dtype=torch.float32).view(-1, 2)
        input_tensor = torch.cat((static_data, test_results), 1)
        return self.standardize_tensor(input_tensor)

    def standardize_tensor(self, input_tensor):
        mean_tensor = torch.tensor(STANDARDIZE_MEAN, dtype=torch.float32)
        std_tensor = torch.tensor(STANDARDIZE_STD, dtype=torch.float32)
        input_tensor = (input_tensor - mean_tensor) / std_tensor
        return input_tensor
    
        