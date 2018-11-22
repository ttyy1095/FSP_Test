#-*-coding:utf-8-*-

import pytest
import allure
import os, sys, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Config import config
from Producer import fsp_common_pb2 as pb_common


@allure.feature("路由")
class Test_BusinessInsulate(object):

    def changeRuleConf_step(self, sftp, fileName):
        filepath = os.path.join(os.path.abspath("../TestData"), fileName)
        sftp.put(filepath, "/fsmeeting/fsp_sss_stream/rule/rule-config.xml")
        time.sleep(2)



    def get_group_server(self, producer, service_type, client_ip, user_id, app_id,
                         company_id, room_id, service_type1):

        # CreateGroup中的service_type中无意义，即组并无AV或者VNC的区别，GetGroupServers需指定获取服务器类型
        resp = producer.CreateGroup(
            app_id=app_id,
            service_type=service_type,
            room_id=room_id,
            company_id=company_id)
        groupId = resp['group']['groupId']
        resp = producer.GetGroupServers(
            group_id=groupId,
            client_ip=client_ip,
            user_id=user_id,
            app_id=app_id,
            company_id=company_id,
            room_id=room_id,
            type=service_type1)
        return resp

    #业务路由与网络路由有交集
    @allure.story("业务路由与网络路由有交集")
    @pytest.mark.parametrize(
        "rule_conf,client_ip, user_id, app_id, company_id, room_id, av_expected, vnc_expected",
        [("business_net.xml","192.168.6.65", "1000000", "1", "41000", "100000", "gs1", "vncgs1"),
         ("","192.168.6.65", "1000001", "1", "41000", "100000", "gs2", "vncgs2"),
         ("","192.168.6.65", "1000001", "1", "41000", "100001", "gs1", "vncgs1"),
         ("","192.168.6.65", "1000001", "1", "41001", "100001", "gs2", "vncgs2")],
        ids=["匹配userId", "匹配roomId", "匹配compnayId", "匹配appId"])

    def test_business_insulate_by_in(self, sftp, producer,rule_conf, client_ip, user_id, app_id,
                                     company_id, room_id, av_expected, vnc_expected):
        if rule_conf != "":
            with allure.step("替换rule配置文件"):
                self.changeRuleConf_step(sftp, "business_net.xml")
        with allure.step('获取AV服务器'):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip,
                                         user_id, app_id, company_id, room_id,
                                         pb_common.EnumAVService)
            assert resp['groupServers'][0]['id'] == av_expected
        with allure.step('获取VNC服务器'):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip,
                                         user_id, app_id, company_id, room_id,
                                         pb_common.EnumVNCService)
            assert resp['groupServers'][0]['id'] == vnc_expected

    #匹配业务路由，与网络路由无交集

    @pytest.mark.parametrize(
        "rule_conf,client_ip, user_id, app_id, company_id, room_id, expected",
        [("business_only.xml","192.168.6.65", "1000000", "1", "41000", "100000", "EnumError"),
         ("","192.168.6.65", "1000001", "1", "41000", "100000", "EnumError"),
         ("","192.168.6.65", "1000001", "1", "41000", "100001", "EnumError"),
         ("","192.168.6.65", "1000001", "1", "41001", "100001", "EnumError")],
        ids=["匹配userId", "匹配roomId", "匹配compnayId", "匹配appId"])
    @allure.story("业务路由与网络路由无交集")
    def test_business_insulate_by_out(self, sftp, producer,rule_conf, client_ip, user_id, app_id,
                                      company_id, room_id, expected):
        # 仅匹配业务路由，此处会报异常
        if rule_conf !="":
            with allure.step("替换rule配置文件"):
                self.changeRuleConf_step(sftp, rule_conf)

        with allure.step('获取AV服务器'):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip,
                                         user_id, app_id, company_id, room_id,
                                         pb_common.EnumAVService)
            assert resp['response']['responseCode'] == expected
        with allure.step('获取VNC服务器'):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip,
                                         user_id, app_id, company_id, room_id,
                                         pb_common.EnumVNCService)
            assert resp['response']['responseCode'] == expected

    @allure.story("网络路由-国内规则-不过载")
    @pytest.mark.parametrize(
        "ruleConf,client_ip,av_expected,vnc_expected",
        [("rule-config_NotOverload.xml", "1.1.8.5", "gs1", "vncgs1"),
         ("", "1.1.8.6", "gs2", "vncgs2"),
         ("", "1.3.0.5", "gs3", "vncgs3"),
         ("", "221.183.18.212", "gs1", "vncgs1"),
         ("", "1.1.0.5", "gs2", "vncgs2"),
         ("", "1.2.8.5", "gs3", "vncgs3")])
    # ("rule-config_SuperiorOverload_internal.xml", "1.1.8.5", "gs3","vncgs")

    def test_getGroupServers_internal(self, producer, sftp, ruleConf, client_ip,
                                      av_expected, vnc_expected):
        if ruleConf != "":
            with allure.step("替换rule配置文件"):
                self.changeRuleConf_step(sftp, ruleConf)
        with allure.step("获取GS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumAVService)

            gsId = resp["groupServers"][0]["id"]
            assert gsId == av_expected
        with allure.step("获取VNCGS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumVNCService)
            gsId = resp["groupServers"][0]["id"]
            assert gsId == vnc_expected

    @allure.story("网络路由-国外规则-不过载")
    @pytest.mark.parametrize(
        "ruleConf,client_ip,av_expected,vnc_expected",
        [("rule-config_NotOverload.xml", "23.33.184.5", "gs1", "vncgs1"),
         ("", "23.33.184.55", "gs2", "vncgs2"),
         ("", "206.164.235.5", "gs3", "vncgs3"),
         ("", "206.164.224.5", "gs1", "vncgs1"),
         ("", "185.117.115.5", "gs2", "vncgs2")])

    def test_getGroupServers(self, producer, sftp, ruleConf, client_ip, av_expected,
                             vnc_expected):
        if ruleConf != "":
            with allure.step("替换rule配置文件"):
                self.changeRuleConf_step(sftp, ruleConf)
        with allure.step("获取GS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumAVService)

            gsId = resp["groupServers"][0]["id"]
            assert gsId == av_expected
        with allure.step("获取VNCGS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumVNCService)
            gsId = resp["groupServers"][0]["id"]
            assert gsId == vnc_expected

    @allure.story("网络路由-国内规则-全部过载")
    @pytest.mark.parametrize("ruleConf,client_ip,av_expected,vnc_expected", [
        ("rule-config_Overload.xml", "1.1.8.5", "gs3", "vncgs3"),
    ])
    def test_getGroupServers_overload_internal(self, producer, sftp, ruleConf, client_ip,
                                               av_expected, vnc_expected):
        with allure.step("替换rule配置文件"):
            self.changeRuleConf_step(sftp, ruleConf)
        with allure.step("获取GS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumAVService)

            gsId = resp["groupServers"][0]["id"]
            assert gsId == av_expected
        with allure.step("获取VNCGS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumVNCService)
            gsId = resp["groupServers"][0]["id"]
            assert gsId == vnc_expected

    @allure.story("网络路由-国外规则-全部过载")
    @pytest.mark.parametrize(
        "ruleConf,client_ip,av_expected,vnc_expected",
        [("rule-config_Overload.xml", "23.33.184.5", "gs3", "vncgs3")])
    def test_getGroupServers_overload(self, producer, sftp, ruleConf, client_ip,
                                      av_expected, vnc_expected):
        with allure.step("替换rule配置文件"):
            self.changeRuleConf_step(sftp, ruleConf)
        with allure.step("获取GS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumAVService)

            gsId = resp["groupServers"][0]["id"]
            assert gsId == av_expected
        with allure.step("获取VNCGS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumVNCService)
            gsId = resp["groupServers"][0]["id"]
            assert gsId == vnc_expected

    @allure.story("网络路由-国内规则-部分过载")
    @pytest.mark.parametrize("ruleConf,client_ip,av_expected,vnc_expected", [
        ("rule-config_PartialOverload.xml", "1.1.8.5", "gs1", "vncgs1"),
        ("", "1.1.8.6", "gs3", "vncgs3"),
    ])
    def test_getGroupServers_partialOverload_internal(
            self, producer, sftp, ruleConf, client_ip, av_expected, vnc_expected):
        if ruleConf != "":
            with allure.step("替换rule配置文件"):
                self.changeRuleConf_step(sftp, ruleConf)
        with allure.step("获取GS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumAVService)

            gsId = resp["groupServers"][0]["id"]
            assert gsId == av_expected
        with allure.step("获取VNCGS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumVNCService)
            gsId = resp["groupServers"][0]["id"]
            assert gsId == vnc_expected

    @allure.story("网络路由-国外规则-部分过载")
    @pytest.mark.parametrize("ruleConf,client_ip,av_expected,vnc_expected", [
        ("rule-config_PartialOverload.xml", "23.33.184.5", "gs1", "vncgs1"),
        ("", "23.33.184.6", "gs3", "vncgs3"),
    ])
    def test_getGroupServers_partialOverload(self, producer, sftp, ruleConf, client_ip,
                                             av_expected, vnc_expected):
        if ruleConf != "":
            with allure.step("替换rule配置文件"):
                self.changeRuleConf_step(sftp, ruleConf)
        with allure.step("获取GS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumAVService)

            gsId = resp["groupServers"][0]["id"]
            assert gsId == av_expected
        with allure.step("获取VNCGS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumVNCService)
            gsId = resp["groupServers"][0]["id"]
            assert gsId == vnc_expected

    @allure.story("网络路由-上级过载")
    @pytest.mark.parametrize("ruleConf,client_ip,av_expected,vnc_expected", [
        ("rule-config_SuperiorOverload.xml", "1.1.8.5", "gs2", "vncgs2"),
        ("", "23.33.184.5", "gs2", "vncgs2"),
    ])
    def test_getGroupServers_superiorOverload(self, producer, sftp, ruleConf, client_ip,
                                              av_expected, vnc_expected):
        if ruleConf != "":
            with allure.step("替换rule配置文件"):
                self.changeRuleConf_step(sftp, ruleConf)
        with allure.step("获取GS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumAVService)

            gsId = resp["groupServers"][0]["id"]
            assert gsId == av_expected
        with allure.step("获取VNCGS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumVNCService)
            gsId = resp["groupServers"][0]["id"]
            assert gsId == vnc_expected

    @allure.story("异常测试")
    @pytest.mark.parametrize("ruleConf,client_ip,av_expected,vnc_expected", [
        ("rule-config_NotOverload.xml", "266.1.8.5", "EnumError", "vncgs2"),
        ("rule-config_Null.xml", "192.168.6.65", "EnumError", "vncgs2"),
    ],ids=["错误的IP地址","默认组为空"] )
    def test_route_abnormal(self,producer,sftp,ruleConf,client_ip,av_expected,vnc_expected):
        if ruleConf != "":
            with allure.step("替换rule配置文件"):
                self.changeRuleConf_step(sftp, ruleConf)
        with allure.step("获取GS服务器"):
            resp = self.get_group_server(producer, pb_common.EnumAVService, client_ip, "",
                                         "", "", "", pb_common.EnumAVService)

            gsId = resp["response"]["responseCode"]
            assert gsId == av_expected


if __name__ == '__main__':
    pass
