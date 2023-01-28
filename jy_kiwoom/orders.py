from pykiwoom.kiwoom import *


class Order():
    def __init__(self, kiwoom):
        self.kiwoom = kiwoom
        self.stock_account = None
        self.get_log_info()

    def get_log_info(self):
        # 주식계좌
        accounts = self.kiwoom.GetLoginInfo("ACCNO")
        self.stock_account = accounts[0]

    def buy_order(self, buy_data):
        self.kiwoom.SendOrder(buy_data["sRQName"],
                         buy_data["sScreenNO"],
                         self.stock_account,
                         buy_data["nOrderType"],
                         buy_data["sCode"],
                         buy_data["nQty"],
                         buy_data["nPrice"],
                         buy_data["sHogaGb"],
                         buy_data["sOrgOrderNo"])