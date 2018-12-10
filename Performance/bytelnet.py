#-*-coding:utf-8-*-
import telnetlib

import logging,time
# logging.basicConfig(level=logging.DEBUG)
# tn = telnetlib.Telnet('192.168.8.203',port=23,timeout=10)
#
# tn.set_debuglevel(2)
#
# tn.read_until(b'login: ', timeout=10)
# tn.write('ttyy'+ '\r\n')
# # 等待Password出现后输入用户名，最多等待10秒
#
# tn.read_until(b'password:', timeout=10)
# tn.write('hj123456'+ '\r\n')
# time.sleep(2)
# command_result = tn.read_very_eager().decode('ascii')
# print command_result
#
# tn.write('dir'+'\r\n')
# time.sleep(2)
# command_result = tn.read_very_eager().decode('GBK')
# print command_result
ll = ["1",'2','3']
print('%s'%ll)
i = 10
print str(i).zfill(2) if i<10 else str(i)

# import pika
# credentials = pika.PlainCredentials('root','root')
# conn = pika.BlockingConnection(pika.ConnectionParameters('192.168.7.111',5672,'fsp',credentials))
# channel = conn.channel()
# channel.queue_declare(queue='testqueue')
# channel.basic_publish(exchange='',
#                       routing_key='testqueue',
#                       body='Hello World!')
# conn.close()

room_list='107894'
print(room_list.split(','))