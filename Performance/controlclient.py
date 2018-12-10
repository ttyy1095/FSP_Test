#-*-coding:utf-8-*-
import os
import socket  # 导入 socket 模块
import json
import sys
import uuid
import time
import paramiko
import psutil

from protocol import *
_path = ".."
sys.path.append(_path)
from Config.config import *
from ClientControler.simulatorcontroler import ClientSimulator


cs_list = []



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

def get_res_rate():

    cpu_rate = psutil.cpu_percent(interval=1)
    mem_rate = psutil.virtual_memory().percent
    internet = psutil.net_io_counters()
    io_sent1 = internet.bytes_sent
    io_recv1 = internet.bytes_recv
    time.sleep(1)
    internet = psutil.net_io_counters()
    io_sent2 = internet.bytes_sent
    io_recv2 = internet.bytes_recv
    upload_speed = (io_sent2-io_sent1)/1024
    download_speed = (io_recv2-io_recv1)/1024

    print(cpu_rate,mem_rate,upload_speed,download_speed)

    data = {"command_id": REPORT_RES_RATE, "cpu_rate": cpu_rate, "mem_rate": mem_rate, "upload_speed": upload_speed,"download_speed":download_speed}
    return json.dumps(data)
if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建 socket 对象
    s.connect(('192.168.6.65', 5566))
    myip = s.getsockname()[0]
    kill_all_client()
    while True:
        s.send(get_res_rate())
        data = s.recv(1024).decode(encoding='utf8')
        try:
            msg = json.loads(data)
            print msg
            if msg['command_id'] == OPEN_SIMULATOR:
                room_list = msg['room_list']
                username_prefix = msg['username_prefix']
                start_index = msg['start_index']
                end_index = msg['end_index']
                simulator_index = msg['simulator_index']
                userlist = []
                for i in range(int(start_index), int(end_index) + 1):
                    userindex = str(i).zfill(2) if i < 10 else str(i)
                    userlist.append(username_prefix + userindex)
                pwd = msg['userpwd']
                cs = ClientSimulator(simulator_index,room_list, userlist, pwd)
                cs_list.append(cs)
                cs.start()
                print('open simulator client')
            elif msg['command_id'] == CLOSE_SIMULATOR:
                print('close simulator')
                simulator_index = msg['simulator_index']
                for cs in cs_list:
                    if cs.simulator_index == simulator_index:
                        cs.stop()
                        time.sleep(1)

            elif msg['command_id'] == UPLOAD_LOG:
                print('upload log')
                uplaod_log()
        except Exception as e:
            print("error data",e)
