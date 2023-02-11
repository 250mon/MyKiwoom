from kwm_method_api import *

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

감리구분 = kiwoom.GetMasterConstruction("005690")
print(감리구분)
