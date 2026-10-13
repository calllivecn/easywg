

import tomllib
import asyncio
import argparse
import threading
from pathlib import Path


CHECK_PORT = 19000
CHECK_TIMEOUT = 5
CHECK_FAILED_COUNT = 6



# 加载配置文件
def loadconf(conf: Path):
    with open(conf, "rb") as f:
        return tomllib.load(f)


class Argument(argparse.ArgumentParser):

    def __init__(self, **kwargs):
        super().__init__(add_help=False, **kwargs)

        self._positionals = self.add_argument_group("位置参数")
        self._optionals = self.add_argument_group("通用选项")

        self.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='打印帮助信息后退出')


def start_thread(*args, **kwargs):
    th = threading.Thread(*args, **kwargs)
    th.start()
    return th


def get_event():
    return threading.Event()


async def run_sync(func, *args, **kwargs):
    # pyroute2 同步 API 自己运行事件循环，必须在工作线程内调用。
    # 取消协程不会停止线程；等待操作完成，避免它与接口清理竞争。
    task = asyncio.create_task(asyncio.to_thread(func, *args, **kwargs))
    try:
        return await asyncio.shield(task)
    except asyncio.CancelledError:
        await task
        raise
