import pykiwoom


if __name__ == "__main__":
    km = pykiwoom.KiwoomManager()

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

    km.put_real(real_cmd)
    while True:
        data = km.get_real()
        print(data)


