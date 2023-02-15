import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from kwm_connect import Kwm
from kwm_real_api import KwmRealApi
from common_data import Ticker_Dict
from logging_handler import LoggingHandler
from kwm_type import *   # REALTYPE, SENDTYPE


class RealDataHandler(QThread, LoggingHandler):
    chegyul = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main = parent
        # API object
        self.real_api = KwmRealApi(self)

        # choose tickers to monitor
        self.input_code = None
        self.code_list = []

        self.model = QStandardItemModel()
        self.main.real_code_list_view.setModel(self.model)

        # connect to UI
        self.main.input_real_code_le.textChanged[str].connect(self.code_input)
        self.main.register_btn.clicked.connect(self.register_btn_clicked)
        self.main.deregister_btn.clicked.connect(self.deregister_btn_clicked)
        self.main.deregister_all_btn.clicked.connect(self.deregister_all)

        # initialize
        self.deregister_all()

        # register real data of markets' status
        self.register_markets_status()

    def code_input(self, text):
        if text in Ticker_Dict.keys():
            code_name = Ticker_Dict[text]["종목명"]
            self.log.debug(f'RealDataHandler _code_input {text} {code_name}')
            self.main.real_code_name_label.setText(code_name)
            self.input_code = text
        else:
            self.input_code = None

    def register_btn_clicked(self):
        if self.input_code is None:
            self.log.debug('No code input to register')
        elif self.input_code in self.code_list:
            self.log.debug(f'The code entered is already in the list')
        else:
            self.code_list.append(self.input_code)
            self.model.appendRow(QStandardItem(self.input_code))
            self.register_real_code()

    def register_real_code(self):
        screen_no = Kwm().get_screen_no("Real")
        fid_list = [FID['주식체결']['체결시간']]
        self.log.debug('Real time data being registered ... ')
        self.log.debug(f'\t{self.code_list} {fid_list}')
        self.real_api.set_real_reg(screen_no, self.code_list, fid_list, "0")

    def deregister_btn_clicked(self):
        if self.input_code is None:
            self.log.debug('No code input to deregister')
        elif self.input_code in self.code_list:
            self.log.debug('Real time data being deregistered ... ')
            self.log.debug(f'\t{self.input_code}')
            self.code_list.remove(self.input_code)
            self.model.clear()
            map(self.model.appendRow, map(QStandardItem, self.code_list))
            self.deregister_real_code(self.input_code)
        else:
            self.log.debug('The code entered is not registered')

    def deregister_real_code(self, code):
        self.real_api.SetRealRemove("ALL", code)

    def deregister_all(self):
        """
        deregister all real data
        :return:
        """
        self.log.debug('All screen All codes are deregistered from Real')
        self.model.clear()
        self.real_api.SetRealRemove("ALL", "ALL")

    def register_markets_status(self):
        """
        register real data for markets' status
        "0" before opening
        "3" opening
        "2" simultaneous calling
        "4" closing
        :return:
        """
        screen_no = Kwm().get_screen_no("Real")
        self.real_api.set_real_reg(screen_no, self.code_list, [FID['장시작시간']['장운영구분']], "0")

    # def handle_real_data(self, code, rtype, data):
    #     """
    #     call-back function which handles real data received from api
    #     :param read_data: {"code": code, fid1: val1, fid2: val2 ...}
    #     :return:
    #     """

    def handle_real_data(self, code, rtype, data):
        """
        call-back function which handles real data received from api
        :param code: ticker
        :param rtype: real type
        :param data: item values
        :return:
        """
        self.log.debug(f'handle real data {rtype} {data}')

        # check if rtype is defined in FID
        if rtype not in FID.keys():
            self.log.debug(f'OnReceiveRealData rtype {rtype} does not exist in FID')
            return
        data_df = pd.DataFrame(data=data, columns=FID[rtype].keys())

        if rtype == "주식체결":
            self.log.debug(f'주식체결 dataframe')
            self.log.debug(data_df[['현재가', '등락율', '전일거래량대비(비율)', '체결강도']])
        elif rtype == "주식호가잔량":
            self.log.debug(f'주식호가잔량 dataframe')
            self.log.debug(data_df)
        elif rtype == "장시작시간":
            self.log.debug(f'장시작시간 dataframe')
            self.log.debug(data_df)
        else:
            pass


    def handle_chejan_data(self, gubun, chejan_data):
        """
        call-back function which handles chejan data received from api
        :param gubun: '0': 접수, 체결, '1': 잔고 변경
        :param chejan_data: {fid: value ...}
        :return:
        """
        self.log.debug(f'handle chejan data 구분:{gubun}')

        if gubun == "0":
            # rtype "주문체결"
            data_s = pd.Series(data=chejan_data.values(), index=chejan_data.keys())
            data_s.reindex(FID["주문체결"].values())
            self.log.debug(f'주문체결 Series')
            self.log.debug(data_s)
        else:
            # rtype "잔고"
            data_s = pd.Series(data=chejan_data.values(), index=chejan_data.keys())
            data_s.reindex(FID["잔고"].values())
            self.log.debug(f'잔고 Series')
            self.log.debug(data_s)

