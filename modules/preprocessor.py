from database import Database
from model import Model
from datetime import datetime
import torch

class Preprocessor():
    def __init__(self, message, Database):
        self.message = message
        self.check_message()
        self.message_type = message.message_type
        self.database = Database

    def preprocess(self):
        self.database.set(self.message.mrn, self.message.obr_timestamp, self.message.obx_value)
        # switch case for message type
        if self.message.message_type == b'ADT_A01':
            self.database.register(self.message.mrn, self.message.gender, self.message.dob, self.message.name)
        elif self.message.message_type == b'ADT_A03':
            self.database.delete(self.message.mrn)
        elif self.message.message_type == b'ORU_R01':
            patient_data = self.database.get(self.message.mrn)
            gender = patient_data['gender']
            dob = patient_data['dob']
            test_results = patient_data['test_results']
            test_results.append(0)
            test_results.append(self.message.obx_value)
            input_tensor = self.to_tensor(gender=gender, dob=dob, test_results=test_results)
        return input_tensor
    
    def check_message(self):
        if self.message.mrn is None:
            raise Exception('Error: MRN not found in the message')
        if self.message.message_type == b'ADT_A01':
            if self.message.gender is None:
                raise Exception('Error: Invalid message: no gender found')
            if self.message.dob is None:
                raise Exception('Error: Invalid message: no date of birth found')
            if self.message.name is None:
                raise Exception('Error: Invalid message: no name found')
            self.database.register(self.message.mrn, self.message.mrn)
        elif self.message.message_type == b'ADT_A03':
            self.database.delete(self.message.mrn)
        elif self.message.message_type == b'ORU_R01':
            if not self.message.obx_type == "CREATININE":
                raise Exception('Error: Invalid message: invalid test type:', self.message.obx_type)
            elif self.message.obx_value is None:
                raise Exception('Error: Invalid message: no test value found')
            elif self.message.obr_timestamp is None:
                raise Exception('Error: Invalid message: no test date found')
        else:
            raise Exception('Error: Invalid message type:', self.message.message_type)

    def to_tensor(self, gender, dob, test_results):
        # convert info to 2D tensor with [gender, dob, date, value]
        age = (datetime.now() - dob).years
        if gender == 'M':
            gender = 0
        elif gender == 'F':
            gender = 1
        else:
            raise Exception('Error: expected binary gender (F or M) but found:',gender)
        static_data = torch.tensor([age, gender], dtype=torch.float32)
        test_results = [float(x) for x in test_results]
        static_data = static_data.repeat(int(len(test_results)/2), 1)
        test_results = torch.tensor(test_results, dtype=torch.float32).view(-1, 2)
        input_tensor = torch.cat((static_data, test_results), 1)
        return self.standardize_tensor(input_tensor)

    def standardize_tensor(self, input_tensor):
        value_mean = 105.94255738333332 # result mean
        value_std = 39.19610255401994 # result std
        age_mean = 37.040219 # age_mean
        age_std = 21.681311572666875 # age_std
        date_mean = 19.595264259014705 # date mean
        date_std = 56.37914791297929 # date std
        mean_tensor = torch.tensor([age_mean,0, date_mean, value_mean], dtype=torch.float32)
        std_tensor = torch.tensor([age_std,1, date_std, value_std], dtype=torch.float32)
        input_tensor = (input_tensor - mean_tensor) / std_tensor
        return input_tensor
    
        