from PyQt5.QtCore import QEventLoop


class ConnectorInterface():
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

