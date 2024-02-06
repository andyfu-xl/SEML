import torch
from tqdm import tqdm
from sklearn.metrics import f1_score, fbeta_score


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
		return predicted.cpu().numpy()[0][1]