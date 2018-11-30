#-*-coding:utf-8-*-
import os
import socket  # 导入 socket 模块
import json
import sys
import uuid
from protocol import *
_path = ".."
sys.path.append(_path)

from ClientControler.clientcontroler import Client


s = socket.socket()  # 创建 socket 对象
s.connect(('192.168.6.65', 5566))

def kill_all_client():
    os.system('taskkill /im /f FastMeeting.exe')
    os.system('taskkill /im /f ClientSimulatorUI.exe')

def open_realclient(prefix,num,room_id,pwd):
    for i in range(0,num):
        if 1 < 10:
            username = '%s0%s'%(prefix,i)
        else:
            username = '%s%s'%(prefix,i)
        client_flag = uuid.uuid4()
        client = Client(client_flag)
        client.login(username,pwd,room_id)
        client.publishVideo()
        client.publishAudio()



def exec_command(data):
    if data['command_id'] == OPEN_REALCLIENT:
        room_id = data['room_id']
        start_username = data['start_username']
        end_username = data['end_username']
        pwd = data['pwd']
        print('open real client')
    elif data['command_id'] == OPEN_SIMULATOR:
        print('open simulator client')
    elif data['command_id'] == UPLOAD_LOG:
        print('upload log')

while True:
    data = s.recv(1024).decode(encoding='utf8')
    try:
        json_data = json.loads(data)
        print json_data
    except Exception as e:
        print("error data")
