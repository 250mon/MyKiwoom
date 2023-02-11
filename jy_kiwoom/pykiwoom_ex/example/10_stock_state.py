from kwm_method_api import *

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

종목상태 = kiwoom.GetMasterStockState("005930")
print(종목상태)
