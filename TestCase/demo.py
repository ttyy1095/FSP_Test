#-*-coding:utf-8-*-

import os
import time,json
# rq = time.strftime('%Y-%m-%d', time.localtime(time.time()))
# report_path = os.path.join(os.getcwd(), "report", rq)
# print report_path
# if not os.path.exists(report_path):
#     os.mkdir(report_path)

from kazoo.client import KazooClient

zk = KazooClient(hosts="192.168.7.111:2181")
zk.start()
print zk.get_children("/fsp/ms")

print json.loads(zk.get("/fsp/rule/rule1")[0])

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
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.7.104', port=22, username="root", password="123456")
stdin,stdout,stderr = ssh.exec_command("ps -ef|grep moniter_agents|grep -v grep|awk '{print $2}'|xargs kill")
# stdin,stdout,stderr = ssh.exec_command("ls /femeeting/jax")
# stdin,stdout,stderr = ssh.exec_command("grep -c 'Invoke TimeTask' `ls -l /fsmeeting/fsp_sss_stream/ms/log/2018-11-23/moniter_server_*|sed -n '$p'|awk '{print $NF}'`",get_pty=True)
print stdout.read()
# print stdin.read()
# print stdout.read()
print stderr.read()
print stdout.channel.recv_exit_status()