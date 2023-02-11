import pandas as pd
from PyQt5.QtCore import QThread
from kwm_connect import Kwm
from kwm_method_api import KwmMethodApi
from pandas_table import PandasModel

class AccInfo(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main = parent
        # Singleton ocx
        self.oxc = Kwm().get_ocx()
        # API object
        self.api = KwmMethodApi()

        # screen number
        self.acc_screen = "1000"
        # TR request
        self.acc_detailed_info_req()

    def acc_detailed_info_req(self):
        print("계좌평가좌고내역조회")
        df = self.api.block_request("계좌평가잔고내역요청",
                                    "opw00018",
                                    계좌번호=self.main.get_acc_no(),
                                    비밀번호="0000",
                                    비밀번호입력매체구분="00",
                                    조회구분="2",
                                    next=0,
                                    screen=self.acc_screen)

        print(df.columns)
        cols = ["총매입금액", "총평가금액", "추정예탁자산", "총평가손익금액", "총수익률(%)"]
        df_total = df.loc[:, cols].dropna()
        df_total = self._data_to_numeric(df_total)
        model = PandasModel(df_total)
        self.main.tableView0.setModel(model)


        cols = ["종목번호", "종목명", "보유수량", "매입가", "수익률(%)", "현재가", "매입금액", "매매가능수량"]
        df_per_ticker = df.loc[:, cols].dropna()
        df_per_ticker.iloc[:, 2:] = self._data_to_numeric(df_per_ticker.iloc[:, 2:])
        model = PandasModel(df_per_ticker)
        self.main.tableView1.setModel(model)

    def _data_to_numeric(self, data_df):
        """
        convert dataframe 'obj' data format to numeric format
        if the data is percentage (%), it is converted to .2f floating number
        :param data_df:
        :return:
        """
        data_df = data_df.apply(pd.to_numeric)
        for c in data_df.columns:
            print(c)
            if "%" in c:
                data_df[c] = data_df[c].apply(lambda x: '{0:.2f}'.format(x))
            else:
                data_df[c] = data_df[c].apply(lambda x: '{:,.0f}'.format(x))
        return data_df