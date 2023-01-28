from pykiwoom.kiwoom import *

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

# 전일가
previous_closing = kiwoom.GetMasterLastPrice("005930")
print(int(previous_closing))
print(type(previous_closing))