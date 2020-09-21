import sys
import time
from PyQt5.QtWidgets import *
from kiwoom_interface import Kiwoom
from transaction import Transaction


if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.connect()

    tr_opt10081 = Transaction(kiwoom, 'opt10081_req')
    kiwoom.reg_transaction(tr_opt10081)
    tr_opt10081.send_request()
