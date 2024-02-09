import unittest
import torch
from model import inference, load_model
from preprocessor import Preprocessor
from database import Database

class TestModel(unittest.TestCase):
	def setUp(self):
		self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
		self.model = load_model('./lstm_model.pth')
		self.model.to(self.device)
		self.database = Database()
		self.preprocessor = Preprocessor(self.database)

		# Random input data
		self.input_1 = torch.normal(0, 1, (1, 9, 4))
		# Positive sample form training set (unpreprocessed)
		self.input_2 = torch.tensor([[[0.0, 0.0, 76, 0],
							   		[0.0, 0.0, 76, 0],
									[1.9479166666715173, 96.98, 76, 0],
									[0.6541666666671517, 112.99, 76, 0],
									[2.094444444439432, 115.52, 76, 0],
									[65.91458333333867, 109.61, 76, 0],
									[0.36041666666278616, 128.1, 76, 0],
									[1.5743055555576575, 141.38, 76, 0],
									[0, 208.73, 76, 0]]])
		
		# Negative sample form training set (unpreprocessed)
		self.input_3 = torch.tensor([[[1.7805555555605679, 103.06, 58, 1],
									[0.18541666666715173, 107.05, 58, 1],
									[0.0194444444423425, 106.69, 58, 1],
									[205.57708333332994, 94.93, 58, 1],
									[0.041666666671517305, 113.28, 58, 1],
									[0.2083333333284827, 106.45, 58, 1],
									[1.0118055555576575, 115.99, 58, 1],
									[0.804861111108039, 103.19, 58, 1],
									[0, 99.0, 58, 1]]])
		# Positive sample form training set (preprocessed)
		self.input_4 = torch.tensor([[[ 1.9051e-01, -3.0673e-01,  2.4566e+00,  0.0000e+00],
									[-3.4692e-01, -5.6721e-01,  2.4566e+00,  0.0000e+00],
									[-3.1868e-01, -2.2789e-01,  2.4566e+00,  0.0000e+00],
									[-3.4552e-01,  2.4860e-03,  2.4566e+00,  0.0000e+00],
									[-3.0353e-01, -1.9371e-01,  2.4566e+00,  0.0000e+00],
									[-1.4641e-01, -4.1005e-01,  2.4566e+00,  0.0000e+00],
									[-2.3926e-01, -3.0571e-01,  2.4566e+00,  0.0000e+00],
									[-3.4106e-01, -6.6935e-01,  2.4566e+00,  0.0000e+00],
									[-3.4756e-01,  2.7688e+04,  2.4566e+00,  0.0000e+00]]])
									
	def test_inference(self):
		'''
		Test if the model can inference the input data with expected shape, 
		and give the expected output 0 or 1.
		'''
		predicted = int(inference(self.model, self.input_1.to(self.device)))
		self.assertIsInstance(predicted, int)
		self.assertIn(predicted, [0, 1])

	def test_accuracy_inference(self):
		'''
		Test if the model can correctly classify the positive sample, negative sample, 
		and the preprocessed input sample
		'''
		standardized_input = self.preprocessor.standardize_tensor(self.input_2.to(self.device))
		# Test if the model can correctly classify the input data
		predicted = inference(self.model, standardized_input)
		self.assertEqual(predicted, 1)

		standardized_input = self.preprocessor.standardize_tensor(self.input_3.to(self.device))
		predicted = inference(self.model, standardized_input)
		self.assertEqual(predicted, 0)

		predicted = inference(self.model, self.input_4.to(self.device))
		self.assertEqual(predicted, 1)

if __name__ == '__main__':
    unittest.main()