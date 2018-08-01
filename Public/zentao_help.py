# coding:utf-8
import requests
from requests_toolbelt import MultipartEncoder
import hashlib
host = 'http://127.0.0.1'  # 禅道的服务器地址

def login(s,user,psw):
    u'''登录禅道'''
    loginUrl = host+"/zentao/user-login.html"
    h = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Referer": host+"/zentao/user-login.html",
        # "Cookie":  # 头部没登录前不用传cookie，因为这里cookie就是保持登录的
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        }

    body = {"account": user,
            "password": psw,
            "keepLogin[]": "on",
            "referer": host+"/zentao/my/"
            }
    print body
    try:
        r = s.post(loginUrl, data=body, headers=h)
        print(r.content)  # 打印结果看到location='http://127.0.0.1/zentao/my/'说明登录成功了
        if "/zentao/my/" in r.content:
            print("登录成功！")
            return True
        else:
            print("登录失败：%s" % r.content)
            return False
    except Exception as msg:
        print("登录失败:%s"%str(msg))
        return False

def upload_jpg(s):
    u'''上传图片'''
    url1 = host+"/zentao/file-ajaxUpload-5a26aca290b59.html?dir=image"
    m = MultipartEncoder(
        fields={
               "localUrl": (None, "1.png"),
               "imgFile": ("1.png", open("d:\\1.png", "rb"), "image/png")
               })
    try:
        r1 = s.post(url1, data=m, headers={'Content-Type': m.content_type})
        jpg_url = r1.json()["url"]
        return jpg_url
    except Exception as msg:
        print("上传失败：%s"%str(msg))
        return ""

def submit_bug(s,jpg_url,title="yoyoketang-这是一个带附件的内容"):

    # 提交bug, 带上附件
    url2 = host+"/zentao/bug-create-1-0-moduleID=0.html"

    m = MultipartEncoder(
        fields = [
            ("product", "1"),
            ("module","1"),
            ("project", ""),
            ("openedBuild[]", "trunk"),
            ("assignedTo", "admin"),
            ("type", "codeerror"),
            ("os", "all"),
            ("browser", "all"),
            ("color", ""),
            ("title", title),  # bug标题参数化
            ("severity", "3"),
            ("pri", "0"),
            ("steps", u'<p>[步骤]</p>\
                    <p>1、第一步点</p>\
                    <p>2、第二步点</p>\
                    <p>3、点三步点</p>\
                    <p>[结果]</p>\
                    <p><img src="%s" alt="" /></p>\
                    <p>[期望]</p>' % jpg_url),  # 正文图片地址参数
            ("story", "0"),
            ("task", "0"),
            ("mailto[]", ""),
            ("keywords", ""),
            # 这里的四个参数就是上传文件附件了
            ("files[]", ("1.png", open("d:\\1.png", "rb"), "image/png")),  # 附件1
            ("labels[]", "tu1"),
            ("files[]", ("2.png", open("d:\\2.png", "rb"), "image/png")),   # 附件1
            ("labels[]", "tu2"),
            ("uid", "5a2955c884f98"),
            ("case", "0"),
            ("caseVersion", "0"),
            ("result", "0"),
            ("testtask", "0")
             ])
    try:
        r2 = s.post(url2, data=m, headers={'Content-Type': m.content_type})
        print r2.content
    except Exception as msg:
        print("提交BUG失败：%s"%str(msg))

if __name__ == "__main__":
    s = requests.session()  # 保持会话
    login(s, user="admin", psw=hashlib.md5("Hj1qaz2w").hexdigest()) # 登录
    jpg = upload_jpg(s)  # 上传图
    # 获取上传图片后用的url地址传给提交bug的正文
    submit_bug(s, jpg, title="yoyoketang-这是一个带附件的内容")