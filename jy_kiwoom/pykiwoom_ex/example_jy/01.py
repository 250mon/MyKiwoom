import pykiwoom.kiwoom_q_manager as KmQMgr

if __name__ == "__main__":
    kmq = KmQMgr()

    kmq.put_method(("GetConnectState",))
    # data = kmq.get_method()
    print(f"GetConnectState: {data}")

    # kmq.put_method(("GetCodeListByMarket", "0"))
    # data = kmq.get_method()
    # print(f"GetCodeListByMarket: {data}")



