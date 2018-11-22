import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.7.114", 22, "root", "123456")
# stdin, stdout, stderr = ssh.exec_command("pkill  ice_server")
# print stdin
# print "############"
# print stdout.read()
# print "############"
# print stderr.read()

import time

# time.sleep(5)

stdin, stdout, stderr = ssh.exec_command("ps -ef|grep ice_server|grep -v grep|wc -l")
print stdin
print "############"
print int(stdout.read().strip())
print "############"
print stderr.read()