from queue import Queue
from pykiwoom.kiwoom_req_handler import KwmRqHandler
from PyQt5.QtCore import pyqtSignal, pyqtSlot


# This wrapper is for command queue
# All command queues are supposed to send a signal to the req handler
# So that, the handler gets to know that a command is in the queue and
# pop it out and send it
def command_q(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        # args[0] is self
        # it emits a signal to the req handler
        args[0].rq_handler.run_trigger.emit()
        return result
    return wrapper


class KwmQMgr:

    def __init__(self):
        # method queue
        self.method_cqueue = Queue()
        self.method_dqueue = Queue()

        # tr queue
        self.tr_cqueue = Queue()
        self.tr_dqueue = Queue()

        # order queue
        self.order_cqueue = Queue()

        # real queue
        self.real_cqueue = Queue()
        self.real_dqueues = Queue()

        # condition queue
        self.cond_cqueue = Queue()
        self.cond_dqueue = Queue()
        self.tr_cond_dqueue = Queue()
        self.real_cond_dqueue = Queue()

        # chejan queue
        self.chejan_dqueue = Queue()

        self.rq_handler = KwmRqHandler(
            # method queue
            self.method_cqueue,
            self.method_dqueue,
            # tr queue
            self.tr_cqueue,
            self.tr_dqueue,
            # order queue
            self.order_cqueue,
            # real queue
            self.real_cqueue,
            self.real_dqueues,
            # condition queue
            self.cond_cqueue,
            self.cond_dqueue,
            self.tr_cond_dqueue,
            self.real_cond_dqueue,
            # chejan queue
            self.chejan_dqueue,
            parent=self
        )

        # connect trigger signal to rq_handler
        # self.run_req_handler.connect(self.rq_handler.run)

        self.rq_handler.start()

    # method
    @command_q
    def put_method(self, cmd):
        self.method_cqueue.put(cmd)

    def get_method(self):
        return self.method_dqueue.get()

    # tr
    @command_q
    def put_tr(self, cmd):
        self.tr_cqueue.put(cmd)

    def get_tr(self):
        return self.tr_dqueue.get()

    # order
    @command_q
    def put_order(self, cmd):
        self.order_cqueue.put(cmd)

    # real
    @command_q
    def put_real(self, cmd):
        self.real_cqueue.put(cmd)

    def get_real(self):
        return self.real_dqueues.get()

    # condition
    @command_q
    def put_cond(self, cmd):
        self.cond_cqueue.put(cmd)

    def get_cond(self, real=False, method=False):
        if method is True:
            return self.cond_dqueue.get()
        elif real is True:
            return self.real_cond_dqueue.get()
        else:
            return self.tr_cond_dqueue.get()

    def get_chejan(self):
        return self.chejan_dqueue.get()
