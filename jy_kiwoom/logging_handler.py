import logging
logging.basicConfig(level=logging.DEBUG)

class LoggingHandler:
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(self.__class__.__name__)
