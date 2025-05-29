
import sys
import logging


class Log(logging.Logger):

    DEBUG2 = 5

    def __init__(self, name="wgpy", level=logging.INFO):
        super().__init__(name, level)
        # self.logger = logging.getLogger(name)

        formatter = logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(funcName)s:%(lineno)d %(message)s", datefmt="%Y-%m-%d-%H:%M:%S")

        self.consoleHandler = logging.StreamHandler(stream=sys.stdout)

        self.consoleHandler.setFormatter(formatter)

        self.addHandler(self.consoleHandler)
        self.setLevel(level)


logger = Log()

