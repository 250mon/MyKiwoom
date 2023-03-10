import os
import sqlite3
import pandas as pd
from PyQt5.QtCore import QThread
from kwm_connect import Kwm
from kwm_method_api import KwmMethodApi
from kwm_tr_api import KwmTrApi
from common_data import Ticker_Dict
from pandas_table import PandasModel
from logging_handler import LoggingHandler
from time import time, sleep
from datetime import date


class TrDataHandler(QThread, LoggingHandler):
# class TrDataHandler(LoggingHandler):
    def __init__(self, parent=None):
        print("TrDataHandler thread starts!!!")
        super().__init__(parent)
        self.main = parent
        # get a ref of Kwm() singleton instance
        self.tr_api = KwmTrApi()

        # file name of stocks info
        self.info_file_name = "stocks_info.h5"

        # get screen number
        self.tr_screen = Kwm().get_screen_no("Tr")

        # wire methods to UI
        self.wire_to_ui()

    def wire_to_ui(self):
        if self.main is None:
            return

        self.main.call_account.clicked.connect(self.show_acc_info)

    def get_acc_detailed_info(self, acc_no):
        self.log.info("계좌평가좌고내역조회")
        df = self.tr_api.block_request("계좌평가잔고내역요청",
                                       "opw00018",
                                       계좌번호=acc_no,
                                       비밀번호="0000",
                                       비밀번호입력매체구분="00",
                                       조회구분="2",
                                       screen=self.tr_screen)

        self.log.debug(df.columns)
        cols = ["총매입금액", "총평가금액", "추정예탁자산", "총평가손익금액", "총수익률(%)"]
        df_total = df.loc[:, cols].dropna()
        df_total = self._data_to_numeric(df_total)

        cols = ["종목번호", "종목명", "보유수량", "매입가", "수익률(%)", "현재가", "매입금액", "매매가능수량"]
        df_stocks = df.loc[:, cols].dropna()
        df_stocks.iloc[:, 2:] = self._data_to_numeric(df_stocks.iloc[:, 2:])

        return df_total, df_stocks

    def show_acc_info(self):
        df_total, df_stocks = self.get_acc_detailed_info(self.main.get_acc_no())
        model = PandasModel(df_total)
        self.main.tableView0.setModel(model)
        model = PandasModel(df_stocks)
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
        tickers = list(Ticker_Dict.keys())
        stock_info_df = pd.DataFrame()
        for i, ticker in enumerate(tickers):
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

    def get_ohlcv(self, ticker_list):
        """

        :param data_df:
        :return:
        """
        self.log.debug("ohlcv  being updated ...")
        self.log.info("주식일봉차트조회요청")
        con = sqlite3.connect("ohlcv.db")

        ohlcv_df = pd.DataFrame()
        for i, ticker in enumerate(ticker_list):
            df = self.tr_api.block_request("주식일봉차트조희요청",
                                           "opt10081",
                                           종목코드=ticker,
                                           기준일자='20210101',
                                           수정주가구분="1",
                                           screen=self.tr_screen)
            df.set_index("일자")
            ohlcv_df = pd.concat([ohlcv_df, df])
            sleep(0.5)
        print(ohlcv_df)


if __name__ == "__main__":
    tr_handler = TrDataHandler()
    sleep(3)

    method_api = KwmMethodApi()
    accounts = method_api.GetLoginInfo("ACCNO")
    acc_list = []
    for acc in accounts.split(';'):
        acc_list.append(acc)
    print(acc_list)
    df1, df2 = tr_handler.get_acc_detailed_info(acc_list[0])
    print(df1)
    print(df2)

    tr_handler.get_ohlcv(['005930'])

