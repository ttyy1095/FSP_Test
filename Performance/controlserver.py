#-*-coding:utf-8-*-

import json
import time
from protocol import *
import gevent
from collections import OrderedDict
from gevent import socket,monkey
import threading
import MySQLdb

db = MySQLdb.connect("192.168.7.108",'root','123456','fsp_preformance',charset='utf8')
cursor = db.cursor()

controlclient_list = []
class ControlClient(object):
    def __init__(self,skt,ip):
        self.skt = skt
        self.ip = ip

def hand_client_con(client):
    try:
        isNormar=True
        while isNormar:
            data = client.skt.recv(1024)

            if not data:
                time.sleep(1.5)
                continue
            print('recv data from:%s data:%s'%(client.ip,data))
            try:
                msg = json.loads(data)
                if msg['command_id'] == OPEN_SIMULATOR:
                    get_conn(msg['ip']).send(data)
                elif msg['command_id'] == CLOSE_SIMULATOR:
                    get_conn(msg['ip']).send(data)
                elif msg['command_id'] == REPORT_RES_RATE:
                    cpu_rate = msg['cpu_rate']
                    mem_rate = msg['mem_rate']
                    upload_speed = msg['upload_speed']
                    download_speed = msg['download_speed']
                    sql = "SELECT * FROM fsp_preformance_serverstate WHERE ip='%s'"%client.ip
                    cursor.execute(sql)
                    if len(cursor.fetchall())==0:
                        sql = """INSERT INTO fsp_preformance_serverstate 
                              (ip,cpu_rate,mem_rate,upload_speed,download_speed) VALUES ('%s','%s','%s','%s','%s')"""%\
                              (client.ip,cpu_rate,mem_rate,upload_speed,download_speed)
                    else:
                        sql = """UPDATE fsp_preformance_serverstate SET cpu_rate='%s',mem_rate='%s',upload_speed='%s',
                                download_speed='%s' WHERE ip='%s'"""%(cpu_rate,mem_rate,upload_speed,download_speed,client.ip)
                    cursor.execute(sql)
                    db.commit()
            except Exception as e:
                print(e)
                print("error json data")

    except Exception as e:
        isNormar = False
        print("except Exception:%s"%e)
        print("lost connectting from:%s"%client.ip)
        controlclient_list.remove(client)
        sql = "UPDATE fsp_preformance_slaveserver SET state=0 WHERE ip='%s';"%client.ip
        cursor.execute(sql)
        db.commit()

def get_conn(ip):
    for client in controlclient_list:
        if client.ip == ip:
            return client.skt
    print("%s not connected"%ip)

def update_res_rate(ip,cpu,mem,upload_speed,download_speed):

    pass

def main():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0',5566))
    s.listen(500)
    print('Server', socket.gethostbyname('0.0.0.0'), 'listening ...')
    while True:
        cli,(ip,cport) = s.accept()
        print("(%s,%s connected...)" % (ip, cport))
        sql = "UPDATE fsp_preformance_slaveserver SET state=1 WHERE ip='%s';"%ip
        cursor.execute(sql)
        db.commit()
        client = ControlClient(cli,ip)
        controlclient_list.append(client)
        t=threading.Thread(target=hand_client_con,args=(client,))
        t.setDaemon(True)
        t.start()
    s.close()
    db.close()


monkey.patch_all()
conn_list = []
conn_dict = {}
def server(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0',port))
    s.listen(500)
    print('Server', socket.gethostbyname('0.0.0.0'), 'listening ...')
    while True:
        cli,(ip,cport) = s.accept()
        conn_dict[ip] = cli
        print("(%s,%s connected...)"%(ip,cport))
        gevent.spawn(handle_request,cli)

def handle_request(conn):
    try:
        while True:
            data = conn.recv(1024)
            print('recv',data)
            if not data:
                conn.shutdown(socket.SHUT_WR)
                break
            try:
                json_data = json.loads(data,object_pairs_hook=OrderedDict)
                if json_data['command_id'] == OPEN_SIMULATOR:
                    conn_dict[json_data['host']].send(data)
                elif json_data['command_id'] == REPORT_RES_RATE:
                    conn_dict[json_data['host']].send(data)

            except Exception as ex:
                print (ex)
    except Exception as ex:
        conn_list.remove(conn)
        print(ex)
    finally:
        conn.close()

if __name__ == '__main__':
    # server(5566)
    main()