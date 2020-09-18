import sys
import time
from PyQt5.QtWidgets import *
from kiwoom_interface import Kiwoom
from transaction import Transaction

TR_REQ_TIME_INTERVAL = 0.2

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.connect()
    tr_opt10081 = Transaction(kiwoom, 'opt10081_req')
    kiwoom.reg_transaction(tr_opt10081)

    # Day candle chart; opt10081 tr request
    kiwoom.sender.set_input_value("종목코드", "039490")
    kiwoom.sender.set_input_value("기준일자", "20170224")
    kiwoom.sender.set_input_value("수정주가구분", 1)
    kiwoom.sender.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

    while kiwoom.receiver.is_data_remaining():
        time.sleep(TR_REQ_TIME_INTERVAL)
        kiwoom.sender.set_input_value("종목코드", "039490")
        kiwoom.sender.set_input_value("기준일자", "20170224")
        kiwoom.sender.set_input_value("수정주가구분", 1)
        kiwoom.sender.comm_rq_data("opt10081_req", "opt10081", 2, "0101")

