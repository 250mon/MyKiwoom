import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from kwm_connect import Kwm
from kwm_method_api import KwmMethodApi
from tr_data_handler import TrDataHandler
from real_data_handler import RealDataHandler
from orders import Order
from logging_handler import LoggingHandler
import pandas as pd

form_class = uic.loadUiType("Initial2.ui")[0]

class MyWindow(QMainWindow, QWidget, form_class, LoggingHandler):
    def __init__(self, *args, **kwargs):
        super(MyWindow, self).__init__(*args, **kwargs)
        form_class.__init__(self)
        # setup UI; a method from form_class
        self.setupUi(self)

        # get a ref of Kwm() singleton instance
        self.method_api = KwmMethodApi(self)

        # first of all, account number is needed
        self.get_account_info()

        # retrieving all the codes and names of KOSPI and KOSDAQ
        # self.code_dict = {"005930": {"종목명": "삼성전자"},
        #                   "373220": {"종목명": "LG에너지솔루션"},
        #                   ...}
        self.code_dict = None
        self.get_item_list()

        # sotck basic info (Dataframe) which will be set by TR request
        # later while constructing the self.tr_handler
        self.stock_info = pd.DataFrame()

        # worker threads: tr_data_handler, real_data_handler
        self.tr_handler = TrDataHandler(self)
        self.real_handler = RealDataHandler(self)

        # when clicked, retrieves account info
        # self.acc_manage.clicked.connect(self.a_manage)

        self.start()

    def start(self):
        order = Order(self)
        order.start

    def get_account_info(self):
        print('get account info')
        account_list = self.method_api.GetLoginInfo("ACCNO")
        print(account_list)

        for acc_no in account_list.split(';'):
            self.accComboBox.addItem(acc_no)

    def get_acc_no(self):
        return self.accComboBox.currentText()

    def get_item_list(self):
        """
        self.code_dict = {"005930": {"종목명": "삼성전자"},
                          "373220": {"종목명": "LG에너지솔루션"},
                          ...}
        :return:
        """
        markets = ["0", "10"]
        codes = list(map(self.method_api.GetCodeListByMarket, markets))
        kospi_codes = codes[0]
        kosdaq_codes = codes[1]
        # retrieving code names
        kospi_names = list(map(self.method_api.GetMasterCodeName, kospi_codes))
        kosdaq_names = list(map(self.method_api.GetMasterCodeName, kosdaq_codes))
        # creats code dicts
        kospi_code_dict = {code: {"종목명": name} for code, name
                           in zip(kospi_codes, kospi_names)}
        kosdaq_code_dict = {code: {"종목명": name} for code, name
                            in zip(kosdaq_codes, kosdaq_names)}
        # combining the dicts
        self.code_dict = {**kospi_code_dict, **kosdaq_code_dict}

    def setup_timer(self):
        self.timer1.setInterval(3000)
        self.timer1.timeout.connect(self.time_out_event)

    def time_out_event(self):
        dummy_integer = 3
        self.to_worker_q.put(dummy_integer)


    # def run_thread_pool(self):
    #     thread_count = QThreadPool.globalInstance().maxThreadCount()
    #     thread_count = 1
    #     pool = QThreadPool.globalInstance()
    #     for i in range(thread_count):
    #         # 2. Instantiate the subclass of QRunnable
    #         runnable = Runnable()
    #         # 3. Call start()
    #         pool.start(runnable)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
