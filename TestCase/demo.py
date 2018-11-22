#-*-coding:utf-8-*-

import os
import time
# rq = time.strftime('%Y-%m-%d', time.localtime(time.time()))
# report_path = os.path.join(os.getcwd(), "report", rq)
# print report_path
# if not os.path.exists(report_path):
#     os.mkdir(report_path)

from kazoo.client import KazooClient

# zk = KazooClient(hosts="192.168.7.114:2181")
# zk.start()
# print zk.get_children("/fsp/msaaa")

# import pytest
#
# @pytest.fixture(scope="session")
# def init(request):
#     print "##########",request.param
#
# @pytest.mark.parametrize("init",[111,222,333],indirect=True)
# @pytest.mark.parametrize("i,exp",[(1,2),(2,3),(4,5)])
# def test_add(i,exp):
#
#     assert i+1 == exp


import win32api
import win32con
import win32gui
import win32ui
import win32console
import win32process
import os
import signal
import socket
MAIN_HWND = 0
from ctypes import *
# class Rect(Structure):
#     _fields_=[('Left',c_long),('Top',c_long),('Right',c_long),('Bottom',c_long)]
# rect = Rect()
# rsp = win32gui.GetWindowRect(2964284)
# print rsp

import psutil
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('114.114.114.114', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

from lxml import etree

def choose_server(service_type,group_name,use_specialline=False):
    """
    修改配置文件，使客户端能登录到指定服务器上
    :param service_type:
    :param group_name:
    :param use_specialline:
    :return:
    """
    testdata_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'TestData')
    default_conf = os.path.join(testdata_path,'rule-config_Transnational.xml')
    tree = etree.parse(default_conf)

    r = tree.xpath('//IPRuleSet')[0]
    r.clear()
    iprule = etree.Element('IPRule', {"serverType": service_type})
    ip = etree.Element('IP')
    ip.text = get_host_ip()
    groupname = etree.Element("GroupName")
    groupname.text = group_name
    iprule.append(ip)
    iprule.append(groupname)
    r.append(iprule)
    if use_specialline:
        ValueOfUseSpecialLineConfig = tree.find('//TransnationalConfig/ValueOfUseSpecialLineConfig')
        ValueOfUseSpecialLineConfig.text = '0.01'
    xml_str =  etree.tostring(tree,encoding="utf-8",pretty_print=True)
    xml_path = os.path.join(testdata_path,'rule_config_temp.xml')
    with open(xml_path,'w') as f:
        f.write(xml_str)
    return xml_path
# print etree.tostring(tree,encoding="utf-8",pretty_print=True)

# choose_server('gs','gs_group1',True)
# print etree.tostring(r[0])
import re,datetime

print time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

# with open(r'C:\Users\huangjie\Documents\Inpor\FMClient\log\new\vncmp-DESKTOP-JPRBBOB-10-54-18.log.text','r') as f:
#     lines = f.read()
#
#     start_time = re.findall(r'(\d{2}:\d{2}:\d{2})\.\d{6}',lines)[0]
#     start_time = time.mktime(time.strptime('2018-01-01 %s'%start_time,'%Y-%m-%d %H:%M:%S'))
#     recv_time = re.findall(r'(\d{2}:\d{2}:\d{2})\.\d{6}.*?VideoDecoder:VIDEO_Decode_StartDecompress success',lines)[0]
#     recv_time = time.mktime(time.strptime('2018-01-01 %s'%recv_time,'%Y-%m-%d %H:%M:%S'))
#
#     recv_time-start_time
    # for line in  lines:
    #     print line
