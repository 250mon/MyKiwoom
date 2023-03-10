import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QEventLoop
from pykiwoom import parser
import pandas as pd
from kwm_connect import Kwm
from logging_handler import LoggingHandler
from time import sleep


class KwmTrApi(QObject, LoggingHandler):
    def __init__(self):
        super().__init__()
        # OCX instance
        self.ocx = Kwm().ocx
        self.min_interval = 0.5

        # Event loop
        self.tr_data_loop = QEventLoop()

        # dictionary of output items for each tr code
        self.tr_output = {}
        # retrieved data for the tr req in the form of DataFrame
        self.tr_data = None
        # flag for more data to come
        self.tr_remained = False

        # Tr Data slots for Kiwoom
        self.ocx.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.ocx.OnReceiveMsg.connect(self.OnReceiveMsg)

    def get_data(self, trcode, rqname, items):
        rows = self.GetRepeatCnt(trcode, rqname)
        if rows == 0:
            rows = 1

        data_list = []
        for row in range(rows):
            row_data = []
            for item in items:
                data = self.GetCommData(trcode, rqname, row, item)
                # self.log.debug(f"get_data: data from GetCommData..\n{data}")
                row_data.append(data)
            data_list.append(row_data)

        # data to DataFrame
        df = pd.DataFrame(data=data_list, columns=items)
        return df

    def OnReceiveTrData(self, screen, rqname, trcode, record, next):
        self.log.debug(f'OnReceiveTrData {screen}, {rqname}, {trcode}, {record}, {next}')
        # order trcode
        # - KOA_NORMAL_BUY_KP_ORD  : 코스피 매수
        # - KOA_NORMAL_SELL_KP_ORD : 코스피 매도
        # - KOA_NORMAL_KP_CANCEL   : 코스피 주문 취소
        # - KOA_NORMAL_KP_MODIFY   : 코스피 주문 변경
        # - KOA_NORMAL_BUY_KQ_ORD  : 코스피 매수
        # - KOA_NORMAL_SELL_KQ_ORD : 코스피 매도
        # - KOA_NORMAL_KQ_CANCEL   : 코스피 주문 취소
        # - KOA_NORMAL_KQ_MODIFY   : 코스피 주문 변경
        if trcode in ['KOA_NORMAL_BUY_KP_ORD',
                      'KOA_NORMAL_SELL_KP_ORD',
                      'KOA_NORMAL_KP_CANCEL',
                      'KOA_NORMAL_KP_MODIFY',
                      'KOA_NORMAL_BUY_KQ_ORD',
                      'KOA_NORMAL_SELL_KQ_ORD',
                      'KOA_NORMAL_KQ_CANCEL',
                      'KOA_NORMAL_KQ_MODIFY']:
            self.log.debug(f'주문번호는 아마도... {record}')
            return None

        output_items = []
        if self.tr_output[trcode] is None:
            # output_items 는 가능한 모든 output 항목 들의 list
            lines = parser.read_enc(trcode)
            tr_items = parser.parse_dat(trcode, lines)
            # tr_items
            # {
            #   'trcode': 'opw00018',
            #   'input': [{'계좌평가잔고내역요청': ['계좌번호', '비밀번호',...]}],
            #   'output': [
            #       {'계좌평가결과': ['총매입금액', '총평가금액',...]},
            #       {'계좌평가잔고개별합산': ['종목번호', '종목명',...]}
            #   ]
            # }

            for output in tr_items['output']:
                output_items += list(output.values())[0]
        else:
            output_items = self.tr_output[trcode]
        self.log.debug(f'output_items ##################\n {output_items}')

        try:
            # remained data
            if next == '2':
                self.tr_remained = True
            else:
                self.tr_remained = False

            df = self.get_data(trcode, rqname, output_items)
            self.log.debug(df.head(3))
            self.log.debug(df.shape)
            self.tr_data = df

            if self.tr_data_loop.isRunning():
                self.tr_data_loop.exit()

        except Exception as e:
            self.log.error(f'onReceiveTrData: Error occured {e}')

    def OnReceiveMsg(self, screen, rqname, trcode, msg):
        self.log.debug(f'OnReceiveMsg {screen}, {rqname}, {trcode}, {msg}')

    # -------------------------------------------------------------------------------------------------------------------
    # OpenAPI+ 메서드
    # -------------------------------------------------------------------------------------------------------------------

    def block_request(self, *args, **kwargs):
        """
        Performs TR request
        :param args:
            rq_name; actually the description of trcode
            trcode
        :param kwargs:
            acc_no
            pw
            pw category: "00"
            search category
            screen_no
        :return: Returns the results for all items of the trcode output
                 in format of dataframe
        """

        rqname = args[0]
        self.log.debug(f'TR req name: {rqname} ##################')
        trcode = args[1].lower()
        screen = kwargs["screen"]
        if "output_items" not in kwargs.keys():
            self.tr_output[trcode] = None
        else:
            self.tr_output[trcode] = kwargs["output_items"]

        self._set_input_value(kwargs)

        # initialize remaining data flag
        self.tr_remained = False

        # initial request
        self.CommRqData(rqname, trcode, 0, screen)
        self.log.debug(f'Calling CommRqData #1 ...')

        # blocking until onReceiveTrData is called and self.tr_data gets filled
        self.tr_data_loop.exec_()
        result_df = self.tr_data.copy()

        # if there is more data to come, more requests are made
        i = 2
        while self.tr_remained:
            sleep(self.min_interval)
            self._set_input_value(kwargs)
            self.CommRqData(rqname, trcode, 2, screen)
            self.log.debug(f'Calling CommRqData #{i} ...')
            self.tr_data_loop.exec_()
            result_df.append(self.tr_data.copy())
            i += 1

        return self.tr_data

    def _set_input_value(self, kwargs):
        # set input
        for key in kwargs:
            kwarg_key = key.lower()
            if kwarg_key != "output" and kwarg_key != "screen":
                self.SetInputValue(key, kwargs[key])
                self.log.debug(f'SetInputValue({key}, {kwargs[key]})')

    def CommRqData(self, rqname, trcode, next, screen):
        """
        TR을 서버로 송신합니다.
        :param rqname: 사용자가 임의로 지정할 수 있는 요청 이름
        :param trcode: 요청하는 TR의 코드
        :param next: 0: 처음 조회, 2: 연속 조회
        :param screen: 화면번호 ('0000' 또는 '0' 제외한 숫자값으로 200개로 한정된 값
        :return: None
        """
        self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen)

    def SetInputValue(self, id, value):
        """
        TR 입력값을 설정하는 메서드
        :param id: TR INPUT의 아이템명
        :param value: 입력 값
        :return: None
        """
        self.ocx.dynamicCall("SetInputValue(QString, QString)", id, value)

    def GetRepeatCnt(self, trcode, rqname):
        """
        멀티데이터의 행(row)의 개수를 얻는 메서드
        :param trcode: TR코드
        :param rqname: 사용자가 설정한 요청이름
        :return: 멀티데이터의 행의 개수
        """
        count = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return count

    def CommKwRqData(self, arr_code, next, code_count, type, rqname, screen):
        """
        여러 종목 (한 번에 100종목)에 대한 TR을 서버로 송신하는 메서드
        :param arr_code: 여러 종목코드 예: '000020:000040'
        :param next: 0: 처음조회
        :param code_count: 종목코드의 개수
        :param type: 0: 주식종목 3: 선물종목
        :param rqname: 사용자가 설정하는 요청이름
        :param screen: 화면번호
        :return:
        """
        ret = self.ocx.dynamicCall("CommKwRqData(QString, bool, int, int, QString, QString)", arr_code, next,
                                   code_count, type, rqname, screen);
        return ret

    def GetCommData(self, trcode, rqname, index, item):
        """
        수신 데이터를 반환하는 메서드
        :param trcode: TR 코드
        :param rqname: 요청 이름
        :param index: 멀티데이터의 경우 row index
        :param item: 얻어오려는 항목 이름
        :return: 수신 데이터
        ex) 현재가출력 - openApi.GetCommData("opt00001", "주식기본정보", 0, "현재가");
        """
        data = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, index, item)
        return data.strip()

    def GetConditionLoad(self, block=True):
        """
        서버에 저장된 사용자 조건식을 조회해서 임시로 파일에 저장
        :param block:
        :return:
        """
        self.condition_loaded = False

        self.ocx.dynamicCall("GetConditionLoad()")
        if block:
            while not self.condition_loaded:
                pythoncom.PumpWaitingMessages()

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
        if block is True:
            self.tr_condition_loaded = False

        self.ocx.dynamicCall("SendCondition(QString, QString, int, int)", screen, cond_name, cond_index, search)

        if block is True:
            while not self.tr_condition_loaded:
                pythoncom.PumpWaitingMessages()

        if block is True:
            return self.tr_condition_data

    def SendConditionStop(self, screen, cond_name, index):
        """
        조건검색 실시간 중지 TR 을 송신
        :param screen: 화면번호
        :param cond_name: 조건명
        :param index: 조건명 인덱스
        :return:
        """
        self.ocx.dynamicCall("SendConditionStop(QString, QString, int)", screen, cond_name, index)

    def GetCommDataEx(self, trcode, rqname):
        """
        차트 조회 데이터를 배열로 받아온다
        :param trcode: 조회한 TR코드
        :param rqname: 조회한 TR명
        :return:
        조회 데이터가 많은 차트 경우 GetCommData()로 항목당 하나씩 받아오는 것 보다
        한번에 데이터 전부를 받아서 사용자가 처리할 수 있도록 배열로 받는다.
        """
        data = self.ocx.dynamicCall("GetCommDataEx(QString, QString)", trcode, rqname)
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
