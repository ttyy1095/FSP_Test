#-*-coding:utf-8-*-
import paramiko

ip_list = ["63","64","65","71","72","73","104","105","106","108","144","153","160"]

for i in  ip_list:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host_name = "192.168.7.%s"%i
    ssh.connect(hostname=host_name,port=22,username="root",password="123456")
    stdin, stdout, stderr = ssh.exec_command( "cat /proc/cpuinfo| grep 'processor'| wc -l")
    cpu_count = stdout.read().strip()
    stdin, stdout, stderr = ssh.exec_command( "grep MemTotal /proc/meminfo |awk '{print $2}'")
    mem_total = stdout.read().strip()
    print "%s cpu:%s MEM: %s "%(host_name,cpu_count,mem_total)

from kafka import SimpleClient

client = SimpleClient(hosts="192.168.7.111:9092")
topic = client.topics['rule_group_01']
