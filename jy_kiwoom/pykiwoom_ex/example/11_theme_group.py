from kwm_method_api import *
import pprint

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

group = kiwoom.GetThemeGroupList(type=1)
pprint.pprint(group)

