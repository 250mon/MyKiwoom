

class KiwoomInterface():
    def __init__(self, kiwoom):
        self.kiwoom = kiwoom

    def comm_connect(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.login_event_loop = QEventLoop()
        self.kiwoom.login_event_loop.exec_()


    def event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.kiwoom.login_event_loop.exit()

    def set_input_value(self, id, value):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no)
        self.kiwoom.tr_event_loop = QEventLoop()
        self.kiwoom.tr_event_loop.exec_()

    def comm_get_data(self, tr_code, record_name, index, item_name):
        ret = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", tr_code, record_name,
                               index, item_name)
        return ret.strip()

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString", trcode, rqname)
        return ret

    def receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unusde4):
        if next == '2':
            self.kiwoom.remained_data = True
        else:
            self.kiwoom.remained_data = False

        if rqname == "opt10081_req":
            self.kiwoom_opt10081(rqname, trcode)

        try:
            self.kiwoom.tr_event_loop.exit()
        except AttributeError:
            pass

