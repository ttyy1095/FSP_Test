#-*-coding:utf-8-*-

import collections
import json
import logging
import os
import re
import sys
sys.path.append('..')

import tarfile
import time

import allure
import jenkins
import paramiko
import pytest
import redis
import requests
from kazoo.client import KazooClient

from ClientControler.clientcontroler import *
from Config import config
from Public import base
from Public.my_zentao import zentao
from Public.resource_view import *

logging.basicConfig(level=logging.INFO)

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
# log_path = os.path.dirname(os.getcwd()) + '/Logs/'
# logfile = "%s%s.log" % (log_path, rq)
# fh = logging.FileHandler(logfile, mode='w')
# fh.setLevel(logging.DEBUG)
# formatter = logging.Formatter(
#     "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
# fh.setFormatter(formatter)
# logger.addHandler(fh)

zk = KazooClient(hosts=config.zookeeperAddr)

def get_all_server_ip(service_type):
    server_list = []
    for instance_id in zk.get_children('/fsp/%s'%service_type):
        ip = json.loads(zk.get('/fsp/%s/%s'%(service_type,instance_id))[0])['ip']
        server_list.append(ip)
    return server_list

def changeRuleConf_step(fileName):
    testdata_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'TestData')
    filepath = os.path.join(testdata_path, fileName)
    for rule_ip in config.RULE_SERVERS:

        transport = paramiko.Transport(rule_ip)
        transport.connect(username="root", password="123456")
        sftp_client = paramiko.SFTPClient.from_transport(transport)
        sftp_client.put(filepath, "/fsmeeting/fsp_sss_stream/rule/rule-config.xml")
        sftp_client.close()
    time.sleep(5)

def get_ssh_connect( host):
    connects = {}
    if not connects.has_key(host):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=22, username="root", password="123456")
        connects[host] = ssh
    return connects[host]

def ssh_exec_command(host,command):
    logger = logging.getLogger('ssh')
    ssh = get_ssh_connect(host)
    stdin,stdout,stderr = ssh.exec_command(command,timeout=600)
    # 必须要清除buffer，否则会立即往下执行
    err = stderr.read()

    if err:
        logger.error('ssh exec command error(host:%s,command:%s,err:%s' % (host, command, err))
        raise Exception('ssh exec command error')
    else:
        result = stdout.read()
    return result

