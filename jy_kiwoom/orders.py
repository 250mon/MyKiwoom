from PyQt5.QtCore import QThread
from kwm_connect import Kwm
from kwm_method_api import KwmMethodApi
from pandas_table import PandasModel
from logging_handler import LoggingHandler

class Order(QThread, LoggingHandler):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main = parent
        # Singleton ocx
        self.oxc = Kwm().get_ocx()
        # API object
        self.api = KwmMethodApi(self)

        # screen number
        self.screen_no = "1100"

        # order data input from line edit
        # 1:매수 2:매도 3:매수취소 4:매도취소 5:매수정정 6:매도정정
        self.order_type = 1
        # 주문 주식 코드
        self.order_ticker = None
        self.is_ticker_set = False
        # 주문 수량
        self.order_quantity = 0
        # 주문 단가
        self.order_price = None
        # '00':지정가  '03':시장가
        self.order_price_type = "00"
        # 원주문번호로 주문 정정시 사용
        self.org_order_no = ""

        self.main.limit_order_rb.clicked.connect(
            lambda: self.order_price_type == "00")
        self.main.limit_order_rb.setChecked(True)
        self.main.market_order_rb.clicked.connect(
            lambda: self.order_price_type == "03")

        self.main.input_code_le.textChanged[str].connect(self._code_input)
        self.main.input_price_spinbox.setRange(0, 99999999)
        self.main.input_price_spinbox.setSingleStep(100)
        self.main.input_price_spinbox.valueChanged.connect(self._price_input)
        self.main.input_price_spinbox.setRange(0, 99999999)
        self.main.input_qty_spinbox.valueChanged.connect(self._quantity_input)
        self.main.buy_btn.clicked.connect(self._order_buy)
    def place_order(self, req_name):
        self.api.SendOrder(req_name,
                           self.screen_no,
                           self.main.get_acc_no(),
                           self.order_type,
                           self.order_ticker,
                           self.order_quantity,
                           self.order_price,
                           self.order_price_type,
                           self.org_order_no)
        self.log.debug(f''
                       f''
                       )

    def _code_input(self, text):
        if text in self.main.code_dict.keys():
            code_name = self.main.code_dict[text]["종목명"]
            self.log.debug(f'Order _code_input {text} {code_name}')
            self.order_ticker = text
            self.main.code_name_label.setText(code_name)
            self.is_ticker_set = True
            self._set_quantity_limits()
        else:
            self.is_ticker_set = False


    def _set_quantity_limits(self):
        """
        TODO
        if it is about "buy", depending on the stock code and account balance,
         calculate the amount of stock that can be bought
        :return:
        """
        self.main.input_qty_spinbox.setMaximum(100)

    def _price_input(self):
        self.order_price = self.main.input_price_spinbox.value()
        self.log.debug(f'Order _quantity_input {self.order_price}')

    def _quantity_input(self):
        self.order_quantity = self.main.input_qty_spinbox.value()
        self.log.debug(f'Order _quantity_input {self.order_quantity}')

    def _order_buy(self):
        if self.order_quantity == 0:
            self.log.debug("Inconrrect order: Order quantity is set 0")
        elif self.order_price == 0:
            self.log.debug("Incorrect order: Order price is set 0")
        elif self.is_ticker_set:
            rqname = "매수 " + self.main.code_dict[self.order_ticker]["종목명"]
            self.log.debug(f"Order _order_buy {rqname} {self.order_quantity}")
            self.place_order(rqname)
        else:
            self.log.debug("Order ticker is incorrect")
