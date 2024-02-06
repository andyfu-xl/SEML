from database import Database
from datetime import datetime
import torch

# Following constants are computed from CW1 training data
# the mean and standard deviation of the test result value and age
VALUE_MEAN = 105.94255738333332
VALUE_STD= 39.19610255401994
AGE_MEAN = 37.040219
AGE_STD = 21.681311572666875
# the average interval between two tests in days
DATE_MEAN = 19.595264259014705
# the standard deviation of the interval between two tests in days
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
        # register patient
        if self.message.message_type == 'ADT^A01':
            self.database.register(self.message.mrn, self.message.gender, self.message.dob, self.message.name)
            return
        # delete patient
        elif self.message.message_type == 'ADT^A03':
            self.database.delete(self.message.mrn)
            return
        # test result
        elif self.message.message_type == 'ORU^R01':
            patient_data = self.database.get(self.message.mrn)
            gender = patient_data['gender']
            dob = patient_data['dob']
            if gender is None or dob is None:
                raise Exception('Error: empty gender or dob, please register patient first')
            self.database.set(self.message.mrn, self.message.obr_timestamp, self.message.obx_value)
            test_results = patient_data['test_results']
            # only look at the last 9 test results
            if len(test_results) > 18:
                test_results = test_results[-18:]
            input_tensor = self.to_tensor(gender=gender, dob=dob, test_results=test_results)
            return input_tensor
    
    # this is a helper function to check if the message is valid
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

    # combine the patient's info and test results into a tensor, and standardize it
    def to_tensor(self, gender, dob, test_results):
        dob = datetime.strptime(dob, '%Y-%m-%d')
        # convert info to 2D tensor with [gender, dob, date, value]
        # the age computation is not accurate, but will not significantly affect the model
        # python's datetime library is faster
        # 0.25 is used to account for leap years
        age = (datetime.now() - dob).days / 365.25
        static_data = torch.tensor([age, gender], dtype=torch.float32)
        test_results = [float(x) for x in test_results]
        static_data = static_data.repeat(int(len(test_results)/2), 1)
        test_results = torch.tensor(test_results, dtype=torch.float32).view(-1, 2)
        input_tensor = torch.cat((static_data, test_results), 1)
        return self.standardize_tensor(input_tensor)

    # standardize the tensor, using the mean and std computed from the training data
    def standardize_tensor(self, input_tensor):
        mean_tensor = torch.tensor(STANDARDIZE_MEAN, dtype=torch.float32)
        std_tensor = torch.tensor(STANDARDIZE_STD, dtype=torch.float32)
        input_tensor = (input_tensor - mean_tensor) / std_tensor
        return input_tensor
    
        