import socket
import time
import urllib.request
from enum import Enum

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
    def __init__(self, mllp_address=None, pager_address=None):
        '''Constructor for the Communicator class.'''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if pager_address is not None:
            self.pager_address = pager_address.replace("https://", "").replace("http://", "")

        if mllp_address is not None:
            self.mllp_address = mllp_address.replace("https://", "").replace("http://", "")
            self.connect(mllp_address)

    # MLLP server
    def connect(self, mllp_address):
        '''Connects to the MLLP server.'''
        host, port = mllp_address.split(":")
        self.socket.connect((host, int(port)))

    def receive(self):
        '''Receives a message from the MLLP server.

        In the case where the message is sent partially, the function will wait and 
        continue to receive the message until the end of the message is reached.

        Returns:
            - message (bytes): The message received from the MLLP server.
        '''
        message = b""
        while MLLPDelimiter.END_OF_BLOCK.value not in message:
            buffer = self.socket.recv(1024)
            if len(buffer) == 0:
                return None
            message += buffer
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
    def page(self, mrn):
        '''Sends a page request to the Pager server.

        Args:
            - mrn (str): The medical record number of the patient to page.
        '''
        mrn_bytes = bytes(mrn, "ascii")
        r = urllib.request.urlopen(
            f"http://{self.pager_address}{PagerAPI.PAGE.value}", 
            data=mrn_bytes
        )
        return r

    def shutdown_server(self):
        '''Sends a shutdown request to the Pager server.'''
        r = urllib.request.urlopen(
            f"http://{self.pager_address}{PagerAPI.SHUTDOWN.value}"
        )

