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
        self.msg_timestamp = msh[6]
        self.mrn = pid[3]
        self.name = pid[5]
        self.dob = datetime.strptime(pid[7].decode('utf-8'), '%Y%m%d').strftime('%Y-%m-%d')
        self.gender = pid[8]
        if not self.msg_timestamp or \
           not self.mrn or \
           not self.name or \
           not self.dob or \
           not self.gender:
            raise ValueError('Invalid message format: missing required fields')
        return self


class Adt_a03(MLLPMessage):
    def __init__(self):
        super().__init__()
        self.message_type = b'ADT^A03'

    def process_message(self, message_segments: list[bytes]):
        msh = message_segments[0].split(b'|')
        pid = message_segments[1].split(b'|')
        self.msg_timestamp = msh[6]
        self.mrn = pid[3]
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
        self.msg_timestamp = msh[6]
        self.mrn = pid[3]
        self.obr_timestamp = obr[7]
        self.obx_type = obx[3]
        self.obx_value = float(obx[5])
        if not self.msg_timestamp or \
           not self.mrn or \
           not self.obr_timestamp or \
           not self.obx_type or \
           not self.obx_value:
            raise ValueError('Invalid message format: missing required fields')
        return self