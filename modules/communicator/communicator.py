import socket
import time
import urllib.request
from enum import Enum
from collections import deque 

class MLLPDelimiter(Enum):
    START_OF_BLOCK = 0x0b
    END_OF_BLOCK = 0x1c
    CARRIAGE_RETURN = 0x0d

class PagerAPI(Enum):
    PAGE = "/page"
    SHUTDOWN = "/shutdown"

class Communicator():
    '''Communicator class for sending and receiving messages from MLLP and Pager servers.
    Attributes:
        - mllp_address (str): The address of the MLLP server.
        - pager_address (str): The address of the Pager server.
    '''
    def __init__(self, mllp_address=None, pager_address=None, communicator_logs=None):
        '''Constructor for the Communicator class.'''
        self.page_queue = deque()

        if communicator_logs is not None:
            self.communicator_logs = communicator_logs

        if pager_address is not None:
            self.pager_address = pager_address.replace("https://", "").replace("http://", "")

        if mllp_address is not None:
            self.mllp_address = mllp_address.replace("https://", "").replace("http://", "")
            self.host, self.port = self.mllp_address.split(":")
            self.connect()

    # MLLP server
    def connect(self):
        '''
        Connects to the MLLP server. Retries 10 times with an increasing delay if the connection fails.
        '''
        max_retries = 10
        retry_delay = 5  # Initial delay of 5 seconds
        delay_increment = 2

        for _ in range(max_retries):
            try:
                print(f"Attempting to connect to {self.host}:{self.port}...")
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, int(self.port)))
                print(f"Connected to MLLP server at {self.host}:{self.port}.")
                self.communicator_logs['connect'].inc()
                return
            except Exception as e:
                print(f"Error occurred while trying to connect to MLLP server: {e}")
                print(f"Retrying in {retry_delay} seconds...")
                self.close()
                time.sleep(retry_delay)
                retry_delay += delay_increment  # Linear backoff

        print("Maximum retry attempts reached. Could not connect to MLLP server.")
        exit(1)

    def receive(self):
        '''Receives a message from the MLLP server.

        In the case where the message is sent partially, the function will wait and 
        continue to receive the message until the end of the message is reached.

        Returns:
            - message (bytes): The message received from the MLLP server.
        '''
        try:
            message = b""
            while MLLPDelimiter.END_OF_BLOCK.value not in message:
                buffer = self.socket.recv(1024)
                if len(buffer) == 0:
                    return None
                message += buffer
            return message
        except Exception as e:
            print(f"Error occurred while trying to receive message from MLLP server: {e}")
            self.connect()
            message = self.receive()
            return message
    
    def acknowledge(self):
        '''Sends an acknowledgment message to the MLLP server with the current time.'''
        current_time = time.strftime("%Y%m%d%H%M%S")
        ACK = [
            f"MSH|^~\&|||||{current_time}||ACK|||2.5",
            "MSA|AA",
        ]
        self.socket.sendall(self.to_mllp(ACK))

    def close(self):
        '''Closes the connection to the MLLP server.'''
        self.socket.close()

    # Packing and unpacking MLLP messages
    def to_mllp(self, segments):
        '''Packs the segments into an MLLP message.'''
        m = bytes(chr(MLLPDelimiter.START_OF_BLOCK.value), "ascii")
        m += bytes("\r".join(segments) + "\r", "ascii")
        m += bytes(chr(MLLPDelimiter.END_OF_BLOCK.value) + chr(MLLPDelimiter.CARRIAGE_RETURN.value), "ascii")
        return m
    
    # Pager server
    def page(self, mrn, timestamp=None):
        '''Sends a page request to the Pager server.

        Args:
            - mrn (str): The medical record number of the patient to page.
            - timestamp (str): The timestamp of the message.
        '''
        self.page_queue.append((mrn, timestamp))
        try:
            while len(self.page_queue) > 0:
                queued_mrn, queued_timestamp = self.page_queue.popleft()
                request = queued_mrn
                if timestamp is not None:
                    request = f"{queued_mrn},{queued_timestamp}"
                request_bytes = bytes(request, "ascii")

                r = urllib.request.urlopen(
                    f"http://{self.pager_address}{PagerAPI.PAGE.value}", 
                    data=request_bytes
                )
                print(f"Patient {queued_mrn} has been paged.")
        except Exception as e:
            print(f"Error occurred while trying to page {queued_mrn}: {e}")
            self.communicator_logs['page_failures'].inc()
            self.page_queue.appendleft((queued_mrn, queued_timestamp))

    def shutdown_server(self):
        '''Sends a shutdown request to the Pager server.'''
        r = urllib.request.urlopen(
            f"http://{self.pager_address}{PagerAPI.SHUTDOWN.value}"
        )

