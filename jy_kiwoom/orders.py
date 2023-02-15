from PyQt5.QtCore import QThread
from kwm_connect import Kwm
from kwm_method_api import KwmMethodApi
from pandas_table import PandasModel
from common_data import Ticker_Dict, My_Stock_Df
from logging_handler import LoggingHandler

class Order(LoggingHandler):
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

        self.main.limit_order_rb.clicked.connect(self.limit_order_checked)
        self.main.limit_order_rb.setChecked(True)
        self.main.market_order_rb.clicked.connect(self.market_order_checked)

        self.main.input_code_le.textChanged[str].connect(self.code_input)
        self.main.input_price_spinbox.setRange(0, 99999999)
        self.main.input_price_spinbox.setSingleStep(100)
        self.main.input_price_spinbox.valueChanged.connect(self.price_input)
        self.main.input_price_spinbox.setRange(0, 99999999)
        self.main.input_qty_spinbox.valueChanged.connect(self.quantity_input)
        self.main.buy_btn.clicked.connect(self.buy_btn_clicked)

    def limit_order_checked(self):
        self.order_price_type = "00"
        self.main.input_price_spinbox.setEnabled(True)

    def market_order_checked(self):
        self.order_price_type = "03"
        self.order_price = 0
        self.main.input_price_spinbox.setEnabled(False)

    def is_limit_order(self):
        """
        check if it is market order(시장가 주문)
        :return:
        """
        return self.main.limit_order_rb.isChecked()

    def code_input(self, text):
        """
        handling user input and set self.order_ticker and self.is_ticker_set
        :param text:
        :return:
        """
        if text in Ticker_Dict.keys():
            code_name = Ticker_Dict[text]["종목명"]
            self.log.debug(f'Order _code_input {text} {code_name}')
            self.order_ticker = text
            self.main.code_name_label.setText(code_name)
            self.is_ticker_set = True
            self.set_quantity_limits()
        else:
            self.is_ticker_set = False


    def set_quantity_limits(self):
        """
        TODO
        if it is about "buy", depending on the stock code and account balance,
         calculate the amount of stock that can be bought
        :return:
        """
        self.main.input_qty_spinbox.setMaximum(100)

    def price_input(self):
        """
        getting price input
        :return:
        """
        self.order_price = self.main.input_price_spinbox.value()
        self.log.debug(f'Order _quantity_input {self.order_price}')

    def quantity_input(self):
        """
        getting quantity input
        :return:
        """
        self.order_quantity = self.main.input_qty_spinbox.value()
        self.log.debug(f'Order _quantity_input {self.order_quantity}')

    def buy_btn_clicked(self):
        if self.order_quantity == 0:
            self.log.debug("Wrong order: Order quantity is set 0")
        elif self.is_limit_order() and self.order_price == 0:
            self.log.debug("Wrong order: Order price is set 0 when it is a limit order")
        elif self.is_ticker_set and self:
            rqname = "매수 " + Ticker_Dict[self.order_ticker]["종목명"]
            self.log.info(f"Order _order_buy {rqname} {self.order_quantity}")
            self.place_order(rqname)
        else:
            self.log.debug("Wrong order: Order ticker is incorrect")

        # clear the input fields
        self.main.input_code_le.clear()
        self.main.input_price_spinbox.setValue(0)
        self.main.input_qty_spinbox.setValue(0)

    def sell_btn_clicked(self):
        if self.order_quantity == 0:
            self.log.debug("Wrong order: Order quantity is set 0")
        elif self.is_limit_order() and self.order_price == 0:
            self.log.debug("Wrong order: Order price is set 0 when it is a limit order")
        elif self.is_ticker_set and self.order_ticker in My_Stock_Df.index():
            rqname = "매도 " + Ticker_Dict[self.order_ticker]["종목명"]
            self.log.info(f"Order _order_buy {rqname} {self.order_quantity}")
            self.place_order(rqname)
        else:
            self.log.debug("Wrong order: Order ticker is incorrect")

        # clear the input fields
        self.main.input_code_le.clear()
        self.main.input_price_spinbox.setValue(0)
        self.main.input_qty_spinbox.setValue(0)

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
