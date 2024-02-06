import torch
import torch.nn as nn

class LSTMModel(nn.Module):
	def __init__(self, input_dim, hidden_dim, output_dim, num_layers):
		super(LSTMModel, self).__init__()
		self.hidden_dim = hidden_dim
		self.num_layers = num_layers
		# LSTM layer
		self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
		
		# Fully connected layer
		self.fc = nn.Linear(hidden_dim, output_dim)

	def forward(self, x):
		# Initialize hidden state and cell state
		h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
		c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
		# Forward propagate LSTM
		out, _ = self.lstm(x, (h0, c0))
		
		# Pass the output of the last time step to the classifier
		out = self.fc(out[:, -1, :])
		return out