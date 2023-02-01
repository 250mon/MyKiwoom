from pykiwoom.kiwoom_q_manager import KwmQMgr

if __name__ == "__main__":
    kwm_q = KwmQMgr()

    tr_cmd = {
        'rqname': "opt10001",
        'trcode': 'opt10001',
        'next': '0',
        'screen': '1000',
        'input': {
            "종목코드": "005930"
        },
        'output': ['종목코드', '종목명', 'PER', 'PBR']
    }

    kwm_q.put_tr(tr_cmd)
    data, remain = kwm_q.get_tr()
    print(data, remain)
    print('req')

    kwm_q.put_method(("GetConnectState",))
    data = kwm_q.get_method()
    print(f"GetConnectState: {data}")
