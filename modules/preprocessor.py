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

STANDARDIZE_MEAN = [DATE_MEAN, VALUE_MEAN, AGE_MEAN, 0]
STANDARDIZE_STD = [DATE_STD, VALUE_STD, AGE_STD, 1]

class Preprocessor():
    def __init__(self, database):
        self.database = database

    def preprocess(self, message):
        '''
        Preprocess all three types of messages:
        for ADT^A01, register the patient, and return None
        for ADT^A03, the function do nothing for CW3, return None
        for ORU^R01, add the test result to the patient's data, and return the input tensor for the model
        Args:
            message (Message): The message to be preprocessed
        Returns:
            input_tensor (Tensor): The input tensor for the model
                                    3D tensor with shape (1, 9, 4), 1 is the fixed batch size for cw3
                                    9 is the fixed number of test results for each patient, 4 is the number of features
        '''
        self.message = message
        self.check_message()
        # register patient
        if self.message.message_type == 'ADT^A01':
            self.database.register(self.message.mrn, self.message.gender, self.message.dob, self.message.name)
            return
        # delete patient
        elif self.message.message_type == 'ADT^A03':
            return
        # test result
        elif self.message.message_type == 'ORU^R01':
            patient_data = self.database.get(self.message.mrn)
            # we do not have to page a patient twice
            if patient_data["paged"]:
                return None
            gender = patient_data['gender']
            dob = patient_data['dob']
            if gender is None or dob is None:
                raise Exception('Error: empty gender or dob, please register patient first')
            self.database.set(self.message.mrn, self.message.obr_timestamp, self.message.obx_value)
            test_results = patient_data['test_results']
            # only look at the last 9 test results
            # if there is only one test result, we just skip it
            if len(test_results) <= 2:
                return None
            if len(test_results) > 18:
                test_results = test_results[-18:]
            if len(test_results) < 18:
                test_results = [0] * (18 - len(test_results)) + test_results
            input_tensor = self.to_tensor(gender=gender, dob=dob, test_results=test_results).view(1, -1, 4)
            input_tensor[input_tensor > 100] = 100
            return input_tensor
    

    def check_message(self):
        '''
        Check if the message is valid
        '''
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
        '''
        Convert the patient's info and test results into 2D tensor, and standardize it
        Args:
            gender (int): patient's gender
            dob (str): patient's date of birth
            test_results (list): patient's test results, in the order of [date1, value1, date2, value2, ...]
        Returns:
            input_tensor (Tensor): the 2D tensor of the patient's info and test results
                                    With shape (n, 4), n is the number of test results (fixed to 9 in CW3)
        '''
        dob = datetime.strptime(dob, '%Y-%m-%d')
        # The age computation is not accurate, but will not significantly affect the model
        # python's datetime library is faster
        # 0.25 is used to account for leap years
        age = (datetime.now() - dob).days / 365.25
        static_data = torch.tensor([age, gender], dtype=torch.float32)
        test_results = [float(x) for x in test_results]
        static_data = static_data.repeat(int(len(test_results)/2), 1)
        test_results = torch.tensor(test_results, dtype=torch.float32).view(-1, 2)
        input_tensor = torch.cat((test_results, static_data), 1)
        return self.standardize_tensor(input_tensor)


    def standardize_tensor(self, input_tensor):
        '''
        Standardize the input tensor. Means and stds computed from CW1 training data
        Args:
            input_tensor (Tensor): the input tensor to be standardized
        Returns:
            input_tensor (Tensor): the standardized input tensor
        '''
        mean_tensor = torch.tensor(STANDARDIZE_MEAN, dtype=torch.float32)
        std_tensor = torch.tensor(STANDARDIZE_STD, dtype=torch.float32)
        input_tensor = (input_tensor - mean_tensor) / std_tensor
        return input_tensor
    
        