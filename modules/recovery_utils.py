import torch
import os

from modules.dataparser import DataParser
from modules.database import Database
from modules.preprocessor import Preprocessor
from modules.model import load_model, inference
from modules.module_logging import main_logger, set_log_path
import modules.metrics_monitoring as monitoring

def read_missed_messages():

	# Specify the path and filename
	directory = "/app/data/"
	filename = "missed_messages.txt"
	file_path = os.path.join(directory, filename)

	# Check if the file exists
	if os.path.isfile(file_path):
		# File exists, so read it
		with open(file_path, 'r') as file:
			content = file.read()		
		# delete the file
		os.remove(file_path)
		print(f"File {filename} has been deleted.")
		return content.split("MSH")
	return None

def recover_messages(missed_messages, dataparser, preprocessor, model, database, device):
	for message in missed_messages:
		# Pass the message
		# TODO: Add monitoring for recovered messages

		if message[:3] != "|^~":
			continue
		message = "MSH" + message.replace("\n", "\r")
		# Convert message to bytes
		message = message.encode('utf-8')


		#monitoring.increase_message_received()
		
		# Pass the message to data parser
		parsed_message = dataparser.parse_message(message)

		if parsed_message == None:
			monitoring.increase_invalid_messages()
			continue
		elif parsed_message.message_type == 'ORU^R01':
			monitoring.increase_blood_test_messages()
			monitoring.increase_sum_blood_test_results(parsed_message.obx_value)
			monitoring.update_running_mean_blood_test_results()

		mrn = parsed_message.mrn
		timestamp = parsed_message.msg_timestamp

		# Process message
		preprocessed_message = preprocessor.preprocess(parsed_message)
		
		# Perform inference
		has_aki = False
		if preprocessed_message is not None:
			has_aki = inference(model, preprocessed_message.to(device))

		if has_aki:
			database.is_positive(mrn, timestamp)