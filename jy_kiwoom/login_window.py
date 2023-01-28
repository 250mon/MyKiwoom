import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
from PyQt5.QAxContainer import QAxWidget
import pythoncom
import time
import multiprocessing as mp


#################################
# login window
#################################

class LoginWindow(QMainWindow):
    app = QApplication(sys.argv)

    def __init__(self, q):
        super().__init__()
        self.login_status = False
        self.q = q
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self.slot_login)

        self.login()

    def login(self):
        self.ocx.dynamicCall("commConnect()")
        while not self.login_status:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.0001)


    def slot_login(self, err_code):
        self.login_status = True
        print("login is complete")
        self.q.put('a')


if __name__ == "__main__":
    q = mp.Manager().Queue()
    sub_proc = mp.Process(target=LoginWindow, name="Sub Process", args=(q,), daemon=True)
    sub_proc.start()

