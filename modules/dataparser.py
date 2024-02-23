from . import messagetypes
# import messagetypes
import logging

class DataParser():
    '''
    Main class for parsing HL7 messages
    Message types that are supported: ORU^R01, ADT^A01, ADT^A03
    Attributes:
        ORU: str
        A01: str
        A03: str
    '''
    def __init__(self):
        '''
        Constructor for DataParser with supported message types
            self.ORU: str
            self.A01: str
            self.A03: str
        '''
        self.ORU = 'ORU^R01'
        self.A01 = 'ADT^A01'
        self.A03 = 'ADT^A03'

    def remove_start_and_end(self, message: bytes, start=b'\x0b', end=b'\x1c'):
        '''
        Removes the start and end characters from the message
        Default start character is '\x0b'
        Default end character is '\x1c'
        
        Arguments:
            message: bytes [The message to be processed]
            start: bytes [The start character of the message]
            end: bytes [The end character of the message]
        '''
        message = message.replace(start, b'', 1)
        message = message.replace(end, b'', 1)
        return message
    
    def segment_message(self, message: bytes, segment='\r'):
        '''
        Splits the message into segments.
        Default split character is '\r'
        
        Arguments:
            message: bytes [The message to be processed]
            segment: str [The character to split the message by]
        '''
        segments = message.split(segment)
        segments = [x for x in segments if x]
        return segments

    def get_message_type(self, message_segment: list[str]):
        '''
        Returns the message type of the message by parsing the MSH segment
        which by HL7 messages is the first segment of the message
        
        Argument:
            message_segment: list(str) [The list of segments of the message]
        '''
        try:
            msh_segment = message_segment[0]
            msg_type = msh_segment.split('|')[8]
            if msg_type == self.ORU:
                return self.ORU
            elif msg_type == self.A01:
                return self.A01
            elif msg_type == self.A03:
                return self.A03
            else:
                logging.error(f'Invalid message type: {msg_type}')
                return msg_type
        except Exception:
            logging.error('Invalid message format: missing required fields')
            return None

    def parse_message(self, message: bytes):
        '''
        Parses the message and returns the message object of the appropriate type
        Message type: ORU^R01, ADT^A01, ADT^A03
        
        Argument:
            message: bytes [The message to be processed]
        '''
        message = self.remove_start_and_end(message)
        message = message.decode('utf-8')
        message_segments = self.segment_message(message)
        msg_type = self.get_message_type(message_segments)
        message_obj = None
        if msg_type == self.ORU:
            message_obj = messagetypes.Oru_r01()
            is_processed = message_obj.process_message(message_segments)
        elif msg_type == self.A01:
            message_obj = messagetypes.Adt_a01()
            is_processed = message_obj.process_message(message_segments)
        elif msg_type == self.A03:
            message_obj = messagetypes.Adt_a03()
            is_processed = message_obj.process_message(message_segments)
        else:
            logging.error(f'Error while parsing: {message}')
            return None
        
        if is_processed:
            return message_obj
        else:
            return None

if __name__ == '__main__':
    adt_ao1_message = b'\x0bMSH|^~\\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5\rPID|1||497030||ROSCOE DOHERTY||19870515|M\r\x1c\r'
    adt_ao3_message = b'\x0bMSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331035800||ADT^A03|||2.5\rPID|1||829339\r\x1c\r'
    oru_message = b'\x0bMSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240331113300||ORU^R01|||2.5\rPID|1||257406\rOBR|1||||||20240331113300\rOBX|1|SN|CREATININE||92.95579346699137\r\x1c\r'
    dp = DataParser()
    msg = dp.parse_message(oru_message)
    print(msg.msg_timestamp)
    print(msg.mrn)
    print(msg.obr_timestamp)
    print(msg.obx_type)
    print(msg.obx_value)
    
