
import sys
import logging


class Logger:

    DEBUG2 = 5

    def __init__(self, log_name="wgpy", level=logging.INFO):
        self.logger = logging.getLogger(log_name)

        formatter = logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(funcName)s:%(lineno)d %(message)s", datefmt="%Y-%m-%d-%H:%M:%S")

        self.consoleHandler = logging.StreamHandler(stream=sys.stdout)

        self.consoleHandler.setFormatter(formatter)

        self.logger.addHandler(self.consoleHandler)
        self.logger.setLevel(level)

    def debug2(self, msg):
        self.logger.log(self.DEBUG2 ,msg)
    
    def debug(self, msg):
        self.logger.debug(msg)
    def info(self, msg):
        self.logger.info(msg)
    def warning(self, msg):
        self.logger.warning(msg)
    def error(self, msg):
        self.logger.error(msg)
    def critical(self, msg):
        self.logger.critical(msg)
    
    def setLevel(self, level):
        self.logger.setLevel(level)

logger = Logger(level=logging.DEBUG)
