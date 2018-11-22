#-*-coding:utf-8-*-
from enum import Enum

# FSP相关环境配置
kafkaCluster = "192.168.7.111:9092"
zookeeperAddr = "192.168.7.111:2181"
GC_GROUP_TOPIC = "gc_group_01"
SC_GROUP_TOPIC = "sc_group_01"
app_id = "app_test"
room_id = "1234567"
AS_TOPIC = "lizzietest"
rule_server = "192.168.7.71:22"
AUTO_TEST_SERVER = "192.168.7.70"
REDIS={'host':'192.168.7.111','port':'6379'}

#jenkins环境配置
jenkins_url = "http://192.168.5.30:8088/jenkins"
jenkins_user = "jessie"
jenkins_password = "670baa6f76ef2944d0ff0e5e75c169c5"

#testlink环境配置
testlink_url = "http://192.168.5.195/testlink/lib/api/xmlrpc/v1/xmlrpc.php"
testlink_devkey = "f5350af1b949aaab47ca2363e30989dc"

#zentao环境配置
zentao_url = "http://192.168.5.68/zentao/"
zentao_user = "huangjie"
zentao_password = "Hj1qaz2w"
zentao_product = "基础服务平台"
zentao_project = "基础服务平台服务子系统2.8"

OC_PATH = r"D:\Client\3.15.5.33"
NC_PATH = r"D:\Client\NC2"


USERA_NAME = 'ptAutoTest00'
USERA_PWD = '000000'
USERA_USERID = '1438593'
USERB_NAME = 'ptAutoTest01'
USERB_PWD = '000000'
USERB_USERID = '1438594'
ROOM1_ID = '107926'

# 确认每台服务器都是真实存在的,服务instance_id与部署时一致
# ice服务器务必要按照启动node所在目录命名（node1，node2）

services = {"gc":{"process_name":"group_controller","servers":{"gc1":"192.168.7.73","gc2":"192.168.7.160","gc3":"192.168.7.63"}},
            "gs":{"process_name":"group_server","servers":{"gs1":"192.168.7.72","gs2":"192.168.7.105","gs3":"192.168.7.106"}},
            "icegrid":{"process_name":"ice_server","servers":{"node1":"192.168.7.105"}},
            "km":{"process_name":"moniter_agent","servers":{}},
            "ma":{"process_name":"moniter_agent","servers":{"ma_gs1":"192.168.7.72","ma_gs2":"192.168.7.105","ma_gs3":"192.168.7.106","ma_ss1":"192.168.7.104","ma_ss2":"192.168.7.153","ma_ss3":"192.168.7.144"}},
            "ms":{"process_name":"moniter_server","servers":{"ms1":"192.168.7.73","ms2":"192.168.7.160"}},
            "rule":{"process_name":"rule_server","servers":{"rule1":"192.168.7.71"}},
            "sc":{"process_name":"stream_controller","servers":{"sc1":"192.168.7.63","sc2":"192.168.7.64","sc3":"192.168.7.65"}},
            "ss":{"process_name":"stream_server","servers":{"ss1":"192.168.7.104","ss2":"192.168.7.153","ss3":"192.168.7.144"}},
            "vnc_gs":{"process_name":"vnc_group_server","servers":{}}}


class Service_Type(Enum):
    EnumAVService = 0
    EnumVNCService = 1
    EnumDataSyncService = 2

class MediaType(Enum):
    EnumVNC = 0
    EnumAudio = 1
    EnumVideo = 2


if __name__ == '__main__':
    print Service_Type.EnumAVService.value