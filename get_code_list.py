import sys
from PyQt5.QtWidgets import *
from kiwoom_interface import Kiwoom

def get_code_list_by_market(kiwoom, market):
    code_list = kiwoom.dynamicCall("GetCodeListByMarket(QString)", market)
    code_list = code_list.split(';')
    return code_list[:-1]

def get_master_code_name(kiwoom, code):
    code_name = kiwoom.dynamicCall("GetMasterCodeName(QString", code)
    return code_name

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.connect()

    # Get code list
    code_list = get_code_list_by_market(kiwoom, '10')
    for code in code_list:
        code_name = get_master_code_name(kiwoom, code)
        print(code_name, end=" ")

