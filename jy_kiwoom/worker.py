from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot
import datetime
from time import sleep
import logging

# Thread processing inbound data and making outbound requests
# Each thread will take care of only one ticker
class Worker(QObject):
    trigger = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, in_q, out_q, km, accno, ticker):
        super().__init__()
        self.in_q = in_q
        self.out_q = out_q
        # kiwoom manager
        self.km = km
        self.accno = accno
        self.ticker = ticker

        self.timestamp = None
        self.limit_delta = datetime.timedelta(milliseconds=100)

        self.work_timer = QTimer(self)
        self.work_timer.setInterval(3000)
        self.work_timer.timeout.connect(self.time_out_event)

    @pyqtSlot()
    def start_worker(self):
        logging.info("worker timer starts")
        # timer used to prevent run() from looping continously
        # so that any signal is able to come and work supposedly
        self.work_timer.start()

    def stop_worker(self):
        logging.info("worker timer stops")
        self.work_timer.stop()

    def time_out_event(self):
        logging.info("worker timer time out event!!!")
        self._run()

    @pyqtSlot(object)
    def update_km(self, km):
        logging.info(f"Worker km updated")
        self.km = km
        self.start_worker()

    @pyqtSlot()
    def test(self):
        logging.info("!!!!!!!!!!!!Test!!!!!!!!!!!!!!!")

    def _is_km_alive(self):
        logging.info('checking self.km ...')
        try:
            self.km
        except NameError:
            self.km = None

        if self.km is None:
            return False

        logging.info('checking self.km.proxy ...')
        if not self.km.proxy.is_alive():
            return False

        logging.info('checking connection ...')
        if self._get_connect_state() == 0:
            logging.info("Worker km not connected")
            return False

        return True

    def finish(self):
        # do we need to flush the queue????
        logging.info("Worker is finishing")
        self.finished.emit()

    def _run(self):
        # If self.km is not alive, need to update self.km
        # MainWindow will send km_changed signal that is
        # connected to self.update_km
        # If while-loop keeps any signal from triggering,
        # we need to break the loop here
        if not self._is_km_alive():
            self.stop_worker()

        logging.info(f'km is alive ...')

        # check if there is any real data comming in
        real_data = self.km.get_real()
        print(real_data)
        # if there is some data in the queue for analysis,
        if not self.in_q.empty():
            # blocking queue
            data = self.in_q.get()
            logging.info(f'received data = {data}')
            result = self._process_data(data)
            if result:
                self.timestamp = datetime.datetime.now()          # 이전 주문 시간을 기록함
                # Notify main_thread that cmd is placed in the q
                self.trigger.emit(f"Result: {result}")
        else:
            pass

    def _is_time_const_meet(self):
        # 시간 제한을 충족하는가?
        time_meet = False
        if self.timestamp is None:
            time_meet = True
        else:
            now = datetime.datetime.now()  # 현재시간
            delta = now - self.timestamp  # 현재시간 - 이전 주문 시간
            if delta >= self.limit_delta:
                time_meet = True

        logging.info(f"time constraint is met? {time_meet}")

        return time_meet

    def _process_data(self, data):
        result = None
        if not self._is_time_const_meet():
            return result

        # 알고리즘을 충족하는가?
        if data == 3:
            req = self._make_method_req()
            logging.info(f'data processed and request is {req}')
            result = self._send_method_req(req)
        elif data == 4:
            req = self._make_real_req()
            logging.info(f'data processed and request is {req}')
            self._send_real_req(req)
        else:
            pass
        return result

    # it uses blocking queue
    def _get_connect_state(self):
        logging.info("get_connect_state is called")
        req = ("GetConnectState",)
        self.km.put_method(req)
        state = self.km.get_method()
        logging.info(f"state is {state}")
        return state

    def _make_method_req(self):
        req = ("GetMasterCodeName", self.ticker)
        return req

    def _make_real_req(self):
        req = {
            'func_name': "SetRealReg",
            'screen': '2000',
            'code_list': self.ticker,
            # 'fid_list': "20;10",     # 체결시간, 현재가
            'fid_list': "10",          # 현재가
            "opt_type": 0
        }
        return req

    def _make_tr_req(self):
        pass

    def _make_tr_cont_req(self):
        pass

    def _make_order_req(self):
        order_data = {}

        # 삼성전자, 10주, 시장가주문 매수
        # 사용자가 임의로 지정하는 이름
        order_data["sRQName"] = "삼성전자 시장가 매수"
        # 화면번호로 "0"을 제외한 4자리의 문자열
        order_data["sScreenNO"] = "0101"
        # 1:매수 2:매도 3:매수취소 4:매도취소 5:매수정정 6:매도정정
        order_data["nOrderType"] = 1
        # stock symbol
        order_data["sCode"] = self.ticker
        # 주문수량
        order_data["nQty"] = 10
        # 주문단가
        order_data["nPrice"] = 0
        # '00':지정가  '03':시장가
        order_data["sHogaGb"] = "03"
        # 원주문번호로 주문 정정시 사용
        order_data["sOrgOrderNo"] = ""

        return order_data

    # it uses blocking queue
    def _send_method_req(self, req):
        logging.info(f"_send_method_req => Method request {req}")
        self.km.put_method(req)
        result = self.km.get_method()
        logging.info(f"_send_method_req => Result {result}")

        return result

    # it uses blocking queue
    def _send_real_req(self, req):
        logging.info(f"_send_real_req => Real request {req}")
        self.km.put_real(req)

    # it uses blocking queue
    def _send_tr_req(self, req):
        logging.info(f"_send_tr_req => TR request {req}")
        self.km.put_tr(req)
        result = self.km.get_tr()
        logging.info(f"_send_tr_req => Result {result}")
        return result

    # it uses blocking queue
    def _sent_tr_cont_req(self, req):
        logging.info(f"_send_tr_cont_req => TR cont request {req}")
        # FIX - range(2)
        for i in range(2):
            if i != 0:
                req['next'] = '2'
        self.km.put_tr(req)
        result = self.km.get_tr()
        logging.info(f"_send_tr_cont_req => Result {result}")
        return result

    def _send_order_req(self, req):
        logging.info(f"_send_order_req => Order request {req}")
        self.km.put_order(req)