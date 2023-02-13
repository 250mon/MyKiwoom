import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QEventLoop
from pykiwoom import parser
import pandas as pd
import datetime
from kwm_connect import Kwm
from logging_handler import LoggingHandler


class KwmMethodApi(QObject, LoggingHandler):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        # OCX instance
        self.ocx = Kwm().ocx

        # Event loop
        self.cond_loop = QEventLoop()

    def GetLoginInfo(self, tag):
        """
        로그인한 사용자 정보를 반환하는 메서드
        :param tag: ("ACCOUNT_CNT, "ACCNO", "USER_ID", "USER_NAME", "KEY_BSECGB", "FIREW_SECGB")
        :return: tag에 대한 데이터 값
        """
        data = self.ocx.dynamicCall("GetLoginInfo(QString)", tag)

        # if tag == "ACCNO":
        #     return data.split(';')[:-1]
        # else:
        #     return data
        return data

    def GetAPIModulePath(self):
        """
        OpenAPI 모듈의 경로를 반환하는 메서드
        :return: 모듈의 경로
        """
        ret = self.ocx.dynamicCall("GetAPIModulePath()")
        return ret

    def GetCodeListByMarket(self, market):
        """
        시장별 상장된 종목코드를 반환하는 메서드
        :param market: 0: 코스피, 3: ELW, 4: 뮤추얼펀드 5: 신주인수권 6: 리츠
                       8: ETF, 9: 하이일드펀드, 10: 코스닥, 30: K-OTC, 50: 코넥스(KONEX)
        :return: 종목코드 리스트 예: ["000020", "000040", ...]
        """
        data = self.ocx.dynamicCall("GetCodeListByMarket(QString)", market)
        tokens = data.split(';')[:-1]
        return tokens

    def GetConnectState(self):
        """
        현재접속 상태를 반환하는 메서드
        :return: 0:미연결, 1: 연결완료
        """
        ret = self.ocx.dynamicCall("GetConnectState()")
        return ret

    def GetMasterCodeName(self, code):
        """
        종목코드에 대한 종목명을 얻는 메서드
        :param code: 종목코드
        :return: 종목명
        """
        data = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
        return data

    def GetMasterListedStockCnt(self, code):
        """
        종목에 대한 상장주식수를 리턴하는 메서드
        :param code: 종목코드
        :return: 상장주식수
        """
        data = self.ocx.dynamicCall("GetMasterListedStockCnt(QString)", code)
        return data

    def GetMasterConstruction(self, code):
        """
        종목코드에 대한 감리구분을 리턴
        :param code: 종목코드
        :return: 감리구분 (정상, 투자주의 투자경고, 투자위험, 투자주의환기종목)
        """
        data = self.ocx.dynamicCall("GetMasterConstruction(QString)", code)
        return data

    def GetMasterListedStockDate(self, code):
        """
        종목코드에 대한 상장일을 반환
        :param code: 종목코드
        :return: 상장일 예: "20100504"
        """
        data = self.ocx.dynamicCall("GetMasterListedStockDate(QString)", code)
        return datetime.datetime.strptime(data, "%Y%m%d")

    def GetMasterLastPrice(self, code):
        """
        종목코드의 전일가를 반환하는 메서드
        :param code: 종목코드
        :return: 전일가
        """
        data = self.ocx.dynamicCall("GetMasterLastPrice(QString)", code)
        return int(data)

    def GetMasterStockState(self, code):
        """
        종목의 종목상태를 반환하는 메서드
        :param code: 종목코드
        :return: 종목상태
        """
        data = self.ocx.dynamicCall("GetMasterStockState(QString)", code)
        return data.split("|")

    def GetThemeGroupList(self, type=1):
        """
        테마코드와 테마명을 반환하는 메서드
        :param type: 정렬순서 (0:코드순, 1:테마순)
        :return: 코드와 코드명 리스트
        반환값의 코드와 코드명 구분은 '|' 코드의 구분은 ';'
        ex) 100|태양광_폴리실리코;152|합성섬유
        """
        data = self.ocx.dynamicCall("GetThemeGroupList(int)", type)
        tokens = data.split(';')
        if type == 0:
            grp = {x.split('|')[0]: x.split('|')[1] for x in tokens}
        else:
            grp = {x.split('|')[1]: x.split('|')[0] for x in tokens}
        return grp

    def GetThemeGroupCode(self, theme_code):
        """
        테마코드에 소속된 종목코드를 반환
        :param theme_code: 테마코드
        :return: 종목코드 리스트
        반환값의 종목코드간 구분은 ';'
        ex) A000660;A005930
        """
        data = self.ocx.dynamicCall("GetThemeGroupCode(QString)", theme_code)
        data = data.split(';')
        return [x[1:] for x in data]

    def GetFutureList(self):
        """
        지수선물 리스트를 반환
        :return:
        """
        data = self.ocx.dynamicCall("GetFutureList()")
        return data


if not QApplication.instance():
    app = QApplication(sys.argv)

if __name__ == "__main__":
    pass
    ## 로그인
    # kiwoom = Kiwoom()
    # kiwoom.CommConnect(block=True)

    ## 조건식 load
    # kiwoom.GetConditionLoad()

    # conditions = kiwoom.GetConditionNameList()

    ## 0번 조건식에 해당하는 종목 리스트 출력
    # condition_index = conditions[0][0]
    # condition_name = conditions[0][1]
    # codes = kiwoom.SendCondition("0101", condition_name, condition_index, 0)

    # print(codes)
