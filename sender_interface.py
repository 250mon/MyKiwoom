from PyQt5.QtCore import QEventLoop


class SenderInterface():
    def __init__(self, kiwoom):
        self.kiwoom = kiwoom

    def set_input_value(self, id, value):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no)
        self.kiwoom.tr_event_loop = QEventLoop()
        self.kiwoom.tr_event_loop.exec_()