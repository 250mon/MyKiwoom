import sys 
from PyQt5.QtWidgets import *
from pykiwoom.kiwoom_q_manager import KwmQMgr

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kwm_q = KwmQMgr()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()