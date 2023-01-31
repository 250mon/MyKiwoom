import datetime
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import QTimer, pyqtSlot
import multiprocessing as mp
from pykiwoom import KiwoomManager
from worker import Worker


# This is the main thread
# 1. It provides user interface by handling the GUI components
# 2. It creates a single instance of KiwoomManager to communicate Kiwoom server
# 3. It creates 5 worker threads to handle data and cmd for each ticker and
#    also create 5 pairs of queues to communicate with the threads
class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.km = None
        self.accno = None
        self.initUI()

    def connect_km(self):
        self.km = KiwoomManager(False)
        self.accno = None
        self.get_account_no()

    def get_account_no(self):
        self.km.put_method(("GetLoginInfo", "ACCNO"))
        accounts = self.km.get_method()
        if accounts:
            # set account number
            self.accno = accounts[0]
            print(f'set account number {self.accno}')
        else:
            raise Exception('Error: No account number!!!')

    def initUI(self):
        self.setWindowTitle("Test")
        self.conn_btn = QPushButton("Connect", self)
        self.conn_btn.clicked.connect(self.conn_btn_clicked)
        self.disconn_btn = QPushButton("Disconnect", self)
        self.disconn_btn.clicked.connect(self.disconn_btn_clicked)
        self.disconn_btn.setEnabled(False)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.conn_btn)
        hbox.addWidget(self.disconn_btn)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)
        self.setGeometry(300, 300, 300, 400)

    def conn_btn_clicked(self):
        self.connect_km()
        self.conn_btn.setEnabled(False)
        self.disconn_btn.setEnabled(True)

    def disconn_btn_clicked(self):
        print("btn_clicked")
        self.km.rq_handler.kill()
        del self.km
        self.km = None
        print("self.km deleted")
        self.conn_btn.setEnabled(True)
        self.disconn_btn.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())