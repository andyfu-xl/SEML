from datetime import datetime
import logging

logging.basicConfig(filename='logs/error.log',level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class MLLPMessage:
    '''
    Base class for MLLP message types
    '''
    def __init__(self):
        self.msg_timestamp = None
        self.mrn = None


class Adt_a01(MLLPMessage):
    '''
    Class for ADT^A01 message type

    Attributes:
        message_type: str [Message type]
        name: str [Patient name]
        dob: str [Date of birth
        msg_timestamp: str [Timestamp of the message]
        mrn: int [Medical record number]
    '''
    def __init__(self):
        '''
        Constructor for ADT^A01 message type

        Attributes:
            message_type: str [Message type]
            name: str [Patient name]
            dob: str [Date of birth]
            gender: int [0 for Male, 1 for Female]
        '''
        super().__init__()
        self.message_type = 'ADT^A01'
        self.name = None
        self.dob = None
        self.gender = None

    def process_message(self, message_segments: list[str]):
        '''
        Processes the message and sets the attributes of the appropriate class

        Arguments:
            message_segments: list[str] [The list of segments of the message]
        '''
        try:
            msh = message_segments[0].split('|')
            pid = message_segments[1].split('|')
            self.msg_timestamp = msh[6]
            self.mrn = pid[3]
            self.name = pid[5]
            self.dob = datetime.strptime(pid[7], '%Y%m%d').strftime('%Y-%m-%d')
            self.gender = pid[8]
            if not self.msg_timestamp or \
                not self.mrn or \
                not self.name or \
                not self.dob or \
                not self.gender:
                logging.error('Invalid message format: missing required fields')
                return False
            # parse gender after checking for missing fields, as gender = 0 may trigger a Exception
            if self.gender == 'M':
                self.gender = 0
            elif self.gender == 'F':
                self.gender = 1
            else:
                logging.error(f'Error: expected binary gender (F or M) but found: {self.gender}')
                return False
        except Exception:
            logging.error('Invalid message format: missing required fields')
            return False
        return True


class Adt_a03(MLLPMessage):
    '''
    Class for ADT^A03 message type

    Attributes:
        message_type: str [Message type]
        msg_timestamp: str [Timestamp of the message]
        mrn: int [Medical record number]
    '''
    def __init__(self):
        '''
        Constructor for ADT^A03 message type

        Attributes:
            message_type: str [Message type]
        '''
        super().__init__()
        self.message_type = 'ADT^A03'

    def process_message(self, message_segments: list[str]):
        '''
        Processes the message and sets the attributes of the appropriate class
        
        Arguments:
            message_segments: list[str] [The list of segments of the message]
        '''
        try:
            msh = message_segments[0].split('|')
            pid = message_segments[1].split('|')
            self.msg_timestamp = msh[6]
            self.mrn = pid[3]
            if not self.msg_timestamp or not self.mrn:
                logging.error('Invalid message format: missing required fields')
                return False
        except Exception:
            logging.error('Invalid message format: missing required fields')
            return False
        return True

class Oru_r01(MLLPMessage):
    '''
    Class for ORU^R01 message type

    Attributes:
        message_type: str [Message type]
        obr_timestamp: str [Timestamp of the observation]
        obx_type: str [Type of observation]
        obx_value: float [Value of the observation]
        msg_timestamp: str [Timestamp of the message]
        mrn: int [Medical record number]
    '''
    def __init__(self):
        '''
        Constructor for ORU^R01 message type

        Attributes:
            message_type: str [Message type]
            obr_timestamp: str [Timestamp of the observation]
            obx_type: str [Type of observation]
            obx_value: float [Value of the observation]
        '''
        super().__init__()
        self.message_type = 'ORU^R01'
        self.obr_timestamp = None
        self.obx_type = None
        self.obx_value = None

    def process_message(self, message_segments: list[str]):
        '''
        Processes the message and sets the attributes of the appropriate class

        Arguments:
            message_segments: list[str] [The list of segments of the message]
        '''
        try:
            msh = message_segments[0].split('|')
            pid = message_segments[1].split('|')
            obr = message_segments[2].split('|')
            obx = message_segments[3].split('|')
            self.msg_timestamp = msh[6]
            self.mrn = pid[3]
            self.obr_timestamp =  datetime.strptime(obr[7], '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
            self.obx_type = obx[3]
            self.obx_value = float(obx[5])
            if not self.msg_timestamp or \
            not self.mrn or \
            not self.obr_timestamp or \
            not self.obx_type or \
            not self.obx_value:
                logging.error('Invalid message format: missing required fields')
                return False
        except Exception:
            logging.error('Invalid message format: missing required fields')
            return False
        return True
