class Transaction():
    def __init__(self, kiwoom, rqname):
        self.kiwoom = kiwoom
        self.sender = kiwoom.sender
        self.receiver = kiwoom.receiver
        self.rqname = rqname
        self.trcode = self.rqname[:-4]

    def get_rqname(self):
        return self.rqname

    def handle(self):
        receiver = self.receiver
        rqname = self.rqname
        trcode = self.trcode

        _data_cnt = receiver.get_repeat_cnt(trcode, rqname)

        for i in range(_data_cnt):
            date = receiver.comm_get_data(trcode, rqname, i, "일자")
            open = receiver.comm_get_data(trcode, rqname, i, "시가")
            high = receiver.comm_get_data(trcode, rqname, i, "고가")
            low = receiver.comm_get_data(trcode, rqname, i, "저가")
            close = receiver.comm_get_data(trcode, rqname, i, "현재가")
            volume = receiver.comm_get_data(trcode, rqname, i, "거래량")
            print(date, open, high, low, close, volume)
