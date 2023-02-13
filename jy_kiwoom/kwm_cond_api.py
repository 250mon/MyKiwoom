import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QEventLoop
from pykiwoom import parser
import pandas as pd
import datetime
from kwm_connect import Kwm
from logging_handler import LoggingHandler


class KwmCondApi(QObject, LoggingHandler):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        # OCX instance
        self.ocx = Kwm().ocx

        # Event loop
        self.cond_loop = QEventLoop()


        # Event connect
        self.ocx.OnReceiveRealCondition.connect(self.OnReceiveRealCondition)
        self.ocx.OnReceiveTrCondition.connect(self.OnReceiveTrCondition)
        self.ocx.OnReceiveConditionVer.connect(self.OnReceiveConditionVer)

    def OnReceiveConditionVer(self, ret, msg):
        if ret == 1:
            self.condition_loaded = True

    def OnReceiveRealCondition(self, code, id_type, cond_name, cond_index):
        """이벤트 함수로 편입, 이탈 종목이 실시간으로 들어오는 callback 함수

        Args:
            code (str): 종목코드
            id_type (str): 편입('I'), 이탈('D')
            cond_name (str): 조건명
            cond_index (str): 조건명 인덱스
        """
        output = {
            'code': code,
            'type': id_type,
            'cond_name': cond_name,
            'cond_index': cond_index
        }
        # self.real_cond_dqueue.put(output)

    def OnReceiveTrCondition(self, screen_no, code_list, cond_name, cond_index, next):
        """일반조회 TR에 대한 callback 함수

        Args:
            screen_no (str): 종목코드
            code_list (str): 종목리스트(";"로 구분)
            cond_name (str): 조건명
            cond_index (int): 조건명 인덱스
            next (int): 연속조회(0: 연속조회 없음, 2: 연속조회)
        """
        # legacy interface
        codes = code_list.split(';')[:-1]
        self.tr_condition_data = codes
        self.tr_condition_loaded = True

        # queue
        # if self.tr_cond_dqueue is not None:
        #     output = {
        #         'screen_no': screen_no,
        #         'code_list': codes,
        #         'cond_name': cond_name,
        #         'cond_index': cond_index,
        #         'next': next
        #     }
        #     self.tr_cond_dqueue.put(output)

    def GetConditionLoad(self, block=True):
        """
        서버에 저장된 사용자 조건식을 조회해서 임시로 파일에 저장
        :param block:
        :return:
        """
        self.condition_loaded = False

        self.ocx.dynamicCall("GetConditionLoad()")
        self.cond_loop.exec_()
        # if block:
        #     while not self.condition_loaded:
        #         pythoncom.PumpWaitingMessages()

    def GetConditionNameList(self):
        """
        조건검색 조건명 리스트를 받아온다
        :return: 조건명 리스트 (인덱스^조건명)
        조건명 리스트를 구분(“;”)하여 받아온다. ex) 인덱스1^조건명1;인덱스2^조건명2;…
        """
        data = self.ocx.dynamicCall("GetConditionNameList()")
        conditions = data.split(";")[:-1]

        # [('000', 'perpbr'), ('001', 'macd'), ...]
        result = []
        for condition in conditions:
            cond_index, cond_name = condition.split('^')
            result.append((cond_index, cond_name))

        return result

    def SendCondition(self, screen, cond_name, cond_index, search, block=True):
        """조건검색 종목조회 TR을 송신

        Args:
            screen (str): 화면번호
            cond_name (str): 조건명
            cond_index (int): 조건명 인덱스
            search (int): 0: 일반조회, 1: 실시간조회, 2: 연속조회
            block (bool): True: blocking request, False: Non-blocking request

        Returns:
            None: _description_

        OnReceiveTrCondition으로 결과값이 온다
        """
        # if block is True:
        #     self.tr_condition_loaded = False

        self.ocx.dynamicCall("SendCondition(QString, QString, int, int)", screen, cond_name, cond_index, search)

        # if block is True:
        #     while not self.tr_condition_loaded:
        #         pythoncom.PumpWaitingMessages()
        #
        # if block is True:
        #     return self.tr_condition_data

    def SendConditionStop(self, screen, cond_name, index):
        """
        조건검색 실시간 중지 TR 을 송신
        :param screen: 화면번호
        :param cond_name: 조건명
        :param index: 조건명 인덱스
        :return:
        """
        self.ocx.dynamicCall("SendConditionStop(QString, QString, int)", screen, cond_name, index)


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
