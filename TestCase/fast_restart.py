#-*-coding:utf-8-*-
import paramiko
import sys


connects = {}
def get_ssh(host):
    if not connects.has_key(host):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host,port=22,username="root",password="123456")
        connects[host] = ssh

    return connects[host]

def execCommand(host,cmd):
    ssh = get_ssh(host)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read()
    if not result:
        result = stderr.read()
    print host
    print result

def closeAllSSH():
    for i in connects.values():
        i.close()

def stop():
    execCommand("192.168.7.59", "sh /fsmeeting/fsp_sss_stream/gs/GSMonitorCtrl.sh stop")
    execCommand("192.168.7.103", "sh /fsmeeting/fsp_sss_stream/gs/GSMonitorCtrl.sh stop")
    execCommand("192.168.7.174", "sh /fsmeeting/fsp_sss_stream/ss/SSMonitorCtrl.sh stop")
    execCommand("192.168.7.85", "sh /fsmeeting/fsp_sss_stream/sc/SCMonitorCtrl.sh stop")
    execCommand("192.168.7.85", "sh /fsmeeting/fsp_sss_stream/gc/GCMonitorCtrl.sh stop")
    execCommand("192.168.7.85", "sh /fsmeeting/fsp_sss_stream/rule/RULEMonitorCtrl.sh stop")
def start():
    execCommand("192.168.7.59", "rm -rf /fsmeeting/fsp_sss_stream/gs/log && sh /fsmeeting/fsp_sss_stream/gs/GSMonitorCtrl.sh start")
    execCommand("192.168.7.103", "rm -rf /fsmeeting/fsp_sss_stream/gs/log && sh /fsmeeting/fsp_sss_stream/gs/GSMonitorCtrl.sh start")
    execCommand("192.168.7.174", "rm -rf /fsmeeting/fsp_sss_stream/ss/log && sh /fsmeeting/fsp_sss_stream/ss/SSMonitorCtrl.sh start")
    execCommand("192.168.7.85", "rm -rf /fsmeeting/fsp_sss_stream/sc/log && sh /fsmeeting/fsp_sss_stream/sc/SCMonitorCtrl.sh start")
    execCommand("192.168.7.85", "rm -rf /fsmeeting/fsp_sss_stream/gc/log && sh /fsmeeting/fsp_sss_stream/gc/GCMonitorCtrl.sh start")
    execCommand("192.168.7.85", "rm -rf /fsmeeting/fsp_sss_stream/rule/log && sh /fsmeeting/fsp_sss_stream/rule/RULEMonitorCtrl.sh start")

def status():
    execCommand("192.168.7.59", "sh /fsmeeting/fsp_sss_stream/gs/GSMonitorCtrl.sh status")
    execCommand("192.168.7.103", "sh /fsmeeting/fsp_sss_stream/gs/GSMonitorCtrl.sh status")
    execCommand("192.168.7.174", "sh /fsmeeting/fsp_sss_stream/ss/SSMonitorCtrl.sh status")
    execCommand("192.168.7.85", "sh /fsmeeting/fsp_sss_stream/sc/SCMonitorCtrl.sh status")
    execCommand("192.168.7.85", "sh /fsmeeting/fsp_sss_stream/gc/GCMonitorCtrl.sh status")
    execCommand("192.168.7.85", "sh /fsmeeting/fsp_sss_stream/rule/RULEMonitorCtrl.sh status")

if __name__ == '__main__':

    if sys.argv[1] == "stop":
        stop()
    elif sys.argv[1] == "start":
        start()
    elif sys.argv[1] == "restart":
        stop()
        start()
    elif sys.argv[1] == "status":
        status()
    else:
        print "Unknown command: %s" % sys.argv[1]

    closeAllSSH()


