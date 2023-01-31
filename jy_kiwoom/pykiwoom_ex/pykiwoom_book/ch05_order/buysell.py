from pykiwoom.kiwoom import *


kiwoom = Kiwoom()
kiwoom.CommConnect(block= True)

# 주식계좌
accounts = kiwoom.GetLoginInfo("ACCNO")
stock_account = accounts[0]
print(f'account number is {stock_account}')

# 삼성전자, 10주, 시장가주문 매수
# 사용자가 임의로 지정하는 이름
sRQName = "삼성전자 시장가 매수"
# 화면번호로 "0"을 제외한 4자리의 문자열
sScreenNO = "0101"
# 계좌번호
sAccNo = stock_account
# 1:매수 2:매도 3:매수취소 4:매도취소 5:매수정정 6:매도정정
nOrderType = 1
# stock symbol
sCode = "005930"
# 주문수량
nQty = 10
# 주문단가
nPrice = 0
# '00':지정가  '03':시장가
sHogaGb = "03"
# 원주문번호로 주문 정정시 사용
sOrgOrderNo = ""

kiwoom.SendOrder(sRQName,
                 sScreenNO,
                 sAccNo,
                 nOrderType,
                 sCode,
                 nQty,
                 nPrice,
                 sHogaGb,
                 sOrgOrderNo)