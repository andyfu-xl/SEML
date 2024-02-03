
class MLLPMessage:
    def __init__(self):
        self.msg_timestamp = None
        self.mrn = None


class Adt_a01(MLLPMessage):
    def __init__(self):
        super().__init__()
        self.message_type = b'ADT_A01'
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
        self.dob = pid[7]
        self.gender = pid[8]
        return True


class Adt_a03(MLLPMessage):
    def __init__(self):
        super().__init__()
        self.message_type = b'ADT_A03'

    def process_message(self, message_segments: list[bytes]):
        msh = message_segments[0].split(b'|')
        pid = message_segments[1].split(b'|')
        self.msg_timestamp = msh[6]
        self.mrn = pid[3]
        return True

class Oru_r01(MLLPMessage):
    def __init__(self):
        super().__init__()
        self.message_type = b'ORU_R01'
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
        return True