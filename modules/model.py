import csv
import torch
import torch.nn as nn
from tqdm import tqdm
from sklearn.metrics import f1_score, fbeta_score
	
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
	
def train(num_epochs, train_loader, model, criterion, optimizer, device):
	model.train()
	model.to(device)
	for epoch in range(num_epochs):
		train_loader = tqdm(train_loader)
		total_loss = 0
		for batch_idx, (inputs, labels) in enumerate(train_loader):
			inputs, labels = inputs.to(device), labels.to(device)
			
			optimizer.zero_grad()

			# Forward pass
			outputs = model(inputs)
			
			# Compute the loss
			loss = criterion(outputs, labels.long())
			
			# Backward pass and optimize
			loss.backward()
			optimizer.step()

			total_loss += loss.item()

		print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss / len(train_loader)}')


def eval(data_loader, model, device):
	model.to(device)
	model.eval()

	# Initialize variables to track the metrics
	total = 0
	correct = 0
	true_labels = []
	predicted_labels = []
	
	with torch.no_grad():
		val_loader = tqdm(data_loader)
		for batch_idx, (inputs, labels) in enumerate(val_loader):
			inputs, labels = inputs.to(device), labels.to(device)

			# Forward pass
			outputs = model(inputs)
			# Convert logits to probabilities and then to predicted class (0 or 1)
			predicted = torch.sigmoid(outputs).round()

			# Store predictions and true labels
			true_labels.extend(labels.cpu().numpy())
			predicted_labels.extend(predicted.cpu().numpy())

			# Update total and correct counts
			total += labels.size(0)
			correct += (predicted == labels).sum().item()

	# Calculate accuracy, F3 and F1 scores
	accuracy = correct / total
	print(f'Validation Accuracy: {accuracy:.4f}')

	pred_labels = [list[1] for list in predicted_labels]
	f3 = fbeta_score(true_labels, pred_labels, beta=3)
	print(f'Validation F3 Score: {f3:.4f}')

	f1 = f1_score(true_labels, pred_labels, average='binary')
	print(f'Validation F1 Score: {f1:.4f}')

def inference(model, input_data, device):
	model.to(device)
	model.eval()
	with torch.no_grad():
		input_data = input_data.to(device)
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

