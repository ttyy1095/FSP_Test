#-*-coding:utf-8-*-

import sys
import json
import testlink
import jenkins
from Config import config

class My_TestLink():
    def __init__(self,build_tag):
        self.tlc = testlink.TestlinkAPIClient(config.testlink_url,config.testlink_devkey,encoding="utf-8")
        self.jenkins = jenkins.Jenkins(config.jenkins_url,config.jenkins_user,config.jenkins_password)

        self.fsp_version,branch = self.get_build_number(build_tag)
        print self.fsp_version,branch
        self.testProject = "流式服务"
    def get_build_number(self,build_tag):
        if build_tag == "lastSuccessfulBuild":
            job_info = self.jenkins.get_job_info("build_platform_fsp_stream")
            print  json.dumps(job_info)
            build_number = job_info["lastCompletedBuild"]["number"]
        else:
            build_number = int(build_tag)
        try:
            build_info = self.jenkins.get_build_info("build_platform_fsp_stream", build_number)
            print json.dumps(build_info)
            return build_info["actions"][0]["parameters"][0]["value"],build_info["actions"][0]["parameters"][1]["value"]
        except jenkins.JenkinsException as e:

            print "获取构建信息出错，%s" % e.message
            sys.exit(1)
    def add_test_plan(self):
        self.tlc.getProjectTestPlans()

    def my(self,testplan=None):
        # self.tlc.listProjects()
        if testplan == "":
            return
        testproject_id = self.tlc.getTestProjectByName(self.testProject)["id"]
        all_plans = self.tlc.getProjectTestPlans(testproject_id)
        isPlanExist = False
        for plan in all_plans:
            if plan["name"].encode('utf-8') == testplan:
                isPlanExist = True
        if not isPlanExist:
            self.tlc.createTestPlan(testplan,testprojectname=self.testProject)
        print json.dumps(self.tlc.getTestPlanByName(self.testProject,testplan))
        testplan_id = self.tlc.getTestPlanByName(self.testProject,testplan)[0]["id"]
        if len(self.tlc.getBuildsForTestPlan(testplan_id))== 0:
            build_name = self.tlc.createBuild(testplan_id,self.fsp_version,"版本说明")["name"]
        else:
            build_name = self.tlc.getLatestBuildForTestPlan(testplan_id)["name"]


        testcases_plan = self.tlc.getTestCasesForTestPlan(testplan_id)
        print json.dumps(testcases_plan)
        print testcases_plan.keys()
        print "-----------------"
        print json.dumps(self.tlc.getTestCase(None,testcaseexternalid="Platform-fsp_sss-936"))
        testcase_id = self.tlc.getTestCase(None,testcaseexternalid="Platform-fsp_sss-936")[0]["testcase_id"]

        if testcase_id not in testcases_plan.keys():

            self.tlc.addTestCaseToTestPlan(testproject_id,testplan_id,"Platform-fsp_sss-936",1)
            self.tlc.assignTestCaseExecutionTask("huangjie",testplan_id,"Platform-fsp_sss-936",buildname=build_name)

        self.tlc.reportTCResult(testcase_id,testplan_id,build_name,"p","")


if __name__ == '__main__':

    tl = My_TestLink("506")
    tl.my("调试计划")


