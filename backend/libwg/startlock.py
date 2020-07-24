
from threading import Lock

__all__ = ("START_LOCK")

START_LOCK = Lock()
START_LOCK.acquire()