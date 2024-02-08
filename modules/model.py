import csv
import torch
import torch.nn as nn
	
####################
###### Model #######
####################

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
	
####################
### Model Utils ####
####################	

def load_model(model_path):
	model = LSTMModel(input_dim=4, hidden_dim=64, output_dim=2, num_layers=2)
	model.load_state_dict(torch.load(model_path))
	return model

def inference(model, input_data):
	model.eval()
	with torch.no_grad():
		outputs = model(input_data)
		predicted = torch.sigmoid(outputs).round()
		return int(predicted.cpu().numpy()[0][1])
	
def save_inference_results(pred_labels, dates, output_path):
    print("Saving the inference results...")
    w = csv.writer(open(output_path, "w"))
    w.writerow(("mrn","date"))
    for i in range(len(pred_labels)):	
        w.writerow([pred_labels[i], dates[i]])
    print("The inference results have been saved to", output_path)

