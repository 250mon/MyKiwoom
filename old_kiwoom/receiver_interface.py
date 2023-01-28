class ReceiverInterface():
    def __init__(self, kiwoom):
        self.kiwoom = kiwoom
        self.remained_data = False

    def is_data_remaining(self):
        return self.remained_data

    def comm_get_data(self, tr_code, record_name, index, item_name):
        ret = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString", tr_code, record_name,
                                 index, item_name)
        return ret.strip()

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString", trcode, rqname)
        return ret

    def receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unusde4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        self.kiwoom.tr_handler[rqname].handle_response()

        try:
            self.kiwoom.tr_event_loop.exit()
        except AttributeError:
            pass