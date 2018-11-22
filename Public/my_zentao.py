# -*-coding:utf-8-*-
import hashlib
import json
import os
import sys

import requests

from requests_toolbelt import MultipartEncoder

reload(sys)
sys.setdefaultencoding('utf-8')


class zentao(object):
    def __init__(self, zentao_url, account, password, productName, projectName):
        """
        :param zentao_url: 禅道地址，如：http://192.168.5.68/zentao/
        :param account: 禅道用户名
        :param password: 禅道密码
        :param productName: 所属产品
        :param projectName: 所属项目
        """
        self.session = requests.session()
        self.zentao_url = zentao_url
        self._login(account, password)
        self.productID = self._getProductID(productName)
        self.projectID = self._getProjectID(projectName)
        print "当前产品ID：%s,当前项目ID：%s" % (self.productID, self.projectID)

        self.modules = self._getAllModule()
        self.builds = self._getAllBuilds()

    def _login(self, account, password):
        login_url = self.zentao_url + "user-login.json"
        data = {"account": account, "password": hashlib.md5(password).hexdigest(), "referer": self.zentao_url + "my/", "keepLogin[]": "on"}

        response = self.session.post(login_url, data)
        if response.status_code != 200:
            raise Exception("login failed by response:%s" % str(response))
        else:
            result = json.loads(response.text)
            status = result["status"]
            if status != "success":
                reason = result["reason"]
                raise Exception("login failed by reason: %s" % str(reason))

    def _getProductID(self, productName):
        products = self._getAllProducts()
        return products[productName]

    def _getProjectID(self, projectName):
        projects = self._getProjects(self.productID)
        return projects[projectName]

    def _getAllProducts(self):
        products = {}
        products_url = self.zentao_url + "product-all-0--all.json"
        response = self.session.get(products_url)
        if response.status_code == 200:
            products_info = json.loads(json.loads(response.text)["data"])["products"]
            for key, value in products_info.items():
                products[str(value).strip()] = str(key).strip()
            return products
        else:
            raise Exception("Get all products error: %s" % str(response))

    def _getProjects(self, productID):
        projects = {}
        projects_url = self.zentao_url + "product-ajaxGetProjects-%s-0-0.json" % productID
        response = self.session.get(projects_url)
        if response.status_code == 200:
            projects_info = json.loads(response.text)
            for key, value in projects_info.items():
                projects[str(value).strip()] = str(key).strip()
            return projects
        else:
            raise Exception("status code is not 200")

    def _getAllModule(self):
        modules = {}
        module_url = self.zentao_url + "tree-ajaxGetOptionMenu-%s-bug-0-0-json--true.json" % self.productID
        response = self.session.get(module_url)
        if response.status_code == 200:
            modules_info = json.loads(response.text)
            for key, value in modules_info.items():
                modules[str(value).strip()] = str(key).strip()
            return modules
        else:
            raise Exception("status code is not 200")
    def get_build_info(self,build_version):
        builds_url = self.zentao_url + "project-build-%s.json" % (self.projectID)
        response = self.session.get(builds_url)
        resp =  response.text
        builds = json.loads(json.loads(resp)["data"])["builds"]
        for build in builds:
            if build["name"] == build_version:
                return build["filePath"]
        return ""

    def _getAllBuilds(self):
        builds = {}
        builds_url = self.zentao_url + "build-ajaxGetProjectBuilds-%s-%s-openedBuild-0-0-0-true.json" % (self.projectID, self.productID)
        response = self.session.get(builds_url)

        if response.status_code == 200:
            builds_info = json.loads(response.text)

            for key, value in builds_info.items():
                builds[str(value).strip()] = str(key).strip()
            return builds
        else:
            raise Exception("status code is not 200")

    def _getTeamMembers(self):
        member_url = self.zentao_url + "bug-ajaxLoadProjectTeamMembers-%s-.html" % self.productID
        self.session.get(member_url)

    def insertImg(self, filepath):

        return u'<img src="%s" alt="" />' % (self._upload_img(filepath))

    def _upload_img(self, filepath):
        url1 = self.zentao_url + "file-ajaxUpload-5a26aca290b59.html?dir=image"
        file = os.path.basename(filepath)
        fields = {"localUrl": (None, file), "imgFile": (file, open(filepath, "rb"), "image/png")}
        m = MultipartEncoder(fields=fields)
        try:
            r1 = self.session.post(url1, data=m, headers={'Content-Type': m.content_type})
            jpg_url = r1.json()["url"]
            return jpg_url
        except Exception as msg:
            print("上传失败：%s" % str(msg))
            return ""

    def _getProjectBug(self):
        bugs = []
        projectbug_url = self.zentao_url + "project-bug-%s.json" % self.projectID
        response = self.session.get(projectbug_url)
        if response.status_code == 200:
            bugs_info = json.loads(json.loads(response.text)["data"])["bugs"]
            for bug_info in bugs_info:
                bugs.append(bug_info["title"])
            return bugs

    def createBug(self, moduleName, openedBuild, assignedTo, bugtitle, severity, steps, attachments=[]):
        """

        :param moduleName: 所属模块
        :param openedBuild: 影响版本
        :param assignedTo: 指派给
        :param bugtitle: bug标题
        :param severity: 严重程度
        :param steps: 类型为List，如：[步骤一，步骤二,...,结果，期望]。最小长度为3。如果需要加入图片，调用insert方法，将返回值添加到步骤中
        :param attachments: 类型为List，要添加的附件的路径，最好将附件打包为zip压缩包后上传
        :return:
        """

        moduleID = self.modules[moduleName]
        openedBuildID = self.builds[openedBuild]

        report_url = self.zentao_url + "bug-create-%s-0-moduleID=0.json" % (self.productID)

        if len(steps) < 3:
            raise Exception("steps error:len(step)<3")
        test_expectation = steps[-1]
        test_result = steps[-2]
        steps_text = u'<p>[步骤]</p>'
        for i in range(0, len(steps) - 2):
            steps_text += u'<p>%s、%s</p>' % (i + 1, steps[i])
        steps_text += u'<p>[结果]</p><p>%s</p>' % test_result
        steps_text += u'<p>[期望]</p><p>%s</p>' % test_expectation

        print steps_text

        fields = [
            ("product", self.productID),
            ("module", moduleID),
            ("project", self.projectID),
            ("openedBuild[]", openedBuildID),
            ("assignedTo", assignedTo),
            ("type", "codeerror"),
            ("os", "all"),
            ("browser", "all"),
            ("color", ""),
            ("title", bugtitle),  # bug标题参数化
            ("severity", str(severity)),
            ("pri", "0"),
            ("steps", steps_text),  # 正文图片地址参数
            ("story", "0"),
            ("task", "0"),
            ("mailto[]", ""),
            ("keywords", ""),
            ("uid", "5a2955c884f98"),
            ("case", "0"),
            ("caseVersion", "0"),
            ("result", "0"),
            ("testtask", "0")
        ]

        for filepath in attachments:
            file = os.path.basename(filepath)
            filename, filetype = os.path.splitext(file)
            if filetype == "log":
                filetype = "txt"
            fields.append(("files[]", (file, open(filepath, "rb"), filetype)))
            fields.append(("labels[]", filename))

        m = MultipartEncoder(fields=fields)

        try:
            response = self.session.post(report_url, data=m, headers={'Content-Type': m.content_type})
            print response.content
        except Exception as msg:
            print "提交BUG失败：%s" % str(msg)


if __name__ == '__main__':

    # zt = zentao("http://127.0.0.1/zentao/", "huangjie", "Hj1qaz2w", "测试产品", "测试项目")

    # steps = ["第一步", "第二部", "第三部", "结果嗝屁了" + zt.insertImg("d:\\1.png"), "期望成功啊"]
    # attachments = ["d:\\1.png", "d:\\2.png", u"d:\\待删除.txt", "d:\\1.zip", "d:\\1.log"]
    # zt.createBug("/登录", "主干", "huangjie", "测试bugtitlej", 3, steps, attachments)
    # bugs = zt._getProjectBug()
    # print bugs
    pass
