#-*-coding:utf-8-*-

import json
import time
from protocol import *
import gevent
from collections import OrderedDict
from gevent import socket,monkey

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
                if json_data['command_id'] == OPEN_SIMULATOR or json_data['command_id'] == OPEN_REALCLIENT:
                    conn_dict[json_data['host']].send(data)
            except Exception as ex:
                print (ex)
    except Exception as ex:
        conn_list.remove(conn)
        print(ex)
    finally:
        conn.close()

if __name__ == '__main__':
    server(5566)