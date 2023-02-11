from kwm_method_api import *

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

# 종목상태
stock_status = kiwoom.GetMasterStockState("005930")
print(stock_status)