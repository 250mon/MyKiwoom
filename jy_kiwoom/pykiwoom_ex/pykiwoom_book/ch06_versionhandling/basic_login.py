from PyQt5.QAxContainer import *
from kwm_method_api import *


class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self.slot_login)
        self.ocx.dynamicCall("CommConnect()")
        # self.kiwoom = Kiwoom()
        # self.kiwoom.CommConnect(block=True)

    def slot_login(self, err_code):
        print(err_code)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    # event loop
    app.exec_()
