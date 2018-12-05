#-*-coding:utf-8-*-

import json
import time
from protocol import *
import gevent
from collections import OrderedDict
from gevent import socket,monkey
import threading

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
            msg = json.loads(data)

            if msg['command_id'] == OPEN_SIMULATOR:
                get_conn(msg['ip']).send(data)
    except:
        isNormar = False

def get_conn(ip):
    for client in controlclient_list:
        if client.ip == ip:
            return client.skt
    raise Exception("%s not connected"%ip)

def main():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0',5566))
    s.listen(500)
    print('Server', socket.gethostbyname('0.0.0.0'), 'listening ...')
    while True:
        cli,(ip,cport) = s.accept()
        print("(%s,%s connected...)" % (ip, cport))
        client = ControlClient(cli,ip)
        controlclient_list.append(client)
        t=threading.Thread(target=hand_client_con,arg=(client,))
        t.start()
    s.close()



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