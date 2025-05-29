
import sys
import logging

DEBUG = logging.DEBUG

class Log(logging.Logger):

    DEBUG2 = 5

    def __init__(self, name="wgpy", level=logging.INFO):
        super().__init__(name, level)

        formatter = logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(funcName)s:%(lineno)d %(message)s", datefmt="%Y-%m-%d-%H:%M:%S")

        self.consoleHandler = logging.StreamHandler(stream=sys.stdout)

        self.consoleHandler.setFormatter(formatter)

        self.addHandler(self.consoleHandler)
        self.setLevel(level)

    def debug2(self, msg):
        self.log(self.DEBUG2, msg)

logger = Log()