@allure.feature("必测用例")
class Test_CheckList(object):



    def setup_class(self):
        zk.start()
        changeRuleConf_step('rule-config_default.xml')

    def treadown_class(self):
        zk.close()

    def check_video(self):
        _,_,result = check_oc_av()
        return result

    def check_video_nc2nc(self):
        """
        NC广播视频，NC接收视频
        :return:
        """
        return True

    # @pytest.mark.parametrize()

    @allure.story("Platform-fsp_sss-1690:服务器版本检查")

    def test_checkVersion(self):
        """
        对禅道及jenkins构建
        """
        pytest.mark.skip()
        print os.path.realpath(__file__)
        version = "2.8.2.13"
        zt = zentao(config.zentao_url, config.zentao_user, config.zentao_password,
                    config.zentao_product, config.zentao_project)
        filePath = zt.get_build_info(version)
        assert filePath != ""
        if filePath[-1] == "/":
            build_number = int(re.findall(r"/(\d+)/", filePath)[0])
        else:
            build_number = int(re.findall(r"/(\d+)$", filePath)[0])

        jenkinsObj = jenkins.Jenkins(
            config.jenkins_url,
            username=config.jenkins_user,
            password=config.jenkins_password)

        job_build_info = jenkinsObj.get_build_info("build_platform_fsp_stream",
                                                   build_number)
        file_version = ""
        for x in job_build_info["actions"]:
            if x.has_key("_class"):
                if x["_class"] == "hudson.model.ParametersAction":
                    for y in x["parameters"]:
                        if y["name"] == "curversion":
                            file_version = y["value"]

        assert file_version != ""

        file_url = "%sartifact/fsp-sss-stream-%s.tar.gz" % (filePath, file_version)
        r = requests.get(file_url, stream=True)
        gz_file = "fsp-sss-stream-%s.tar.gz" % file_version
        with open(gz_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        t = tarfile.open(gz_file)
        t.extractall(path=".")
        services = [
            "gc", "gs", "icegrid", "km", "ma", "ms", "new_ss", "rule", "sc", "ss",
            "vnc_gs"
        ]
        for service in services:
            version_file = "fsp-sss-stream-%s/cpp/%s/VERSION" % (file_version, service)
            with open(version_file, "r") as f:
                all_info = f.readlines()
                version_info = all_info[1].split(":")[1].strip()
                assert version_info == file_version
        assert file_version in version

    @allure.story("Platform-fsp_sss-1691:服务器重启后能够正常运行和处理业务")
    @pytest.mark.skip(reason='take long time')
    def test_restartAllServices(self):
        logger = logging.getLogger('Platform-fsp_sss-1691')
        ssh_exec_command(config.AUTO_TEST_SERVER,"cd /etc/ansible/jenkins_deploy/autotest && ansible-playbook -i inventories/hosts restart_all.yml")
        result = self.check_video()
        assert result

    @allure.story("Platform-fsp_sss-1692:服务崩溃后守护进程能够自动拉起")
    def test_service_crash(self):
        logger = logging.getLogger('Platform-fsp_sss-1692')
        logger.info("Platform-fsp_sss-1692:服务崩溃后守护进程能够自动拉起")

        service_dict = {'gc':'group_controller','sc':'stream_controller','rule':'rule_server','ms':'moniter_server',
                        'ma':'moniter_agent','gs':'group_server','ss':'stream_server'}
        for service_type in service_dict.keys():
            process_name = service_dict[service_type]
            ips = get_all_server_ip(service_type)
            if len(ips) < 1:
                logger.error('%s must have more than 1 isntance'%service_type)

            ssh_exec_command(ips[0]," ps -ef|grep %s|grep -v grep|awk '{print $2}'|xargs kill" % process_name)
            time.sleep(5)
            count = ssh_exec_command(ips[0],"ps -ef|grep %s|grep -v grep|wc -l" % process_name)

            assert int(count) == 1


    @pytest.fixture(scope='function')
    def keep_all_gc_running(self):
        ssh_exec_command(config.AUTO_TEST_SERVER,"cd /etc/ansible/jenkins_deploy/autotest && ansible-playbook -i inventories/hosts start_gc.yml")
        print '初始化gc'
        yield
        ssh_exec_command(config.AUTO_TEST_SERVER,"cd /etc/ansible/jenkins_deploy/autotest && ansible-playbook -i inventories/hosts start_gc.yml")
        print '恢复gc'

    @allure.story("Platform-fsp_sss-1693:三台gc有一台处理业务时崩溃不重启，对其他服务无影响")
    def test_gc_group(self,keep_all_gc_running):
        """
        首先关掉一个gc，测试音视频是否正常
        恢复该gc，关闭其他gc，测试音视频是否正常
        """
        logger = logging.getLogger('Platform-fsp_sss-1693')
        logger.info('Platform-fsp_sss-1693')
        ips = get_all_server_ip('gc')

        if len(ips) < 2:
            logger.error("must have more than 2 gc")
            raise Exception("must have more than 2 gc")

        ssh_exec_command(ips[0],"cd /fsmeeting/fsp_sss_stream/gc && ./GCMonitorCtrl.sh stop")
        time.sleep(2)
        check_video_result = self.check_video()
        assert check_video_result == True
        ssh_exec_command(ips[0],"cd /fsmeeting/fsp_sss_stream/gc && ./GCMonitorCtrl.sh start ")
        ssh_exec_command(ips[1], "cd /fsmeeting/fsp_sss_stream/gc && ./GCMonitorCtrl.sh stop")
        time.sleep(2)
        check_video_result = self.check_video()
        assert check_video_result == True

    @pytest.fixture(scope='function')
    def keep_all_sc_running(self):
        ssh_exec_command(config.AUTO_TEST_SERVER,"cd /etc/ansible/jenkins_deploy/autotest && ansible-playbook -i inventories/hosts start_sc.yml")
        yield
        ssh_exec_command(config.AUTO_TEST_SERVER,"cd /etc/ansible/jenkins_deploy/autotest && ansible-playbook -i inventories/hosts start_sc.yml")

    @allure.story("Platform-fsp_sss-1694:三台sc有一台处理业务时崩溃不重启，对其他服务无影响")
    def test_sc_group(self,keep_all_sc_running):
        """

        """
        logger = logging.getLogger('Platform-fsp_sss-1694')
        ips = get_all_server_ip('sc')
        if len(ips) < 2:
            logger.error("must have more than 2 sc")
            raise Exception("must have more than 2 sc")

        ssh_exec_command(ips[0],"cd /fsmeeting/fsp_sss_stream/sc && ./SCMonitorCtrl.sh stop")
        time.sleep(5)
        check_video_result = self.check_video()
        assert check_video_result == True
        ssh_exec_command(ips[0], "cd /fsmeeting/fsp_sss_stream/sc && ./SCMonitorCtrl.sh start")
        ssh_exec_command(ips[1], "cd /fsmeeting/fsp_sss_stream/sc && ./SCMonitorCtrl.sh stop")
        time.sleep(5)
        check_video_result = self.check_video()
        assert check_video_result == True

    @pytest.fixture(scope='function')
    def keep_all_rule_running(self):
        ssh_exec_command(config.AUTO_TEST_SERVER,
                              "cd /etc/ansible/jenkins_deploy/autotest && ansible-playbook -i inventories/hosts start_rule.yml")
        yield
        ssh_exec_command(config.AUTO_TEST_SERVER,
                              "cd /etc/ansible/jenkins_deploy/autotest && ansible-playbook -i inventories/hosts start_rule.yml")


    @allure.story("Platform-fsp_sss-1695:两台rule有一台处理业务时崩溃不重启，对其他服务无影响")
    def test_rule_group(self,keep_all_rule_running):
        """
        必须部署2个rule，2个rule均采用可用的配置文件（保证oc，nc均能正常广播音视频）
        为保证每次环境一致，不因存在2个rule导致接入优化结果不一致，除了本用例外，其他用例均只会启动rule1
        """
        logger = logging.getLogger('Platform-fsp_sss-1695')
        ips = get_all_server_ip('rule')
        if len(ips) < 2:
            logger.error("must have more than 2 rule")
            assert len(ips) >= 2

        ssh_exec_command(ips[1],"cd /fsmeeting/fsp_sss_stream/rule && ./RULEMonitorCtrl.sh stop")
        time.sleep(10)
        check_video_result = self.check_video()
        assert check_video_result == True
        ssh_exec_command(ips[1],"cd /fsmeeting/fsp_sss_stream/rule && ./RULEMonitorCtrl.sh start")
        ssh_exec_command(ips[0],"cd /fsmeeting/fsp_sss_stream/rule && ./RULEMonitorCtrl.sh stop")
        time.sleep(10)
        check_video_result = self.check_video()
        assert check_video_result == True

    @pytest.fixture(scope='function')
    def keep_all_ice_running(self):
        ssh_exec_command(config.AUTO_TEST_SERVER,"cd /etc/ansible/jenkins_deploy/autotest && ansible-playbook -i inventories/hosts start_ice.yml")
        yield
        ssh_exec_command(config.AUTO_TEST_SERVER,"cd /etc/ansible/jenkins_deploy/autotest && ansible-playbook -i inventories/hosts start_ice.yml")


    @allure.story("Platform-fsp_sss-1696:node1的ice_server崩溃不重启，node2的ice_server接替业务处理")

    def test_ice_group(self,keep_all_ice_running):
        """

        :return:
        """
        logger = logging.getLogger('Platform-fsp_sss-1696')
        ids = config.services["icegrid"]["servers"].keys()
        if len(ids) != 2:
            logger.error("must have 2 ice node")
            raise Exception("must have 2 ice node")
        ice1_host = config.services["icegrid"]["servers"][ids[0]]

        ssh_exec_command(ice1_host,"pkill icegridnode")
        time.sleep(5)
        check_video_result = self.check_video()
        assert check_video_result == True
        # 重新启动node1
        ssh_exec_command(ice1_host,"cd /fsmeeting/fsp_sss_stream/icegrid/%s && icegridnode --Ice.Config=config.server --Ice.IPv6=0 --daemon --nochdir"
            % ids[0])
        #关闭node2
        other_ice = config.services["icegrid"]["servers"][ids[1]]

        ssh_exec_command(other_ice,"pkill icegridnode")
        time.sleep(5)
        check_video_result = self.check_video()
        assert check_video_result == True

    @pytest.fixture(scope='function')
    def keep_all_ms_running(self):
        ssh_exec_command(config.AUTO_TEST_SERVER,"cd /etc/ansible/jenkins_deploy/autotest && ansible-playbook -i inventories/hosts start_ms.yml")
        time.sleep(5)
        yield
        ssh_exec_command(config.AUTO_TEST_SERVER,"cd /etc/ansible/jenkins_deploy/autotest && ansible-playbook -i inventories/hosts start_ms.yml")
        time.sleep(5)
    @allure.story("Platform-fsp_sss-1697:主ms崩溃不重启，对其他服务无影响，从ms接替业务处理")
    def test_ms_group(self,keep_all_ms_running):
        """
        主MS挂掉时，辅助MS接替处理，向ma
        :return:
        """
        # 通过zookeeper获取主备ms
        logger = logging.getLogger('Platform-fsp_sss-1697')

        main = zk.get_children("/fsp/ms")[0]
        standby = zk.get_children("/fsp/ms_replca")[0]

        main_ms_host = json.loads(zk.get('/fsp/ms/%s'%main)[0])['ip']
        standby_ms_host = json.loads(zk.get('/fsp/ms_replca/%s' % standby)[0])['ip']

        ssh_exec_command(main_ms_host,"pkill MSMonitor.sh && pkill moniter_server")


        rq = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        # 获取当天最后一个moniter_server日志中含有“Invoke TimeTask”的行数
        task_count1 = ssh_exec_command(standby_ms_host,"grep -c 'Invoke TimeTask' `ls -l /fsmeeting/fsp_sss_stream/ms/log/%s/moniter_server_*|sed -n '$p'|awk '{print $NF}'`"
            % rq)
        if not task_count1:
            logger.error("get task_count from mslog error")
            assert 1 != 1
        time.sleep(60)

        # 再次获取，这里需要注意的是为了方便测试，ms下发任务的时间由60s改为30s
        task_count2 = ssh_exec_command(standby_ms_host,
                                            "grep -c 'Invoke TimeTask' `ls -l /fsmeeting/fsp_sss_stream/ms/log/%s/moniter_server_*|sed -n '$p'|awk '{print $NF}'`"
                                            % rq)
        assert task_count1 != task_count2



    @allure.story("Platform-fsp_sss-1698:gs崩溃后重启，NC能够重连原来的gs，OC需重新登录")
    def test_gs_crash(self):
        logger = logging.getLogger('Platform-fsp_sss-1698')
        with allure.step(""):
            pass

    @allure.story("Platform-fsp_sss-1699:边缘ss崩溃不重启，NC能重连新的边缘ss节点")
    def test_marginss_crash(self):
        pass

    @allure.story("Platform-fsp_sss-1700:中转ss崩溃不重启，NC会连接新上级ss，OC会重连其他topo值最小的中转ss")
    def test_kernelss_crash(self):
        pass

    @allure.story("Platform-fsp_sss-1701:MS给MA下发任务，所有的MA都收到并且执行了任务")
    def test_all_ma_received(self):

        main = zk.get_children("/fsp/ms")[0]
        main_ms_host = json.loads(zk.get('/fsp/ms/%s' % main)[0])['ip']



        rq = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        # 获取当天最后一个moniter_server日志中含有“Invoke TimeTask”的行数

        task_str = ssh_exec_command(main_ms_host,"grep  'Invoke TimeTask' `ls -l /fsmeeting/fsp_sss_stream/ms/log/%s/moniter_server_*|sed -n '$p'|awk '{print $NF}'`"
            % rq)
        tasks = re.findall(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d{9}\]', task_str)

        isPass = True
        for i in range(0, len(tasks) - 1):
            time1 = time.mktime(time.strptime(tasks[i], "%Y-%m-%d %H:%M:%S"))
            time2 = time.mktime(time.strptime(tasks[i + 1], "%Y-%m-%d %H:%M:%S"))
            if (time2 - time1) != 30:
                isPass = False
                break
        assert isPass == True

        task_str = ssh_exec_command(main_ms_host,"cat `ls -l /fsmeeting/fsp_sss_stream/ms/log/%s/moniter_server_*|sed -n '$p'|awk '{print $NF}'` |tail -n 200"
            % rq)

        ma_list = re.findall(r"recv kafka msg\(from: (.+)\)", task_str)
        ma_list = list(set(ma_list))
        ma_in_zk = zk.get_children('/fsp/ma')

        assert len(ma_list) == len(ma_in_zk) - 1

    @allure.story("Platform-fsp_sss-1702:ma上报的资源使用信息正确")
    def test_ma_report_resource(self):

        ma_all = zk.get_children("/fsp/ma")

        ice_master_ip = config.services['icegrid']['servers']['node1']
        rq = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        stdout_str = ssh_exec_command(ice_master_ip,"cat `ls -l /fsmeeting/fsp_sss_stream/icegrid/node1/log/%s/TimedTask_*|sed -n '$p'|awk '{print $NF}'` |grep band_usage|tail -n %d"
            % (rq, len(ma_all)))
        resources_info = re.findall(
            r'ip\((\d+.\d+.\d+.\d+)\), cpu_usage\((\d.\d+)\), mem_usage\((\d.\d+)\), band_usage\((\d.\d+)\)',
            stdout_str)
        print resources_info
        for ip, cpu_usage, mem_usage, band_usage in resources_info:

            cpu_usage_real, mem_usage_real, band_usage_real, _ = get_sever_res_rate(ip)
            # 允许10%的误差
            assert abs(cpu_usage_real - float(cpu_usage)) < 0.1
            assert abs(mem_usage_real - float(mem_usage)) < 0.1
            assert abs(band_usage_real - float(band_usage)) < 0.1

    @allure.story("Platform-fsp_sss-1703 : ma上报的负载信息正确")
    def test_ma_report_load(self):
        db = redis.StrictRedis(host=config.REDIS['host'], port=config.REDIS['port'], db=0)


        gs_all = zk.get_children("/fsp/gs")
        ss_all = zk.get_children("/fsp/ss")
        media_severs = gs_all + ss_all

        for server in media_severs:
            instance_id = db.hget(server, 'instance_id')
            ip = db.hget(server, 'ip')
            print ip
            upload_speed = db.hget(server, 'upload_speed')
            user_num = db.hget(server, 'user_num')
            session_num = db.hget(server, 'session_num')
            type = db.hget(server, 'type')
            # service_path = {'3':'gs','2':'ss'}
            # 此处当GS与VNCGS合并后需要修改目录
            if type == '3' and 'vnc' in instance_id.lower():
                service_path = 'vnc_gs'
            elif type == '3' and 'vnc' not in instance_id.lower():
                service_path = 'gs'
            else:
                service_path = 'ss'
            stdout_str = execCommand(
                ip, 'cat /fsmeeting/fsp_sss_stream/%s/statisticalConcurrency.txt' %
                service_path)

            userCount = json.loads(stdout_str)['userCount']
            channelCount = json.loads(stdout_str)['channelCount']
            if type == '3':
                assert int(user_num) == userCount
            assert int(session_num) == channelCount
            _, _, _, upload_speed_calc = get_sever_res_rate(ip)

            # 因为upload_speed获取的不是同一时间，允许波动范围可以稍微给大点
            assert abs(float(upload_speed) - upload_speed_calc) < 100

    @allure.story("Platform-fsp_sss-1704:OC单个gs收发音视频，共享媒体文件，共享桌面声音")
    def test_oc_not_cascade(self):
        logger = logging.getLogger('Platform-fsp_sss-1704')
        changeRuleConf_step( 'rule-config_NotOverload.xml')
        with allure.step("验证音视频功能"):
            send_flag, recv_flag, result = check_oc_av()
            if not result:
                logger.error("TestCase: 1704 failed")
            assert result
        with allure.step("验证共享媒体文件"):
            send_flag, recv_flag, result = check_oc_sharemedia()

    @allure.story("Platform-fsp_sss-1705:NC单个ss收发音视频，共享媒体文件，共享桌面声音")
    def test_nc_not_cascade(self):
        logger = logging.getLogger('Platform-fsp_sss-1705')
        changeRuleConf_step( 'rule-config_NotOverload.xml')
        with allure.step("验证音视频功能"):
            send_flag, recv_flag, result = check_nc_av()
            if not result:
                logger.error("TestCase: 1704 failed")
            assert result

    @allure.story("Platform-fsp_sss-1706:NC&OC单个gs收发音视频，共享媒体文件，共享桌面声音")
    def test_oc_nc_not_cascade(self):
        changeRuleConf_step( 'rule-config_NotOverload.xml')
        with allure.step("验证音视频功能,NC->OC"):
            send_flag, recv_flag, result = check_nc2oc_av()
            assert result

        with allure.step("验证音视频功能,OC->NC"):
            send_flag, recv_flag, result = check_oc2nc_av()
            assert result

    @allure.story("Platform-fsp_sss-1707:OC级联gs收发音视频，共享媒体文件，共享桌面声音")
    def test_oc_cascade(self):
        changeRuleConf_step( 'rule-config_cascade.xml')
        with allure.step("验证音视频功能"):
            send_flag, recv_flag, result = check_oc_av()
            assert result

    @allure.story("Platform-fsp_sss-1708:NC级联ss收发音视频，共享媒体文件，共享桌面声音")
    def test_nc_cascade(self):
        changeRuleConf_step( 'rule-config_cascade.xml')
        with allure.step("验证音视频功能"):
            send_flag, recv_flag, result = check_nc_av()
            assert result

    @allure.story("Platform-fsp_sss-1709:NC&OC级联gs收发音视频，共享媒体文件，共享桌面声音")
    def test_ncoc_cascade(self):
        changeRuleConf_step( 'rule-config_cascade.xml')
        with allure.step("验证音视频功能:NC->OC"):
            send_flag, recv_flag, result = check_nc2oc_av()
            assert result
        with allure.step("验证音视频功能:OC->NC"):
            send_flag, recv_flag, result = check_oc2nc_av()
            assert result

    @allure.story('Platform-fsp_sss-1710:OC跨国不走专线收发音视频，共享媒体文件，共享桌面声音')
    def test_oc_transnational_not_specialline(self):

        base.use_specialline(False)
        changeRuleConf_step('rule-config_Transnational.xml')
        with allure.step('验证音视频功能'):
            send_flag, recv_flag, result = check_oc_av()
            assert result

    @allure.story('Platform-fsp_sss-1711:NC跨国不走专线收发音视频，共享媒体文件，共享桌面声音')
    def test_nc_transnational_not_specialline(self):

        base.use_specialline(False)
        changeRuleConf_step( 'rule-config_Transnational.xml')
        with allure.step('验证音视频功能'):
            send_flag, recv_flag, result = check_nc_av()
            assert result

    @allure.story('Platform-fsp_sss-1712:OC&NC跨国不走专线收发音视频，共享媒体文件，共享桌面声音')
    def test_nc_oc_transnational_not_specialline(self):

        base.use_specialline(False)
        changeRuleConf_step( 'rule-config_Transnational.xml')
        with allure.step('验证音视频功能:NC->OC'):
            send_flag, recv_flag, result = check_nc2oc_av()
            assert result
        with allure.step('验证音视频功能:OC->NC'):
            send_flag, recv_flag, result = check_oc2nc_av()
            assert result

    @allure.story('Platform-fsp_sss-1713:OC跨国走专线收发音视频，共享媒体文件，共享桌面声音')
    def test_oc_transnational_specialline(self):

        base.use_specialline(True)
        changeRuleConf_step( 'rule-config_Transnational.xml')
        with allure.step('验证音视频功能'):
            send_flag, recv_flag, result = check_oc_av()
            assert result

    @allure.story('Platform-fsp_sss-1714:NC跨国走专线收发音视频，共享媒体文件，共享桌面声音')
    def test_nc_transnational_specialline(self):

        base.use_specialline(True)
        changeRuleConf_step( 'rule-config_Transnational.xml')
        with allure.step('验证音视频功能'):
            send_flag, recv_flag, result = check_oc_av()
            assert result

    @allure.story('Platform-fsp_sss-1715:OC&NC跨国走专线收发音视频，共享媒体文件，共享桌面声音')
    def test_nc_oc_transnational_specialline(self):

        base.use_specialline(True)
        changeRuleConf_step( 'rule-config_Transnational.xml')
        with allure.step('验证音视频功能:NC->OC'):
            send_flag, recv_flag, result = check_nc2oc_av()
            assert result
        with allure.step('验证音视频功能:OC->NC'):
            send_flag, recv_flag, result = check_oc2nc_av()
            assert result

    @allure.story('Platform-fsp_sss-1716:paas用户单个ss收发音视频')
    @pytest.mark.skip(reason="no way of currently testing this")
    def test_paas_single_ss(self):
        pass

    @allure.story('Platform-fsp_sss-1717:paas用户级联ss收发音视频')
    @pytest.mark.skip(reason="no way of currently testing this")
    def test_paas_cascade_ss(self):
        pass

    @allure.story('Platform-fsp_sss-1718:新入会用户接收耗时测试')
    def test_sharescreen_time(self):
        """
        计算接收端开始加载解码器到解码接收到屏幕共享数据总耗时
        即接收端创建vncmp日志到VideoDecoder:VIDEO_Decode_StartDecompress success耗时
        """
        logger = logging.getLogger('Platform-fsp_sss-1718')
        with allure.step('非级联场景耗时测试'):
            changeRuleConf_step('rule-config_NotOverload.xml')
            time_uesd = check_sharescreen_time()
            allure.attach('耗时:%f秒'%time_uesd,'time',allure.attachment_type.TEXT)
            assert time_uesd >=0 and time_uesd <= 5

        with allure.step('级联场景耗时测试'):
            changeRuleConf_step( 'rule-config_cascade.xml')
            time_uesd = check_sharescreen_time()

            allure.attach('耗时:%f秒'%time_uesd,'time',allure.attachment_type.TEXT)
            assert time_uesd >= 0 and time_uesd <= 5


    @allure.story('Platform-fsp_sss-1723:同一个vnc-gs')
    def test_sharescreen_not_cascade(self):
        changeRuleConf_step('rule-config_NotOverload.xml')
        with allure.step('2个OC客户端通过同1个vnc-gs进行屏幕共享'):
            send_id,recv_id,result = check_oc_sharescreen()
            if not result:
                now_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                allure.attach("send_id:%s,recv_id:%s,time:%s"%(send_id,recv_id,now_time),'错误信息',allure.attachment_type.TEXT)
            assert result

    @allure.story('Platform-fsp_sss-1724:vnc_gs1 -> n-ss -> vnc_gs2')
    def test_sharescreen_cascade(self):

        changeRuleConf_step('rule-config_cascade.xml')
        with allure.step('2个OC客户端通过同2个vnc-gs进行屏幕共享'):
            send_id,recv_id,result = check_oc_sharescreen()
            if not result:
                now_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                allure.attach("send_id:%s,recv_id:%s,time:%s"%(send_id,recv_id,now_time),'错误信息',allure.attachment_type.TEXT)
            assert result

    @allure.story('Platform-fsp_sss-1725:vnc_gs1 -> n-ss1 -> n-ss2 -> vnc_gs2')
    @pytest.mark.skip(reason="尚未开发实现")
    def test_sharescreen_transnational_use_specialline(self):
        """
        屏幕共享跨国专线
        """
        changeRuleConf_step('rule-config_Tran.xml')
        with allure.step('2个OC客户端通过同2个vnc-gs进行屏幕共享'):
            send_id,recv_id,result = check_oc_sharescreen()
            if not result:
                now_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                allure.attach("send_id:%s,recv_id:%s,time:%s"%(send_id,recv_id,now_time),'错误信息',allure.attachment_type.TEXT)
            assert result



