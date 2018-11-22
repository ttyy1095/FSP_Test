#!/usr/bin/env python
# -*- coding:utf-8 -*-
#Author: Jax

import os, time,json,re
import paramiko
# import zookeeper
# zk = zookeeper.init("192.168.7.111:2181,192.168.7.113:2181,192.168.7.114:2181")
# print zookeeper.get_children(zk,"/fsp",None)
# print json.loads(zookeeper.get(zk,"/fsp/ss/ss2")[0])['ip']

connects = {}


def get_ssh(host):
    if not connects.has_key(host):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host,port=22,username="root",password="123456")
        connects[host] = ssh

    return connects[host]

def destroy():
    for i in connects.values():
        i.close()
def move_crashfile():
    pass




def execCommand(host,cmd):
    ssh = get_ssh(host)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read()
    if not result:
        result = stderr.read()
    return result

def _get_cpu_info(host):
    str_out = execCommand(host,'cat /proc/stat | grep "cpu "')


    cpu_time_list = re.findall('\d+', str_out)
    cpu_idle = cpu_time_list[3]
    total_cpu_time = 0
    for t in cpu_time_list:
        total_cpu_time = total_cpu_time + int(t)
    return cpu_idle,total_cpu_time

def _calc_cpu_rate(host):
    cpu_idle1,total_cpu_time1 = _get_cpu_info(host)

    time.sleep(1)
    cpu_idle2, total_cpu_time2 = _get_cpu_info(host)

    cpu_usage = round(1 - (float(cpu_idle2) - float(cpu_idle1)) / (total_cpu_time2 - total_cpu_time1), 6)
    return cpu_usage
def _calc_mem_rate(host):
    str_out = execCommand(host,"cat /proc/meminfo")

    mem_total = re.findall(r'MemTotal:\s+(\d+)',str_out)[0]
    mem_avail = re.findall(r'MemAvailable:\s+(\d+)',str_out)[0]
    return round(1-float(mem_avail)/float(mem_total),6)

def _get_dev(host):
    str_out = execCommand(host,"ls /etc/sysconfig/network-scripts/|grep ifcfg-|grep -v ifcfg-lo")
    dev = ""
    for i in str_out.split('\n'):
        if i.strip() == "":
            break
        ipaddr = execCommand(host,"cat /etc/sysconfig/network-scripts/%s|grep IPADDR|cut -d '=' -f 2"%i).strip()
        if ipaddr == host:
            dev = i[6:]
    if dev == "":
        raise Exception('can not get net dev by ip')
    return dev
def _get_tran_bytes(host,dev):
    str_out = execCommand(host,"cat /proc/net/dev|grep %s|awk '{print $10}'"%dev)
    return str_out.strip()

def get_sever_res_rate(host):
    # 默认带宽大小，在GS/SS配置文件中手动配置，这里自动化部署未对该值做修改
    total_bandwidth = 1024
    mem_usage = _calc_mem_rate(host)
    dev = _get_dev(host)
    tran_bytes1 = _get_tran_bytes(host,dev)
    cpu_idle1,total_cpu_time1 = _get_cpu_info(host)
    time.sleep(1)
    tran_bytes2 = _get_tran_bytes(host, dev)
    cpu_idle2, total_cpu_time2 = _get_cpu_info(host)

    cpu_usage = round(1 - (float(cpu_idle2) - float(cpu_idle1)) / (total_cpu_time2 - total_cpu_time1), 6)

    band_usage = round((float(tran_bytes2)-float(tran_bytes1))*8/(total_bandwidth*1024*1024),6)
    upload_speed = total_bandwidth*1024*band_usage

    return cpu_usage,mem_usage,band_usage,upload_speed



def get_process_res_rate(host,service_type):
    """

    :param host:
    :param processName:
    :return:cpu逻辑核心数量，总内存大小，cpu占用率，内存占用率，占用虚拟内存大小，占用实际内存大小
    """
    service_process_dict = {"ice":"ice_server","ms":"moniter_server","ma":"moniter_agent",
                            "gc":"group_controller","sc":"stream_controller","rule":"rule_server",
                            "gs":"group_server","ss":"stream_server"}
    cpu_count = execCommand(host,"cat /proc/cpuinfo| grep 'processor'| wc -l")

    mem_total = execCommand(host, "grep MemTotal /proc/meminfo |awk '{print $2}'")
    command = "ps -aux|grep -v grep|grep %s|awk '{print $3,$4,$5,$6}'" % (service_process_dict[service_type])
    resp = execCommand(host,command)
    cpu_rate, mem_rate, vsz_size, rss_size = resp.split(" ")

    return cpu_count.strip(),int(mem_total.strip())/1024,cpu_rate,mem_rate,int(vsz_size)/1024,int(rss_size.strip())/1024

def check_crash(host,service_type):
    """
    检测服务目录下是否存在崩溃文件
    注意：
        1.在测试开始前必须执行环境清理工作，防止之前已存在的崩溃文件对结果
    :param host:
    :param service_type:
    :return:
    """
    base_path = "/fsmeeting/fsp_sss_stream/"
    if service_type == "ice":
        path = base_path+"icegrid/node1"
    else:
        path = base_path + service_type

    resp = execCommand(host,"ll %s|grep core.*|wc -l"%path).strip()
    if resp != "0":
        return True
    return False

def check_error(host,service_type):

    base_path = "/fsmeeting/fsp_sss_stream/"
    if service_type == "ice":
        path = base_path+"icegrid/node1"
    else:
        path = base_path + service_type
    tm = time.localtime(time.time())
    log_path = path+"/log/%s-%s-%s"%(tm.tm_year,tm.tm_mon,tm.tm_mday)
    print log_path
    resp = execCommand(host,"grep -I ERROR %s/*"%log_path)
    print resp


if __name__ == '__main__':

    print get_sever_res_rate("192.168.7.105")