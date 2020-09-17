import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from kiwoom_interface import KiwoomInterface
import time

TR_REQ_TIME_INTERVAL = 0.2


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self.kiwoom_interface = KiwoomInterface(self)
        self._create_kiwoom_instance()
        self._set_signal_slots()

        self.remained_data = False

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self.kiwoom_interface.event_connect)
        self.OnReceiveTrData.connect(self.kiwoom_interface.receive_tr_data)

    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString", code)
        return code_name

    def _opt10081(self, rqname, trcode):
        data_cnt = self.kiwoom_interface.get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self.kiwoom_interface.comm_get_data(trcode, rqname, i, "일자")
            open = self.kiwoom_interface.comm_get_data(trcode, rqname, i, "시가")
            high = self.kiwoom_interface.comm_get_data(trcode, rqname, i, "고가")
            low = self.kiwoom_interface.comm_get_data(trcode, rqname, i, "저가")
            close = self.kiwoom_interface.comm_get_data(trcode, rqname, i, "현재가")
            volume = self.kiwoom_interface.comm_get_data(trcode, rqname, i, "거래량")
            print(date, open, high, low, close, volume)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    k_interface = kiwoom.kiwoom_interface
    kiwoom.comm_connect()

    # Get code list
    # code_list = kiwoom.get_code_list_by_market('10')
    # for code in code_list:
    #     code_name = kiwoom.get_master_code_name(code)
    #     print(code_name, end=" ")

    # Day candle chart; opt10081 tr request
    k_interface.set_input_value("종목코드", "039490")
    k_interface.set_input_value("기준일자", "20170224")
    k_interface.set_input_value("수정주가구분", 1)
    k_interface.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

    while kiwoom.remained_data == True:
        time.sleep(TR_REQ_TIME_INTERVAL)
        k_interface.set_input_value("종목코드", "039490")
        k_interface.set_input_value("기준일자", "20170224")
        k_interface.set_input_value("수정주가구분", 1)
        k_interface.comm_rq_data("opt10081_req", "opt10081", 2, "0101")
