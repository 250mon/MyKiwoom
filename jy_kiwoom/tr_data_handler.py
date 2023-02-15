import os
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSlot
from kwm_connect import Kwm
from kwm_tr_api import KwmTrApi
from common_data import Ticker_Dict, My_Stock_Df
from pandas_table import PandasModel
from logging_handler import LoggingHandler
from time import time, sleep
from datetime import date


class TrDataHandler(QThread, LoggingHandler):
    def __init__(self, parent=None):
        print("TrDataHandler thread starts!!!")
        super().__init__(parent)
        self.main = parent
        # get a ref of Kwm() singleton instance
        self.tr_api = KwmTrApi(self)

        # file name of stocks info
        self.info_file_name = "stocks_info.h5"

        # get screen number
        self.tr_screen = Kwm().get_screen_no("Tr")

        self.get_acc_detailed_info()
        # self.get_stock_basic_info()

        # TR request being made by a user clicking
        self.main.call_account.clicked.connect(self.get_acc_detailed_info)

    @pyqtSlot()
    def get_acc_detailed_info(self):
        self.log.info("계좌평가좌고내역조회")
        df = self.tr_api.block_request("계좌평가잔고내역요청",
                                       "opw00018",
                                       계좌번호=self.main.get_acc_no(),
                                       비밀번호="0000",
                                       비밀번호입력매체구분="00",
                                       조회구분="2",
                                       screen=self.tr_screen)

        self.log.debug(df.columns)
        cols = ["총매입금액", "총평가금액", "추정예탁자산", "총평가손익금액", "총수익률(%)"]
        df_total = df.loc[:, cols].dropna()
        df_total = self._data_to_numeric(df_total)
        model = PandasModel(df_total)
        self.main.tableView0.setModel(model)

        cols = ["종목번호", "종목명", "보유수량", "매입가", "수익률(%)", "현재가", "매입금액", "매매가능수량"]
        My_Stock_Df = df.loc[:, cols].dropna()
        My_Stock_Df.iloc[:, 2:] = self._data_to_numeric(My_Stock_Df.iloc[:, 2:])
        model = PandasModel(My_Stock_Df)
        self.main.tableView1.setModel(model)

    def get_stock_basic_info(self):
        """
        filling self.main.stock_info
        :return:
        """

        if os.path.exists(self.info_file_name):
            creation_time = date.fromtimestamp(os.path.getmtime(self.info_file_name))
            elapsed_time = date.today() - creation_time
            if elapsed_time.days < 30:
                self.log.debug("Stock basic info file not updated because it is yet quite new")
                return

        self.log.debug("stock basic info file being updated ...")
        self.log.info("주식기본정보요청")
        codes = list(Ticker_Dict.keys())

        stock_info_df = pd.DataFrame()
        for i, ticker in enumerate(Ticker_Dict.keys()):
        # for i in range(2):
        #     ticker = codes[i]
            df = self.tr_api.block_request("주식기본정보요청",
                                           "opt10001",
                                           종목코드=ticker,
                                           screen=self.tr_screen)
            df.set_index("종목코드")
            stock_info_df = pd.concat([stock_info_df, df])
            if i % 10 == 0:
                sleep(3)
            else:
                sleep(0.5)

        stock_info_df.to_hdf("stocks_info.h5", "table", mode="w")

        self.log.debug(pd.read_hdf("stocks_info.h5", "stock_basic_info"))

    def _data_to_numeric(self, data_df):
        """
        convert dataframe 'obj' data format to numeric format
        if the data is percentage (%), it is converted to .2f floating number
        :param data_df:
        :return:
        """
        data_df = data_df.apply(pd.to_numeric)
        for c in data_df.columns:
            if "%" in c:
                data_df[c] = data_df[c].apply(lambda x: '{0:.2f}'.format(x))
            else:
                data_df[c] = data_df[c].apply(lambda x: '{:,.0f}'.format(x))
        return data_df
