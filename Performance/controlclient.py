#-*-coding:utf-8-*-
import os
import socket  # 导入 socket 模块
import json
import sys
import uuid
import time
import paramiko

from protocol import *
_path = ".."
sys.path.append(_path)
from Config.config import *
from ClientControler.clientcontroler import Client
from ClientControler.simulatorcontroler import ClientSimulator

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # 创建 socket 对象
s.connect(('192.168.6.65', 5566))
myip = s.getsockname()[0]
def uplaod_log():
    def sftp_upload(host, port, username, password, local, remote):
        sf = paramiko.Transport((host, port))
        sf.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(sf)
        remote_path = remote + '/' + os.path.basename(local)+'/'
        try:
            try:
                sftp.mkdir(remote)
                sftp.mkdir(remote_path)
            except Exception as e:
                print("path exist",e)
            if os.path.isdir(local):  # 判断本地参数是目录还是文件
                for f in os.listdir(local):  # 遍历本地目录
                    sftp.put(os.path.join(local,f), remote_path + f)  # 上传目录中的文件
            else:
                sftp.put(local, remote)  # 上传文件
        except Exception, e:
            print('upload exception:', e)
        sf.close()

    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    window_path = os.path.join(SIMULATOR_PATH, 'log', date)
    remote = '/AutoTest/Performance/log/%s/'%(myip)
    sftp_upload('192.168.7.70',22,'root','123456',window_path,remote)



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
        room_list = data['room_list']
        username_prefix = data['username_prefix']
        start_index = data['start_index']
        end_index = data['end_index']
        userlist = []
        for i in range(int(start_index),int(end_index)+1):
            userindex = str(i).zfill(2) if i<10 else str(i)
            userlist = userlist.append(username_prefix+userindex)
        pwd = data['pwd']
        cs = ClientSimulator(room_list,userlist,pwd)
        cs.start()
        print('open simulator client')
    elif data['command_id'] == UPLOAD_LOG:
        print('upload log')



if __name__ == '__main__':
    # s.send('{"command_id":1001,"room_list":["107894"], "username_prefix":"jaxa", "start_index":0,"end_index":10,"userpwd":"000000" }')

    # uplaod_log()
    while True:

        data = s.recv(1024).decode(encoding='utf8')
        try:
            json_data = json.loads(data)
            print json_data
        except Exception as e:
            print("error data")
