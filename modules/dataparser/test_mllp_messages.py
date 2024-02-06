import socket
import time
def build_mllp_message(hl7_message):
    VT = '\x0b'  # Start Block Character
    FS_CR = '\x1c\x0d'  # End Block Character
    return f"{VT}{hl7_message}{FS_CR}"

def send_mllp_message(host, port, hl7_message):
	mllp_message = build_mllp_message(hl7_message)
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		# Connect to the server
		sock.connect((host, port))
		# Send the MLLP message
		while True:
			sock.sendall(mllp_message.encode())
			time.sleep(3)
		# Optionally, receive a response here if the server sends any
		# response = sock.recv(1024)
	# Connection will be automatically closed when exiting the with block

# Send the message
if __name__ == "__main__":
    # Example HL7 Message
	hl7_message = "MSH|^~\&|||||20240129093837||ACK|||2.5\rMSA|AA"

	# Host and port of the HL7 server
	host = "0.0.0.0"
	port = 8440
	send_mllp_message(host, port, hl7_message)