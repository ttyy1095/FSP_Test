#coding=gbk

import paramiko
import re
import time
import sys
 
#���������б�
host_list=({'ip':'192.168.7.144', 'port':22, 'username':'root', 'password':'123456'},
           {'ip':'192.168.7.153', 'port':22, 'username':'root', 'password':'123456'},)
 
ssh = paramiko.SSHClient()
# ����Ϊ���ܲ���known_hosts �б���������Խ���ssh����
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 
for host in host_list:
    ssh.connect(hostname=host['ip'], port=host['port'], username=host['username'], password=host['password'])
    print(host['ip'])
    stdin, stdout, stderr = ssh.exec_command('cat /proc/stat | grep "cpu "')
    str_out = stdout.read().decode()
    str_err = stderr.read().decode()
 
    if str_err != "":
        print(str_err)
        continue
    else:
        cpu_time_list = re.findall('\d+', str_out)
        cpu_idle1 = cpu_time_list[3]
        total_cpu_time1 = 0
        for t in cpu_time_list:
            total_cpu_time1 = total_cpu_time1 + int(t)
 
    time.sleep(2)
 
    stdin, stdout, stderr = ssh.exec_command('cat /proc/stat | grep "cpu "')
    str_out = stdout.read().decode()
    str_err = stderr.read().decode()
    if str_err != "":
        print(str_err)
        continue
    else:
        cpu_time_list = re.findall('\d+', str_out)
        cpu_idle2 = cpu_time_list[3]
        total_cpu_time2 = 0
        for t in cpu_time_list:
            total_cpu_time2 = total_cpu_time2 + int(t)
 
    cpu_usage = round(1 - (float(cpu_idle2) - float(cpu_idle1)) / (total_cpu_time2 - total_cpu_time1), 6)
    print('��ǰCPUʹ����Ϊ��' + str(cpu_usage))
 
    
    ssh.close()
time.sleep(30)
    