from datetime import datetime

class MLLPMessage:
    def __init__(self):
        self.msg_timestamp = None
        self.mrn = None


class Adt_a01(MLLPMessage):
    def __init__(self):
        super().__init__()
        self.message_type = b'ADT^A01'
        self.name = None
        self.dob = None
        self.gender = None
        # self.nok = None
        # self.nok_name = None
        # self.nok_rs = None

    def process_message(self, message_segments: list[bytes]):
        msh = message_segments[0].split(b'|')
        pid = message_segments[1].split(b'|')
        self.msg_timestamp = msh[6].decode('utf-8')
        self.mrn = pid[3].decode('utf-8')
        self.name = pid[5].decode('utf-8')
        self.dob = datetime.strptime(pid[7].decode('utf-8'), '%Y%m%d').strftime('%Y-%m-%d')
        self.gender = pid[8]
        if not self.msg_timestamp or \
           not self.mrn or \
           not self.name or \
           not self.dob or \
           not self.gender:
            raise ValueError('Invalid message format: missing required fields')
        # parse gender after checking for missing fields, as gender = 0 may trigger a Exception
        if self.gender == b'M':
            self.gender = 0
        elif self.gender == b'F':
            self.gender = 1
        else:
            raise Exception('Error: expected binary gender (F or M) but found:',self.gender)
        return self


class Adt_a03(MLLPMessage):
    def __init__(self):
        super().__init__()
        self.message_type = b'ADT^A03'

    def process_message(self, message_segments: list[bytes]):
        msh = message_segments[0].split(b'|')
        pid = message_segments[1].split(b'|')
        self.msg_timestamp = msh[6].decode('utf-8')
        self.mrn = pid[3].decode('utf-8')
        if not self.msg_timestamp or not self.mrn:
            raise ValueError('Invalid message format: missing required fields')
        return self

class Oru_r01(MLLPMessage):
    def __init__(self):
        super().__init__()
        self.message_type = b'ORU^R01'
        self.obr_timestamp = None
        self.obx_type = None
        self.obx_value = None

    def process_message(self, message_segments: list[bytes]):
        msh = message_segments[0].split(b'|')
        pid = message_segments[1].split(b'|')
        obr = message_segments[2].split(b'|')
        obx = message_segments[3].split(b'|')
        self.msg_timestamp = msh[6].decode('utf-8')
        self.mrn = pid[3].decode('utf-8')
        self.obr_timestamp =  datetime.strptime(obr[7].decode('utf-8'), '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
        self.obx_type = obx[3].decode('utf-8')
        self.obx_value = float(obx[5])
        if not self.msg_timestamp or \
           not self.mrn or \
           not self.obr_timestamp or \
           not self.obx_type or \
           not self.obx_value:
            raise ValueError('Invalid message format: missing required fields')
        return self
