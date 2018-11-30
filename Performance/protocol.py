#-*-coding:utf-8-*-
from enum import Enum
LOGIN = 1000
OPEN_REALCLIENT = 1001
OPEN_SIMULATOR = 1002
UPLOAD_LOG = 1003

class ClientType(Enum):
    controler = 0
    performer = 1

