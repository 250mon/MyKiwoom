from pykiwoom.kiwoom import *

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

# 상장일
listing_date = kiwoom.GetMasterListedStockDate("005930")
print(listing_date)
print(type(listing_date))
