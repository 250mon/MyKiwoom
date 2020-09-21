import pandas as pd
import time

TR_REQ_TIME_INTERVAL = 0.2


class Transaction():
    def __init__(self, kiwoom, rqname):
        self.kiwoom = kiwoom
        self.sender = kiwoom.sender
        self.receiver = kiwoom.receiver
        self.rqname = rqname
        self.trcode = self.rqname[:-4]
        self.input = {
            "종목코드": "039490",
            "기준일자": "20170224",
            "수정주가구분": 1,
        }
        self.output = {
            '일자': [],
            '시가': [],
            '고가': [],
            '저가': [],
            '현재가': [],
            '거래량': [],
        }

    def get_rqname(self):
        return self.rqname

    def handle_response(self):
        receiver = self.receiver
        rqname = self.rqname
        trcode = self.trcode

        _data_cnt = receiver.get_repeat_cnt(trcode, rqname)

        for i in range(_data_cnt):
            for col in self.output.keys():
                received_data = receiver.comm_get_data(trcode, rqname, i, col)
                self.output[col].append(received_data)

        df = pd.DataFrame(self.output, columns=['시가', '고가', '저가', '현재가', '거래량'],
                          index=self.output['일자'])
        print(df)

    def send_request(self):
        for col in self.input.keys():
            self.sender.set_input_value(col, self.input[col])
        self.sender.comm_rq_data(self.rqname, self.trcode, 0, "0101")

        while self.receiver.is_data_remaining():
            time.sleep(TR_REQ_TIME_INTERVAL)
            for col in self.input.keys():
                self.sender.set_input_value(col, self.input[col])
                self.sender.comm_rq_data(self.rqname, self.trcode, 2, "0101")
