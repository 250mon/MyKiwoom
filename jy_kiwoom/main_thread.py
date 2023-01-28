import datetime
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
)
from PyQt5.QtCore import (
    Qt,
    QObject,
    QThread,
    QTimer,
    pyqtSignal,
    pyqtSlot
)
import multiprocessing as mp
from pykiwoom import KiwoomManager
from worker import Worker
import logging

logging.basicConfig(format="%(message)s", level=logging.INFO)

class MyWindow(QMainWindow, QObject):
    finish_worker = pyqtSignal()
    km_changed = pyqtSignal(object)
    trigger_test = pyqtSignal()

    def __init__(self):
        super().__init__()
        # data from the worker thread
        self.to_worker_q = mp.Manager().Queue()
        # command to the worker thread
        self.from_worker_q = mp.Manager().Queue()

        self.worker = None
        self.thread = None

        # connect to Kiwoom server
        self.km = None
        self.accno = None
        self.timer1 = QTimer(self)

        self.setupUi()
        self.setup_timer()
        self.connect_and_start()

    def setupUi(self):
        self.setWindowTitle("JY Security powered by Kiwoom")
        self.setGeometry(300, 300, 300, 400)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Create and connect widgets
        self.worker_label = QLabel(f"Waiting for message from worker ...")
        self.worker_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.conn_btn = QPushButton("Connect", self)
        self.conn_btn.clicked.connect(self.conn_btn_clicked)
        self.conn_btn.setEnabled(False)
        self.disconn_btn = QPushButton("Disconnect", self)
        self.disconn_btn.clicked.connect(self.disconn_btn_clicked)
        self.register_btn = QPushButton("Register real", self)
        self.register_btn.clicked.connect(self.register_btn_clicked)
        self.test_btn = QPushButton("Test", self)
        self.test_btn.clicked.connect(self.test_btn_clicked)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.conn_btn)
        hbox.addStretch(1)
        hbox.addWidget(self.disconn_btn)
        hbox.addStretch(1)

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(self.register_btn)
        # hbox1.addStretch(1)
        # hbox1.addWidget(self.disconn_btn)
        hbox1.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.worker_label)
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox1)
        vbox.addStretch(1)

        self.centralWidget.setLayout(vbox)

    def setup_timer(self):
        self.timer1.setInterval(3000)
        self.timer1.timeout.connect(self.time_out_event)

    def connect_and_start(self):
        # connect to the server
        self.km = KiwoomManager()
        # initially get account number
        self.get_account_no()
        self.statusBar().showMessage(f"ACC {self.accno} connected")

        if self.worker is None and self.thread is None:
            self.run_thread_task()
        self.start_main_system()

    def start_main_system(self):
        # 데이터가 들어오는 속도는 주문보다 빠름
        logging.info("Main timer starts")
        self.timer1.start()

    def get_account_no(self):
        self.km.put_method(("GetLoginInfo", "ACCNO"))
        accounts = self.km.get_method()
        if accounts:
            # set account number
            self.accno = accounts[0]
            logging.info(f'set account number {self.accno}')
        else:
            raise Exception('Error: No account number!!!')

    def conn_btn_clicked(self):
        self.connect_and_start()
        self.km_changed.emit(self.km)
        self.conn_btn.setEnabled(False)
        self.disconn_btn.setEnabled(True)

    def disconn_btn_clicked(self):
        # self.finish_worker.emit()
        logging.info("Main timer stops")
        self.timer1.stop()
        self.km.proxy.kill()
        self.km = None
        self.conn_btn.setEnabled(True)
        self.disconn_btn.setEnabled(False)
        self.statusBar().showMessage("Disconnected")

    def register_btn_clicked(self):
        logging.info("Main register real data")
        dummy_integer = 4
        self.to_worker_q.put(dummy_integer)

    def time_out_event(self):
        logging.info("Main timer Time out event!!!")
        dummy_integer = 3
        self.to_worker_q.put(dummy_integer)

    def test_btn_clicked(self):
        self.trigger_test.emit()

    def run_thread_task(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Crate a worker object
        self.worker = Worker(self.to_worker_q,
                             self.from_worker_q,
                             self.km,
                             self.accno,
                             "005930")
        self.trigger_test.connect(self.worker.test)
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.start_worker)
        self.km_changed.connect(self.worker.update_km)
        self.finish_worker.connect(self.worker.finish)
        self.worker.trigger.connect(self.pop_from_worker_q)

        self.worker.finished.connect(
            lambda : logging.info("Timer stops")
        )
        self.worker.finished.connect(self.timer1.stop)
        self.worker.finished.connect(self.km.proxy.kill)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.worker.finished.connect(
            lambda: self.conn_btn.setEnabled(True)
        )
        self.worker.finished.connect(
            lambda: self.disconn_btn.setEnabled(False)
        )
        self.worker.finished.connect(
            lambda: self.statusBar().showMessage("Disconnected")
        )

        self.worker.finished.connect(
            lambda: print("worker.finished emitted")
        )
        self.thread.finished.connect(
            lambda: print("thread.finished emitted")
        )

    @pyqtSlot(str)
    def pop_from_worker_q(self, msg_from_worker):
        # if not self.from_worker_q.empty():
        #     msg_from_worker = self.from_worker_q.get()
        self.worker_label.setText(msg_from_worker)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
