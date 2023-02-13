import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QEventLoop
from kwm_connect import Kwm
from logging_handler import LoggingHandler
from kwm_type import *


class KwmRealApi(QObject, LoggingHandler):
    def __init__(self, parent=None):
        super().__init__()
        self.handler = parent
        # OCX instance
        self.ocx = Kwm().ocx

        # Event loop
        self.tr_data_loop = QEventLoop()

        # Data slots for Real data
        self.ocx.OnReceiveRealData.connect(self.OnReceiveRealData)
        self.ocx.OnReceiveChejanData.connect(self.OnReceiveChejanData)

        self.real_fid = {}

    def set_real_reg(self, screen, code_list, fid_list, opt_type):
        """
        Calls SetRealReg after converting list args to string args
        :param screen:
        :param code_list: ["005930", "000660"]
        :param fid_list: ["215", "20", "214"]
        :param opt_type: "0" deregister pre-registered codes and register new ones
                         "1" register new ones in addition to the pre-registered
        :return:
        """
        # register fid
        if opt_type == "0":
            self.real_fid = {}

        for code in code_list:
            self.real_fid[code] = fid_list

        self.log.debug(f'Real reginstering...')
        self.log.debug(f'\tcodes {code_list}\tfids {fid_list}')

        self.SetRealReg(screen,
                        ";".join(code_list),
                        ";".join(fid_list),
                        opt_type)

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
        arg_list = [screen, code_list, fid_list, opt_type]
        self.log.debug(f'SetRealReg({arg_list}) ...')
        ret = self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen, code_list, fid_list,
                                   opt_type)
        if ret is not None:
            self.log.debug(f'SetRealReg result: {ret} {ERR_CODE[ret]}')
        return ret

    def SetRealRemove(self, screen, del_code):
        """
        종목별 실시간 해제
        :param screen: 실시간 해제할 화면 번호
        :param del_code: 실시간 해제할 종목
        :return: 통신결과 (None if success)
        """
        arg_list = [screen, del_code]
        self.log.debug(f'SetRealRemove({arg_list}) ...')
        ret = self.ocx.dynamicCall("SetRealRemove(QString, QString)", screen, del_code)
        if ret is not None:
            self.log.debug(f'SetRealRemove result: {ret} {ERR_CODE[ret]}')
        return ret

    def OnReceiveRealData(self, code, rtype, data):
        """실시간 데이터를 받는 시점에 콜백되는 메소드입니다.

        Args:
            code (str): 종목코드
            rtype (str): 리얼타입 (주식시세, 주식체결, ...)
            data (str): 실시간 데이터 전문
        """
        self.log.debug(f'OnReceiveRealData code:{code} rtype:{rtype} data:{data}')

        # self.real_fid = {code: fid_list, ...}
        # if self.real_fid is empty or the code is not registered, just ignore
        # the incoming data
        if bool(self.real_fid) or code not in self.real_fid.keys():
            return

        ###### returns data as it is
        # call back
        self.handler.handle_real_data(code, rtype, data)

        ###### returns a dictionary result; real_data
        # real_data = {"code": "005930", fid1: val1, fid2: val2 ...}
        # real_data = {"code": code}
        # for fid in self.real_fid[code]:
        #     val = self.GetCommRealData(code, fid)
        #     real_data[fid] = val

        # call back
        # self.handler.handle_real_data(rtype, real_data)

    def DisconnectRealData(self, screen):
        """
        화면번호에 대한 리얼 데이터 요청을 해제하는 메서드
        :param screen: 화면번호
        :return: None
        """
        self.ocx.dynamicCall("DisconnectRealData(QString)", screen)

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

    def OnReceiveChejanData(self, gubun, item_cnt, fid_list):
        """
        주문접수, 체결, 잔고 변경시 이벤트가 발생
        :param gubun: '0': 접수, 체결, '1': 잔고 변경
        :param item_cnt: 아이템 갯수
        :param fid_list: fid list
        :return:
        """
        chejan_data = {}
        for fid in fid_list.split(';'):
            data = self.GetChejanData(fid)
            chejan_data[fid] = data

        self.main.handle_chejan_data(gubun, chejan_data)


    def GetChejanData(self, fid):
        """
        체결잔고 데이터를 반환하는 메서드
        :param fid: 체결잔고 아이템
        :return: 수신 데이터
        ex) 현재가출력 - oepnApi.GetChejanData(10);
        """
        data = self.ocx.dynamicCall("GetChejanData(int)", fid)
        return data


if not QApplication.instance():
    app = QApplication(sys.argv)