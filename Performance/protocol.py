#-*-coding:utf-8-*-
from enum import Enum
LOGIN = 1000

OPEN_SIMULATOR = 1001
UPLOAD_LOG = 1003

class ClientType(Enum):
    controler = 0
    performer = 1

# 协议说明
# 通知控制客户端打开压测工具
# {"command_id":1001,"room_list":["107894","107916"], "username_prefix":"jaxa", "start_index":0,"end_index":60,"userpwd":"000000" }
# 返回打开登录结果
{"comamnd_id":1002,"result":0}

# 通知控制客户端关闭压测工具
# {"command_id":1002}


# 通知控制客户端上传日志
{"command_id":1003}
# 控制客户端上传日志回复
{"comamnd_id":1004,"result":0}

