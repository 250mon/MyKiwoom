import pykiwoom

if __name__ == "__main__":
    km = pykiwoom.KiwoomManager()

    km.put_method(("GetConnectState",))
    data = km.get_method()
    print(f"GetConnectState: {data}")

    km.put_method(("GetCodeListByMarket", "0"))
    data = km.get_method()
    print(f"GetCodeListByMarket: {data}")



