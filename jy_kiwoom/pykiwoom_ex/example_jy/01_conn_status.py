from pykiwoom.kiwoom_q_manager import KwmQMgr


if __name__ == '__main__':
    kwm_q = KwmQMgr()
    kwm_q.put_method(("GetConnectState",))
    data = kwm_q.get_method()
    print(f"GetConnectState: {data}")

    kwm_q.put_method(("GetCodeListByMarket", "0"))
    data = kwm_q.get_method()
    print(f"GetCodeListByMarket: {data}")
