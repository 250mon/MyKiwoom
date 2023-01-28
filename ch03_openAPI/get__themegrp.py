from pykiwoom.kiwoom import *
import pprint


kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

tickers = map(kiwoom.GetMasterCodeName, kiwoom.GetThemeGroupCode('141'))
print(list(tickers))