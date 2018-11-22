#!/usr/bin/env python
# -*- coding:utf-8 -*-
#Author: Jax

import os, time,json,re
import paramiko
# import zookeeper
# zk = zookeeper.init("192.168.7.111:2181,192.168.7.113:2181,192.168.7.114:2181")
# print zookeeper.get_children(zk,"/fsp",None)
# print json.loads(zookeeper.get(zk,"/fsp/ss/ss2")[0])['ip']

listen_hosts = (
                ('192.168.7.105','ice'),
                ('192.168.7.73','ms'),
                ('192.168.7.108','ms'),
                ('192.168.7.72','ma'),
                ('192.168.7.105','ma'),
                ('192.168.7.106','ma'),
                ('192.168.7.104','ma'),
                ('192.168.7.153','ma'),
                ('192.168.7.144','ma'),
                ('192.168.7.72','gs'),
                ('192.168.7.105','gs'),
                ('192.168.7.106','gs'),
                ('192.168.7.104','ss'),
                ('192.168.7.153','ss'),
                ('192.168.7.144','ss'),
                ('192.168.7.73','gc'),
                ('192.168.7.108','gc'),
                ('192.168.7.63','gc'),
                ('192.168.7.63','sc'),
                ('192.168.7.64','sc'),
                ('192.168.7.65','sc'),
                ('192.168.7.71','rule')
                )
class ServiceListener(object):
    connects = {}
    def __init__(self):

        pass

    def get_ssh(self,host):
        if not self.connects.has_key(host):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host,port=22,username="root",password="123456")
            self.connects[host] = ssh

        return self.connects[host]

    def destroy(self):
        for i in self.connects.values():
            i.close()
    def move_crashfile(self):
        pass




    def execCommand(self,host,cmd):
        ssh = self.get_ssh(host)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read()
        if not result:
            result = stderr.read()
        return result

    def _get_cpu_info(self,host):
        str_out = self.execCommand(host,'cat /proc/stat | grep "cpu "')


        cpu_time_list = re.findall('\d+', str_out)
        cpu_idle = cpu_time_list[3]
        total_cpu_time = 0
        for t in cpu_time_list:
            total_cpu_time = total_cpu_time + int(t)
        return cpu_idle,total_cpu_time

    def _calc_cpu_rate(self,host):
        cpu_idle1,total_cpu_time1 = self._get_cpu_info(host)

        time.sleep(1)
        cpu_idle2, total_cpu_time2 = self._get_cpu_info(host)

        cpu_usage = round(1 - (float(cpu_idle2) - float(cpu_idle1)) / (total_cpu_time2 - total_cpu_time1), 6)
        return cpu_usage
    def _calc_mem_rate(self,host):
        str_out = self.execCommand(host,"cat /proc/meminfo")

        mem_total = re.findall(r'MemTotal:\s+(\d+)',str_out)[0]
        mem_avail = re.findall(r'MemAvailable:\s+(\d+)',str_out)[0]
        return round(1-float(mem_avail)/float(mem_total),6)

    def _get_dev(self,host):
        str_out = self.execCommand(host,"ls /etc/sysconfig/network-scripts/|grep ifcfg-|grep -v ifcfg-lo")
        dev = ""
        for i in str_out.split('\n'):
            if i.strip() == "":
                break
            ipaddr = self.execCommand(host,"cat /etc/sysconfig/network-scripts/%s|grep IPADDR|cut -d '=' -f 2"%i).strip()
            if ipaddr == host:
                dev = i[6:]
        if dev == "":
            raise Exception('can not get net dev by ip')
        return dev
    def _get_tran_bytes(self,host,dev):
        str_out = self.execCommand(host,"cat /proc/net/dev|grep %s|awk '{print $10}'"%dev)
        return str_out.strip()

    def get_sever_res_rate(self,host):



        mem_usage = self._calc_mem_rate(host)
        dev = self._get_dev(host)
        tran_bytes1 = self._get_tran_bytes(host,dev)
        cpu_idle1,total_cpu_time1 = self._get_cpu_info(host)
        time.sleep(1)
        tran_bytes2 = self._get_tran_bytes(host, dev)
        cpu_idle2, total_cpu_time2 = self._get_cpu_info(host)

        cpu_usage = round(1 - (float(cpu_idle2) - float(cpu_idle1)) / (total_cpu_time2 - total_cpu_time1), 6)

        band_usage = round((float(tran_bytes2)-float(tran_bytes1))/(1024*1024*1024),6)

        return cpu_usage,mem_usage,band_usage


    def get_process_res_rate(self,host,service_type):
        """

        :param host:
        :param processName:
        :return:cpu逻辑核心数量，总内存大小，cpu占用率，内存占用率，占用虚拟内存大小，占用实际内存大小
        """
        service_process_dict = {"ice":"ice_server","ms":"moniter_server","ma":"moniter_agent",
                                "gc":"group_controller","sc":"stream_controller","rule":"rule_server",
                                "gs":"group_server","ss":"stream_server"}
        cpu_count = self.execCommand(host,"cat /proc/cpuinfo| grep 'processor'| wc -l")

        mem_total = self.execCommand(host, "grep MemTotal /proc/meminfo |awk '{print $2}'")
        command = "ps -aux|grep -v grep|grep %s|awk '{print $3,$4,$5,$6}'" % (service_process_dict[service_type])
        resp = self.execCommand(host,command)
        cpu_rate, mem_rate, vsz_size, rss_size = resp.split(" ")

        return cpu_count.strip(),int(mem_total.strip())/1024,cpu_rate,mem_rate,int(vsz_size)/1024,int(rss_size.strip())/1024

    def check_crash(self,host,service_type):
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

        resp = self.execCommand(host,"ll %s|grep core.*|wc -l"%path).strip()
        if resp != "0":
            return True
        return False

    def check_error(self,host,service_type):

        base_path = "/fsmeeting/fsp_sss_stream/"
        if service_type == "ice":
            path = base_path+"icegrid/node1"
        else:
            path = base_path + service_type
        tm = time.localtime(time.time())
        log_path = path+"/log/%s-%s-%s"%(tm.tm_year,tm.tm_mon,tm.tm_mday)
        print log_path
        resp = self.execCommand(host,"grep -I ERROR %s/*"%log_path)
        print resp

if __name__ == '__main__':
    a = ServiceListener()
    print a.get_sever_res_rate("192.168.7.105")