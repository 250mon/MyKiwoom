from kwm_method_api import *

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

# 감리구분
supervision_status = kiwoom.GetMasterConstruction("005930")
print(supervision_status)