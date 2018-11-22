#-*-coding:utf-8-*-
import os
import time

import allure
import paramiko
import Producer
import pytest
from Config.config import *





class Test_GC():

    @allure.step
    def createGroup_step(self,producer,app_id,room_id):
        return producer.CreateGroup(gc_group_topic,1,app_id,0,room_id,as_topic)

    @allure.step
    def changeRuleConf_step(self,sftp,fileName):
        filepath = os.path.join(os.path.abspath("../TestData"),fileName)
        sftp.put(filepath,"/fsmeeting/fsp_sss_stream/rule/rule-config.xml")
        time.sleep(2)

    @pytest.mark.parametrize("app_id,room_id",[(app_id,room_id),("error app","error room")],
                             ids=["vaild app_id and vaild room_id","invaild app_id and invaild room_id"])
    @allure.feature("GC")
    @allure.story("创建群组")
    def test_createGroup(self,producer,app_id,room_id):

        response = producer.CreateGroup(gc_group_topic,1,app_id,0,room_id,as_topic)
        groupId = response["group"]["groupId"]
        groupCheckCode = response["group"]["groupCheckCode"]
        assert groupId != ""
        assert groupCheckCode != ""

    @pytest.mark.parametrize("ruleConf,client_ip,expected",
                             [("rule-config_NotOverload_internal.xml", "1.1.8.5", "gs1"),
                              ("rule-config_NotOverload_internal.xml", "1.1.8.6", "gs2"),
                              ("rule-config_NotOverload_internal.xml", "1.3.0.5", "gs3"),
                              ("rule-config_NotOverload_internal.xml", "221.183.18.212", "gs1"),
                              ("rule-config_NotOverload_internal.xml", "1.1.0.5", "gs2"),
                              ("rule-config_NotOverload_internal.xml", "1.2.8.5", "gs3"),
                              ("rule-config_SuperiorOverload_internal.xml", "1.1.8.5", "gs3")])
    @allure.feature("接入优化")
    @allure.story("gs")
    def test_getGroupServers(self,producer,sftp,ruleConf,client_ip,expected):
        allure.attach("allure attach")
        self.changeRuleConf_step(sftp,ruleConf)
        response = self.createGroup_step(producer,app_id,room_id)
        groupId = response["group"]["groupId"]
        response = producer.GetGroupServers(gc_group_topic,1,groupId,client_ip,as_topic)
        gsId = response["groupServers"][0]["id"]
        assert gsId == expected


