from PyQt5.QAxContainer import *
from connector_interface import ConnectorInterface
from sender_interface import SenderInterface
from receiver_interface import ReceiverInterface


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self.connector = ConnectorInterface(self)
        self.sender = SenderInterface(self)
        self.receiver = ReceiverInterface(self)
        self.tr_handler = {}
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self.connector.event_connect)
        self.OnReceiveTrData.connect(self.receiver.receive_tr_data)

    def connect(self):
        self.connector.comm_connect()

    def reg_transaction(self, transaction):
        self.tr_handler.update({transaction.get_rqname(): transaction})
