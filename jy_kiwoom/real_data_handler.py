from PyQt5.QtCore import QThread
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from kwm_connect import Kwm
from kwm_real_api import KwmRealApi
from logging_handler import LoggingHandler
from kwm_type import *   # REALTYPE, SENDTYPE


class RealDataHandler(QThread, LoggingHandler):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main = parent
        # API object
        self.real_api = KwmRealApi(self)

        # choose tickers to monitor
        self.input_code = None
        self.code_list = []
        # self.real_codes = ["005930", "086520"]

        # register real data of markets' status
        # self.register_markets_status()
        # self.register_trading_data()

        self.model = QStandardItemModel()
        self.main.real_code_list_view.setModel(self.model)

        # connect to UI
        self.main.input_real_code_le.textChanged[str].connect(self._code_input)
        self.main.register_btn.clicked.connect(self._register_btn_clicked)
        self.main.deregister_btn.clicked.connect(self._deregister_btn_clicked)
        self.main.deregister_all_btn.clicked.connect(self._deregister_all)

        # initialize
        self._deregister_all()

    def _code_input(self, text):
        if text in self.main.code_dict.keys():
            code_name = self.main.code_dict[text]["종목명"]
            self.log.debug(f'RealDataHandler _code_input {text} {code_name}')
            self.main.real_code_name_label.setText(code_name)
            self.input_code = text
        else:
            self.input_code = None

    def _register_btn_clicked(self):
        if self.input_code is None:
            self.log.debug('No code input to register')
        elif self.input_code in self.code_list:
            self.log.debug(f'The code entered is already in the list')
        else:
            self.code_list.append(self.input_code)
            self.model.appendRow(QStandardItem(self.input_code))
            self._register_real_code()

    def _register_real_code(self):
        screen_no = Kwm().get_screen_no("Real")
        fid_list = []
        fid_list.append(FID['주식체결']['체결시간'])
        self.log.debug('Real time data being registered ... ')
        self.log.debug(f'\t{self.code_list} {fid_list}')
        self.real_api.set_real_reg(screen_no, self.code_list, fid_list, "0")

    def _deregister_btn_clicked(self):
        if self.input_code is None:
            self.log.debug('No code input to deregister')
        elif self.input_code in self.code_list:
            self.log.debug('Real time data being deregistered ... ')
            self.log.debug(f'\t{self.input_code}')
            self.code_list.remove(self.input_code)
            self.model.clear()
            map(self.model.appendRow, map(QStandardItem, self.code_list))
            self._deregister_real_code(self.input_code)
        else:
            self.log.debug('The code entered is not registered')

    def _deregister_real_code(self, code):
        self.real_api.SetRealRemove("ALL", list(code))

    def _deregister_all(self):
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

    def handle_real_data(self, real_data, rtype):
        """
        call-back function which handles real data received from api
        :param read_data: {"code": code, fid1: val1, fid2: val2 ...}
        :return:
        """
        self.log.debug(f'handle real data {rtype} {real_data}')





