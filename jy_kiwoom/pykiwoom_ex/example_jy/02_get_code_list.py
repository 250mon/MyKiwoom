from pykiwoom.kiwoom_q_manager import KwmQMgr

# 시장의 종목코드

if __name__ == "__main__":
    kwm_q = KwmQMgr()
    kwm_q.put_method(("GetCodeListByMarket", "0"))
    kwm_q.put_method(("GetCodeListByMarket", "10"))
    kospi = kwm_q.get_method()
    kosdaq = kwm_q.get_method()
    all = kospi + kosdaq
    print(len(all))
    


