# from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QEventLoop
from PyQt5.QAxContainer import QAxWidget
from PyQt5Singleton import Singleton
from logging_handler import LoggingHandler


class Kwm(QObject, LoggingHandler, metaclass=Singleton):
    TR_SCREEN_NUMBER_MAX = 2999
    REAL_SCREEN_NUMBER_MAX = 3999
    def __init__(self, login=True):
        super().__init__()
        # OCX instance
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        # state variables
        self.connected = False
        # signal slots
        self.ocx.OnEventConnect.connect(self.OnEventConnect)
        # a unique screen number
        self.screen_no = {"Tr": 2000, "Real": 3000}
        # loop for block until login is complete
        self.login_event_loop = QEventLoop()
        # login
        if login:
            self.CommConnect()

    def get_ocx(self):
        """
        Returns ocx instance which is singleton
        :return:
        """
        return self.ocx

    def get_conn_state(self):
        """
        Returns connection state
        Its connection state reflects only the initial connection status
        For the connection status during a session, Kiwoom API needs to be
        called instead
        :return:
        """
        return self.connected
    def OnEventConnect(self, err_code):
        if err_code == 0:
            print("Connect successfully")
            self.connected = True
        else:
            print(f"Failed to connect (err_code: {err_code}!!!")
            self.connected = False

        self.login_event_loop.exit()

    def CommConnect(self):
        """
        Connect to Kiwoom by run login window
        :return: None
        """
        self.ocx.dynamicCall("CommConnect()")
        self.login_event_loop.exec_()

    def get_screen_no(self, type="Tr"):
        """
        Returns a unique screen number
        :param type: "Tr" | "Real"
        :return:
        """
        sn = self.screen_no[type]
        self.log.info(f"{type} screen number is being set... {sn}")
        if type == "Tr" and sn < self.TR_SCREEN_NUMBER_MAX:
            self.screen_no[type] += 1
        elif type == "Real" and sn < self.REAL_SCREEN_NUMBER_MAX:
            self.screen_no[type] += 1
        else:
            self.log.error(f"{type} screen number is exceeding max")

        return str(sn)