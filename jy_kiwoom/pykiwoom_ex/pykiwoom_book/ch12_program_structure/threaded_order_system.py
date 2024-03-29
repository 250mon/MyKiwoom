import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import datetime
from multiprocessing import Queue


# 실시간으로 들어오는 데이터를 보고 주문 여부를 판단하는 스레드
class Worker(QThread):
    # argument는 없는 단순 trigger
    # 데이터는 queue를 통해서 전달됨
    trigger = pyqtSignal()

    def __init__(self, data_queue, order_queue):
        super().__init__()
        self.data_queue = data_queue                # 데이터를 받는 용
        self.order_queue = order_queue              # 주문 요청용
        self.timestamp = None
        self.limit_delta = datetime.timedelta(seconds=2)

    def run(self):
        while True:
            if not self.data_queue.empty():
                data = self.data_queue.get()
                result = self.process_data(data)
                if result:
                    self.order_queue.put(data)                      # 주문 Queue에 주문을 넣음
                    self.timestamp = datetime.datetime.now()        # 이전 주문 시간을 기록함
                    self.trigger.emit()

    def process_data(self, data):
        # 시간 제한을 충족하는가?
        time_meet = False
        if self.timestamp is None:
            time_meet = True
        else:
            now = datetime.datetime.now()                           # 현재시간
            delta = now - self.timestamp                            # 현재시간 - 이전 주문 시간
            if delta >= self.limit_delta:
                time_meet = True

        # 알고리즘을 충족하는가?
        algo_meet = False
        if data % 2 == 0:
            algo_meet = True

        # 알고리즘과 주문 가능 시간 조건을 모두 만족하면
        if time_meet and algo_meet:
            return True
        else:
            return False


class MyWindow(QMainWindow):
    def __init__(self, data_queue, order_queue):
        super().__init__()

        # queue
        self.data_queue = data_queue
        self.order_queue = order_queue

        # thread start
        self.worker = Worker(data_queue, order_queue)
        self.worker.trigger.connect(self.pop_order)
        self.worker.start()

        # 데이터가 들어오는 속도는 주문보다 빠름
        self.timer1 = QTimer()
        self.timer1.start(1000)
        self.timer1.timeout.connect(self.push_data)

    def push_data(self):
        now = datetime.datetime.now()
        self.data_queue.put(now.second)

    @pyqtSlot()
    def pop_order(self):
        if not self.order_queue.empty():
            data = self.order_queue.get()
            print(data)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    data_queue = Queue()
    order_queue = Queue()
    window = MyWindow(data_queue, order_queue)
    window.show()

    app.exec_()