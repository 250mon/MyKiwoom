from pykiwoom.kiwoom_q_manager import KwmQMgr


if __name__ == "__main__":
    kwm_q = KwmQMgr()

    real_cmd = {
        'func_name': "DisconnectRealData",
        'screen': '2000'
    }
    kwm_q.put_real(real_cmd)
    exit(0)

    # real_cmd = {
    #     'func_name': "SetRealReg",
    #     'screen': '2000',
    #     'code_list': "",
    #     'fid_list': "215;20;214",
    #     "opt_type": 0
    # }

    real_cmd = {
        'func_name': "SetRealReg",
        'screen': '2000',
        'code_list': '005930',
        'fid_list': "10",  # 현재가
        "opt_type": 0
    }

    kwm_q.put_real(real_cmd)
    while True:
        data = kwm_q.get_real()
        print(data)


