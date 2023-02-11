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
        self.tr_data_loop = QEventLoop()

        # Data slots for Kiwoom
        self._set_signals_slots()

        self.tr_output = {}
        self.real_fid = {}

    def get_data(self, trcode, rqname, items):
        rows = self.GetRepeatCnt(trcode, rqname)
        if rows == 0:
            rows = 1

        data_list = []
        for row in range(rows):
            row_data = []
            for item in items:
                data = self.GetCommData(trcode, rqname, row, item)
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
        if trcode in [
            'KOA_NORMAL_BUY_KP_ORD',
            'KOA_NORMAL_SELL_KP_ORD',
            'KOA_NORMAL_KP_CANCEL',
            'KOA_NORMAL_KP_MODIFY',
            'KOA_NORMAL_BUY_KQ_ORD',
            'KOA_NORMAL_SELL_KQ_ORD',
            'KOA_NORMAL_KQ_CANCEL',
            'KOA_NORMAL_KQ_MODIFY',
        ]:
            # data = self.GetCommData()
            self.log.debug('call back')
            # self.parent.onRcvTrData(screen, rqname)
            return

        try:
            # remained data
            if next == '2':
                self.tr_remained = True
            else:
                self.tr_remained = False

            # tr_items
            # {
            #   'trcode': 'opw00018',
            #   'input': [{'계좌평가잔고내역요청': ['계좌번호', '비밀번호',...]}],
            #   'output': [
            #       {'계좌평가결과': ['총매입금액', '총평가금액',...]},
            #       {'계좌평가잔고개별합산': ['종목번호', '종목명',...]}
            #   ]
            # }

            # for output in self.tr_items['output']:
            # ex) record: 주식기본정보
            # record = list(output.keys())[0]
            # ex) items: ['종목코드', '종목명', '결산월', ..., '유통비율']
            # items = list(output.values())[0]

            items = []
            for output in self.tr_items['output']:
                items += list(output.values())[0]

            rows = self.GetRepeatCnt(trcode, rqname)
            if rows == 0:
                rows = 1

            data_list = []
            for row in range(rows):
                row_data = []
                for item in items:
                    data = self.GetCommData(trcode, rqname, row, item)
                    self.log.debug(f"kwm_api.OnReceiveTrData: data from GetCommData..\n{data}")
                    row_data.append(data)
                data_list.append(row_data)

            # data to DataFrame
            df = pd.DataFrame(data=data_list, columns=items)
            self.log.debug(df.head(3))
            self.tr_data = df
            self.received = True

            if self.tr_data_loop.isRunning():
                self.tr_data_loop.exit()

        except:
            pass


    def OnReceiveRealData(self, code, rtype, data):
        self.log.debug(f'OnReceiveRealData {code}')
        """실시간 데이터를 받는 시점에 콜백되는 메소드입니다.

        Args:
            code (str): 종목코드
            rtype (str): 리얼타입 (주식시세, 주식체결, ...)
            data (str): 실시간 데이터 전문
        """
        # get real data
        real_data = {"code": code}
        for fid in self.real_fid[code]:
            val = self.GetCommRealData(code, fid)
            real_data[fid] = val

        # call back
        self.parent.handle_rcv_real_data(real_data)

    def _set_signals_slots(self):
        self.ocx.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.ocx.OnReceiveRealData.connect(self.OnReceiveRealData)

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
            next: 0 or 2
            screen_no
        :return: Returns the results for all items of the trcode output
                 in format of dataframe
        """
        try:
            kwargs["next"]
            kwargs["screen"]
        except Exception as e:
            self.log.error("not enough kwargs in block_request")
            self.log.error(e)

        rqname = args[0]
        self.log.debug(f'TR req name: {rqname} ##################')
        trcode = args[1].lower()
        lines = parser.read_enc(trcode)
        # self.tr_items 는 가능한 모든 output 항목 들의 list
        self.tr_items = parser.parse_dat(trcode, lines)
        self.log.debug(f'tr_items ##################\n {self.tr_items}')
        next = kwargs["next"]
        screen = kwargs["screen"]

        # set input
        for key in kwargs:
            s_k = key.lower()
            if s_k != "output" and s_k != "next" and s_k != "screen":
                self.SetInputValue(key, kwargs[key])

        # initialize
        self.received = False
        self.tr_remained = False

        # request
        self.CommRqData(rqname, trcode, next, screen)
        # if not self.received:
        self.tr_data_loop.exec_()
        result_df = self.tr_data.copy()

        # if there is more data to come
        while self.tr_remained:
            self.CommRqData(rqname, trcode, 2, screen)
            self.tr_data_loop.exec_()
            result_df.append(self.tr_data)

        return self.tr_data
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

    def SendOrder(self, rqname, screen, accno, order_type, code, quantity, price, hoga, order_no):
        """
        주식 주문을 서버로 전송하는 메서드
        시장가 주문시 주문단가는 0으로 입력해야 함 (가격을 입력하지 않음을 의미)
        :param rqname: 사용자가 임의로 지정할 수 있는 요청 이름
        :param screen: 화면번호 ('0000' 또는 '0' 제외한 숫자값으로 200개로 한정된 값
        :param accno: 계좌번호 10자리
        :param order_type: 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정
        :param code: 종목코드
        :param quantity: 주문수량
        :param price: 주문단가
        :param hoga: 00: 지정가, 03: 시장가,
                     05: 조건부지정가, 06: 최유리지정가, 07: 최우선지정가,
                     10: 지정가IOC, 13: 시장가IOC, 16: 최유리IOC,
                     20: 지정가FOK, 23: 시장가FOK, 26: 최유리FOK,
                     61: 장전시간외종가, 62: 시간외단일가, 81: 장후시간외종가
        :param order_no: 원주문번호로 신규 주문시 공백, 정정이나 취소 주문시에는 원주문번호를 입력
        :return:
        """
        ret = self.ocx.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                   [rqname, screen, accno, order_type, code, quantity, price, hoga, order_no])
        return ret

    def SetInputValue(self, id, value):
        """
        TR 입력값을 설정하는 메서드
        :param id: TR INPUT의 아이템명
        :param value: 입력 값
        :return: None
        """
        self.ocx.dynamicCall("SetInputValue(QString, QString)", id, value)

    def DisconnectRealData(self, screen):
        """
        화면번호에 대한 리얼 데이터 요청을 해제하는 메서드
        :param screen: 화면번호
        :return: None
        """
        self.ocx.dynamicCall("DisconnectRealData(QString)", screen)

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

    def GetDataCount(self, record):
        """
        레코드의 반복개수를 반환하는 메서드
        :param record: 레코드명
        :return: 레코드 반복개수
        ex) openApi.GetDataCount("주식기본정보");
        """
        count = self.ocx.dynamicCall("GetDataCount(QString)", record)
        return count

    def GetOutputValue(self, record, repeat_index, item_index):
        """
        레코드의 반복순서와 아이템의 출력순서에 따라 수신데이터를 반환하는 메서드
        :param record:
        :param repeat_index: 반복 순서
        :param item_index: 아이템 순서
        :return: 수신 데이터
        ex) openApi.GetOutputValue("주식기본정보", 0, 36);
        """
        count = self.ocx.dynamicCall("GetOutputValue(QString, int, int)", record, repeat_index, item_index)
        return count

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

    def GetCommRealData(self, code, fid):
        """
        실시간 시세 데이터를 반환하는 메서드
        :param code: 종목 코드 (OnReceiveRealData 첫번째 매개변수를 사용)
        :param fid: 실시간 아이템
        :return: 수신 데이터
        ex) 현재가출력 - openApi.GetCommRealData("039490", 10);
        """
        data = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, fid)
        return data

    def GetChejanData(self, fid):
        """
        체결잔고 데이터를 반환하는 메서드
        :param fid: 체결잔고 아이템
        :return: 수신 데이터
        ex) 현재가출력 - oepnApi.GetChejanData(10);
        """
        data = self.ocx.dynamicCall("GetChejanData(int)", fid)
        return data

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

    def SetRealReg(self, screen, code_list, fid_list, opt_type):
        """
        실시간 등록을 하는 메서드
        :param screen:
        :param code_list: 실시간 등록할 종목코드(복수종목가능 - "종목1;종목2;...")
        :param fid_list: 실시간 등록할 FID("FID1;FID2;...")
        :param opt_type: "0', '1' 타입
        :return: 통신결과
        strRealType
        “0” 으로 하면 같은화면에서 다른종목 코드로 실시간 등록을 하게 되면 마지막에 사용한
         종목코드만 실시간 등록이 되고 기존에 있던 종목은 실시간이 자동 해지됨.
        “1”로 하면 같은화면에서 다른 종목들을 추가하게 되면 기존에 등록한 종목도 함께
         실시간 시세를 받을 수 있음.
        꼭 같은 화면이여야 하고 최초 실시간 등록은 “0”으로 하고 이후부터 “1”로 등록해야함.
        """
        ret = self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen, code_list, fid_list,
                                   opt_type)
        return ret

    def SetRealRemove(self, screen, del_code):
        """
        종목별 실시간 해제
        :param screen: 실시간 해제할 화면 번호
        :param del_code: 실시간 해제할 종목
        :return: 통신결과
        """
        ret = self.ocx.dynamicCall("SetRealRemove(QString, QString)", screen, del_code)
        return ret

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
