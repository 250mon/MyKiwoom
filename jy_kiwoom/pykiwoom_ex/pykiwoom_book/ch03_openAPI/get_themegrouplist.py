from pykiwoom.kiwoom import *
import pprint

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

# 테마그룹
group = kiwoom.GetThemeGroupList(1)
pprint.pprint(group)