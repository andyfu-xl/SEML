import unittest
import torch
from model import LSTMModel
from model_utils import inference

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

class TestModel(unittest.TestCase):
	def setUp(self):
		self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
		self.model = LSTMModel(input_dim=4, hidden_dim=64, output_dim=2, num_layers=2)
		self.model = LSTMModel(input_dim=4, hidden_dim=64, output_dim=2, num_layers=2)
		# Load the model's state dictionary
		self.model.load_state_dict(torch.load('../lstm_model.pth'))
		self.input_1 = torch.normal(0, 1, (1, 9, 4))
		self.input_2 = torch.tensor([[[0.0, 0.0, 76, 0],
							   		[0.0, 0.0, 76, 0],
									[1.9479166666715173, 96.98, 76, 0],
									[0.6541666666671517, 112.99, 76, 0],
									[2.094444444439432, 115.52, 76, 0],
									[65.91458333333867, 109.61, 76, 0],
									[0.36041666666278616, 128.1, 76, 0],
									[1.5743055555576575, 141.38, 76, 0],
									[0, 208.73, 76, 0]]])

	def test_inference(self):
		predicted = int(inference(self.model, self.input_1, self.device))
		self.assertIsInstance(predicted, int)
		self.assertIn(predicted, [0, 1])

	def test_correct_inference(self):
		standardized_input = self.standardize_tensor(self.input_2)
		# Test if the model can correctly classify the input data
		predicted = int(inference(self.model, standardized_input, self.device))
		self.assertEqual(predicted, 1)

	def standardize_tensor(self, input_tensor):
		mean_tensor = torch.tensor(STANDARDIZE_MEAN, dtype=torch.float32)
		std_tensor = torch.tensor(STANDARDIZE_STD, dtype=torch.float32)
		input_tensor = (input_tensor - mean_tensor) / std_tensor
		return input_tensor
	

if __name__ == '__main__':
    unittest.main()