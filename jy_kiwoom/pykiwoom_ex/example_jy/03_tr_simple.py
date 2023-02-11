import sys
sys.path.append('C:\\Users\\lambk\\CS\\PycharmProjects\\MyKiwoom\\jy_kiwoom')

from kwm_method_api import Kiwoom
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # kwm_q = KwmQMgr()
    kwm = Kiwoom(login=True)

    tr_cmd = {
        'rqname': "opt10001",
        'trcode': 'opt10001',
        'next': '0',
        'screen': '1000',
        'input': {
            # "종목코드": "005930",
            "종목코드": "035720",
        },
        'output': ['종목코드', '종목명', 'PER', 'PBR']
    }
    kwm.SetInputValue("종목코드", "035720")
    kwm.CommRqData(tr_cmd['rqname'], tr_cmd['trcode'], tr_cmd['next'], tr_cmd['screen'])

    sys.exit(app.exec_())

    # kwm_q.put_tr(tr_cmd)
    #
    # real_cmd = {
    #     'func_name': "DisconnectRealData",
    #     'screen': '2000'
    # }
    # kwm_q.put_real(real_cmd)
    #
    # data, remain = kwm_q.get_tr()
    # print(f'data = {data}, remain = {remain}')
    #
    # print('req2')
    # kwm_q.put_method(("GetConnectState",))
    # data = kwm_q.get_method()
    # print(f"GetConnectState: {data}")
    #
