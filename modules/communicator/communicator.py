import socket
import time
import urllib.request
import requests
from enum import Enum

class MLLPDelimiter(Enum):
    START_OF_BLOCK = 0x0b
    END_OF_BLOCK = 0x1c
    CARRIAGE_RETURN = 0x0d

class PagerAPI(Enum):
    PAGE = "/page"
    SHUTDOWN = "/shutdown"

class Communicator():
    def __init__(self, mllp_address=None, pager_address=None):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if pager_address is not None:
            self.pager_address = pager_address.replace("https://", "").replace("http://", "")

        if mllp_address is not None:
            self.mllp_address = mllp_address.replace("https://", "").replace("http://", "")
            self.connect(mllp_address)

    # MLLP server
    def connect(self, mllp_address):
        host, port = mllp_address.split(":")
        self.socket.connect((host, int(port)))

    def receive(self):
        message = b""
        while MLLPDelimiter.END_OF_BLOCK.value not in message:
            buffer = self.socket.recv(1024)
            if len(buffer) == 0:
                return None
            message += buffer
        return message
    
    def acknowledge(self):
        current_time = time.strftime("%Y%m%d%H%M%S")
        ACK = [
            f"MSH|^~\&|||||{current_time}||ACK|||2.5",
            "MSA|AA",
        ]
        self.socket.sendall(self.to_mllp(ACK))

    def close(self):
        self.socket.close()

    # Packing and unpacking MLLP messages
    def to_mllp(self, segments):
        m = bytes(chr(MLLPDelimiter.START_OF_BLOCK.value), "ascii")
        m += bytes("\r".join(segments) + "\r", "ascii")
        m += bytes(chr(MLLPDelimiter.END_OF_BLOCK.value) + chr(MLLPDelimiter.CARRIAGE_RETURN.value), "ascii")
        return m
    
    # Pager server
    def page(self, mrn):
        r = requests.post(
            f"http://{self.pager_address}{PagerAPI.PAGE.value}",
            data=mrn
        )
        return r

    def shutdown_sever(self):
        r = urllib.request.urlopen(
            f"http://{self.pager_address}{PagerAPI.SHUTDOWN.value}"
        )

