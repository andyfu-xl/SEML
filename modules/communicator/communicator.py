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
    def __init__(self, host=None, mllp_port=None, pager_port=None):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.pager_port = pager_port

        if host is not None and mllp_port is not None:
            self.connect(host, mllp_port)

    # MLLP server
    def connect(self, host, port):
        self.socket.connect((host, port))

    def receive(self):
        buffer = self.socket.recv(1024)
        if len(buffer) == 0:
            return None
        return buffer
    
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
    
    def from_mllp(self, buffer):
        return str(buffer[1:-3], "ascii").split("\r")

    # Pager server
    def page(self, mrn):
        mrn_bytes = bytes(mrn, "ascii")
        r = urllib.request.urlopen(
            f"http://{self.host}:{self.pager_port}{PagerAPI.PAGE.value}", 
            data=mrn_bytes
        )
        return r

    def shutdown_sever(self):
        r = urllib.request.urlopen(
            f"http://{self.host}:{self.pager_port}{PagerAPI.SHUTDOWN.value}"
        )
