from kwm_method_api import *

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

tickers = map(kiwoom.GetMasterCodeName, kiwoom.GetThemeGroupCode('141'))
print(list(tickers))