from . import messagetypes

class DataParser():
    def __init__(self):
        self.ORU = 'ORU^R01'
        self.A01 = 'ADT^A01'
        self.A03 = 'ADT^A03'

    def remove_start_and_end(self, message: bytes, start=b'\x0b', end=b'\x1c'):
        message = message.replace(start, b'', 1)
        message = message.replace(end, b'', 1)
        return message
    
    def segment_message(self, message: bytes, segment='\r'):
        segments = message.split(segment)
        segments = [x for x in segments if x]
        return segments

    def get_message_type(self, message_segment: list):
        msh_segment = message_segment[0]
        msg_type = msh_segment.split('|')[8]
        if msg_type == self.ORU:
            return self.ORU
        elif msg_type == self.A01:
            return self.A01
        elif msg_type == self.A03:
            return self.A03
        else:
            raise ValueError('Invalid message type:', msg_type)

    def parse_message(self, message: bytes):
        message = self.remove_start_and_end(message)
        message = message.decode('utf-8')
        message_segments = self.segment_message(message)
        msg_type = self.get_message_type(message_segments)
        message_obj = None
        if msg_type == self.ORU:
            message_obj = messagetypes.Oru_r01()
            message_obj.process_message(message_segments)
            return message_obj
        elif msg_type == self.A01:
            message_obj = messagetypes.Adt_a01()
            message_obj.process_message(message_segments)
            return message_obj
        elif msg_type == self.A03:
            message_obj = messagetypes.Adt_a03()
            message_obj.process_message(message_segments)
            return message_obj
        else:
            raise ValueError('Invalid message type:', msg_type)

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
    
