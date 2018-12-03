#-*-coding:utf-8-*-

import win32api
import win32gui
import win32con
import win32com.client
import psutil
import os, time
import subprocess
from Config.config import *
import shutil
import re
from lxml import etree
import _winreg
import uuid
import logging


key = _winreg.OpenKey(
    _winreg.HKEY_CURRENT_USER,
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
documents_path, type = _winreg.QueryValueEx(key, "Personal")
print documents_path, type
import win32process

logger = logging.getLogger(__file__)
def click_keys(hwnd, *args):
    """
    定义组合按键
    :param hwd:
    :param args:
    :return:
    """
    for arg in args:
        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, arg, 0)
    for arg in args:
        win32api.SendMessage(hwnd, win32con.WM_KEYUP, arg, 0)


def left_click(hwnd, x, y, sleep_time=1.0):
    """
    左键单击
    :param hwnd:
    :param x:
    :param y:
    :param sleep_time:
    :return:
    """
    long_position = win32api.MAKELONG(x, y)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON,
                         long_position)
    time.sleep(0.1)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)
    time.sleep(sleep_time)


def input_chars(hwnd, pwd):
    """
    输入字符
    :param hwnd:
    :param pwd:
    :return:
    """
    for i in pwd:
        a = ord(i)
        win32gui.SendMessage(hwnd, win32con.WM_CHAR, a, 0)


def close_windows(hwnd):
    """
    关闭指定窗口
    :param hwnd:
    :return:
    """
    win32gui.SendMessage(hwnd, win32con.WM_CLOSE)


class Client(object):
    def __init__(self, client_flag, is_oc=True):
        self.hwnd = 0
        self.dm = win32com.client.Dispatch('dm.dmsoft')
        print self.dm.Ver()

        self.dm.SetPath(os.path.dirname(os.path.realpath(__file__)))
        self.dm.SetDict(0, "dm_soft.txt")
        self.client_flag = client_flag
        logger.info('client flag is: %s'%client_flag)
        self.client_path = OC_PATH if is_oc else NC_PATH
        self.modificationUserDataDirName(client_flag)

    def get_real_menu(self):
        """
        此处大坑，开始菜单有2个窗口，一个窗口做显示，一个窗口接收操作，SendMessage需发送给可见窗口
        :return:
        """

        def callback(h, extra):

            try:
                if win32gui.IsWindowVisible(h) and win32gui.GetClassName(h) == "MENUEX":
                    if "开始菜单" == win32gui.GetWindowText(h).decode("gbk").encode("utf-8"):
                        extra.append(h)
            except:
                print h
            return True

        extra = []
        win32gui.EnumWindows(callback, extra)
        if len(extra) > 0:
            return extra[0]
        return 0

    def modificationUserDataDirName(self, client_flag):
        """
        为保证每个用户的日志为独立的，方便区分，在登录前修改客户端配置文件，使日志目录独立出来
        :param client_flag:
        :return:
        """
        os.system("cd /D %s && BlowFishTest.exe -i config.data -o config.data.xml -m 0" %
                  self.client_path)
        with open(os.path.join(self.client_path, "config.data.xml"), "r") as f:
            client_config = f.read()
        root = etree.fromstring(client_config)
        element = root.xpath('AppCustomParam/Param[@Name="UserDataDirName"]')[0]
        element.set("Value", "\\Inpor\\%s\\" % client_flag)

        with open(os.path.join(self.client_path, "config.data.xml"), "w") as f:
            conf = '<?xml version="1.0" encoding="UTF-8" ?>\n' + etree.tostring(
                root) + "\n"
            f.write(conf)
        os.system("cd /D %s && BlowFishTest.exe -i config.data.xml -o config.data -m 1" %
                  self.client_path)

    def login(self, user_name, user_pwd, room_id, front_server="192.168.7.185:1089"):


        commandline = "%s -uname %s -upwd %s -rid %s -utype 1 -link TCP:%s -stype 1"%\
                      (os.path.join(self.client_path,"FastMeeting.exe"),user_name,user_pwd,room_id,front_server)
        subprocess.Popen(commandline)
        while self.hwnd == 0:
            time.sleep(5)
            classname = "CMainDlg"
            titlename = u"好视通云会议"
            self.hwnd = win32gui.FindWindow(classname, titlename)
        print self.hwnd
        win32gui.SetWindowText(self.hwnd, self.client_flag)
        rect = (0, 0, 0, 0)
        i = 0
        while rect[2] - rect[0] <= 929:
            if i > 60:
                raise Exception('login outtime')
            time.sleep(1)
            rect = win32gui.GetWindowRect(self.hwnd)
            i += 1
        win32gui.MoveWindow(self.hwnd, 0, 0, 929, 694, 0)
        time.sleep(1)

        ret = self.dm.BindWindowEx(self.hwnd, "gdi2", "windows", "windows", "", 0)
        if ret == 0:
            raise Exception("BindWindow Error")
        time.sleep(3)

    def applyChairman(self):
        """
        申请主席
        :return:
        """
        ret, x, y = self.dm.FindStr(2, 174, 35, 209, u"出席", "169ada-202020", 1)
        print ret, x, y
        if ret != -1:
            left_click(self.hwnd, 45, 44)
        time.sleep(1)

        hwd = self.get_real_menu()
        # 点击申请成为主席
        left_click(hwd, 55, 94)
        hwd = win32gui.FindWindow("CPasswordDlg", u"输入会议主席密码")
        # 密码输入框获得焦点
        left_click(hwd, 188, 57, 0.5)
        childhwd = win32gui.FindWindowEx(hwd, 0, "EditWnd", "")
        time.sleep(0.05)
        input_chars(childhwd, "123456")
        time.sleep(0.05)
        # 点击确定按钮
        left_click(hwd, 182, 136)
        # 关闭倒计时窗口
        hwd = win32gui.FindWindow("CCustomMsgBox", u"MessageBox")
        close_windows(hwd)
        time.sleep(2)
        ret, x, y = self.dm.FindStr(2, 174, 35, 209, u"主席", "169ada-202020", 1)
        print ret, x, y
        if ret == -1:
            raise Exception("applyChairman Error")

    def publishVideo(self):
        """
        广播视频
        :return:
        """
        if self.dm.CmpColor(182, 192, 'ecf3fb', 1) == 0:
            left_click(self.hwnd, 182, 192)

    def stopPublishVideo(self):
        """
        停止广播视频
        :return:
        """
        if self.dm.CmpColor(182, 192, '169ada', 1) == 0:
            left_click(self.hwnd, 182, 192)

    def publishAudio(self):
        """
        广播音频
        :return:
        """

        if self.dm.CmpColor(155, 198, '6c8cb1', 1) == 0:
            left_click(self.hwnd, 155, 198)

    def stopPublishAudio(self):
        """
        停止广播音频
        :return:
        """
        if self.dm.CmpColor(155, 198, '169ada', 1) == 0:
            left_click(self.hwnd, 155, 198)

    def shareScreen(self):
        """
        开启屏幕共享
        :return:
        """
        # 判断是否为主讲，不是则点击申请主讲
        if self.dm.CmpColor(204, 47, 'ffbf28', 1) == 1:
            left_click(self.hwnd, 204, 47)
        # 点击共享
        left_click(self.hwnd, 284, 47)
        # 获取共享菜单窗口句柄
        hwd = self.get_real_menu()
        print "开始菜单", hwd
        left_click(hwd, 70, 44)

    def stopShareScreen(self):
        """
        关闭屏幕共享
        :return:
        """
        ret, x, y = self.dm.FindStr(240, 79, 738, 112, u"屏幕共享",
                                    "0c89d1-202020|37475a-202020", 1)
        if ret != -1:
            print x, y
            left_click(self.hwnd, x + 69, y + 3)
        else:
            raise Exception("can't find 屏幕共享")

    def shareMediaFile(self):
        pass

    def closeClient(self):
        """
        关闭当前客户端
        :return:
        """
        self.dm.UnBindWindow()
        win32gui.SendMessage(self.hwnd, win32con.WM_CLOSE)

    def decodeLog(self, log_file_header):
        tm = time.localtime(time.time())
        log_path = os.path.join(documents_path, "Inpor", self.client_flag, "log",
                                "%s-%s-%s" % (tm.tm_year, str(tm.tm_mon).zfill(2), str(tm.tm_mday).zfill(2)))
        # shutil.copyfile(file_abs, copy_name)
        log_files = os.listdir(log_path)
        log_file = ""
        for i in range(len(log_files) - 1, 0, -1):
            if log_file_header == log_files[i][:len(log_file_header)]:
                log_file = log_files[i]
                break
        print log_file
        if log_file == "":
            raise Exception("get log file error")
        copy_filename = os.path.join(log_path, "copy_%s" % log_file)
        shutil.copyfile(os.path.join(log_path, log_file), copy_filename)
        os.system("LogFilter.exe -m 3 -i %s -o %s.text" % (copy_filename, copy_filename))
        return "%s.text" % copy_filename

    def getVideoRecvInfo(self):
        log_file = self.decodeLog("AVQuality-")

        with open(log_file, 'r') as f:
            logStr = f.read()

        regtext = r'{"title":"clividrcv",.+}'

        pattern = re.compile(regtext)
        matchStrs = pattern.findall(logStr)
        if len(matchStrs) == 0:
            return False
        return True

    def has_recv_shareScreen(self):
        log_file = self.decodeLog("vncmp-")

        with open(log_file, 'r') as f:
            logStr = f.read()
        regtext = r'VideoDecoder:VIDEO_Decode_StartDecompress success'
        pattern = re.compile(regtext)
        matchStrs = pattern.findall(logStr)
        if len(matchStrs) == 0:
            return False
        return True

    def count_av_log(self):
        """
        返回当前音视频日志中接收到音视频相关日志的条数
        :return:
        """
        log_file = self.decodeLog("AVQuality-")

        with open(log_file, 'r') as f:
            logStr = f.read()

        vidrcvs = re.findall(r'{"title":"clividrcv",.+}', logStr)
        audrcvs = re.findall(r'{"title":"cliaudrcv",.+}', logStr)
        return len(audrcvs),len(vidrcvs)

    def has_recv_audio_video(self):
        """
        这里接收音频需要保证有持续的音视频流，最好在禁用掉其他音视频设备，保证音视频源设备只有vcam和立体声混音
        """
        log_file = self.decodeLog("AVQuality-")

        with open(log_file, 'r') as f:
            logStr = f.read()

        vidrcvs = re.findall(r'{"title":"clividrcv",.+}', logStr)
        audrcvs = re.findall(r'{"title":"cliaudrcv",.+}', logStr)

        if len(vidrcvs) == 0 or len(audrcvs) == 0:
            return False
        return True

    def calc_sharescreen_time(self):
        log_file = self.decodeLog("vncmp-")
        with open(log_file, 'r') as f:
            logStr = f.read()

        start_time = re.findall(r'(\d{2}:\d{2}:\d{2})\.\d{6}', logStr)[0]
        start_time = time.mktime(
            time.strptime('2018-01-01 %s' % start_time, '%Y-%m-%d %H:%M:%S'))
        recv_time = re.findall(
            r'(\d{2}:\d{2}:\d{2})\.\d{6}.*?VideoDecoder:VIDEO_Decode_StartDecompress success',
            logStr)[0]
        recv_time = time.mktime(
            time.strptime('2018-01-01 %s' % recv_time, '%Y-%m-%d %H:%M:%S'))

        return recv_time - start_time

    @staticmethod
    def close_all_client():
        os.system('taskkill /f /im FastMeeting.exe')
        return
        # def get_windows_by_pid(pid):
        #     def callback(h, extra):
        #         try:
        #             if win32process.GetWindowThreadProcessId(
        #                     h)[1] == pid and (win32gui.GetClassName(h) in ["CMainDlg","FMWnd","CLoginDlg"]):
        #                 extra.append(h)
        #         except:
        #             print h
        #         return True
        #
        #     extra = []
        #     win32gui.EnumWindows(callback, extra)
        #     return extra
        #
        # for p in psutil.process_iter():
        #     if p.name() == 'FastMeeting.exe':
        #         hwnd = get_windows_by_pid(p.pid)[0]
        #         close_windows(hwnd)


def check_oc_av():
    Client.close_all_client()
    send_id = str(uuid.uuid4())
    send = Client(send_id)
    send.login(USERA_NAME, USER_PWD, ROOM1_ID)

    recv_id = str(uuid.uuid4())
    recv = Client(recv_id)
    recv.login(USERB_NAME, USER_PWD, ROOM1_ID)
    send.publishVideo()
    send.publishAudio()
    time.sleep(30)
    send.closeClient()
    recv.closeClient()
    return send_id, recv_id, recv.has_recv_audio_video()


def check_oc_sharescreen():
    Client.close_all_client()
    send_id = str(uuid.uuid4())
    send = Client(send_id)
    send.login(USERA_NAME, USER_PWD, ROOM1_ID)

    recv_id = str(uuid.uuid4())
    recv = Client(recv_id)
    recv.login(USERB_NAME, USER_PWD, ROOM1_ID)
    send.shareScreen()

    time.sleep(30)
    send.closeClient()
    recv.closeClient()
    return send_id, recv_id, recv.has_recv_shareScreen()


def check_oc_sharemedia():
    Client.close_all_client()
    send_id = str(uuid.uuid4())
    send = Client(send_id)
    send.login(USERA_NAME, USER_PWD, ROOM1_ID)
    send.shareMediaFile()
    recv_id = str(uuid.uuid4())
    recv = Client(recv_id)
    recv.login(USERB_NAME, USER_PWD, ROOM1_ID)

    time.sleep(30)
    send.closeClient()
    recv.closeClient()
    return send_id, recv_id, recv.has_recv_audio_video()


def check_nc_av():
    Client.close_all_client()
    send_id = str(uuid.uuid4())
    send = Client(send_id, False)
    send.login(USERA_NAME, USER_PWD, ROOM1_ID)

    recv_id = str(uuid.uuid4())
    recv = Client(recv_id, False)
    recv.login(USERB_NAME, USER_PWD, ROOM1_ID)

    send.publishVideo()
    send.publishAudio()
    time.sleep(30)
    send.closeClient()
    recv.closeClient()
    return send_id, recv_id, recv.has_recv_audio_video()


def check_nc2oc_av():
    Client.close_all_client()
    send_id = str(uuid.uuid4())
    send = Client(send_id, False)
    send.login(USERA_NAME, USER_PWD, ROOM1_ID)

    recv_id = str(uuid.uuid4())
    recv = Client(recv_id)
    recv.login(USERB_NAME, USER_PWD, ROOM1_ID)

    send.publishVideo()
    send.publishAudio()
    time.sleep(30)
    send.closeClient()
    recv.closeClient()
    return send_id, recv_id, recv.has_recv_audio_video()


def check_oc2nc_av():
    Client.close_all_client()
    send_id = str(uuid.uuid4())
    send = Client(send_id)
    send.login(USERA_NAME, USER_PWD, ROOM1_ID)

    recv_id = str(uuid.uuid4())
    recv = Client(recv_id, False)
    recv.login(USERB_NAME, USER_PWD, ROOM1_ID)

    send.publishVideo()
    send.publishAudio()
    time.sleep(30)
    send.closeClient()
    recv.closeClient()
    return send_id, recv_id, recv.has_recv_audio_video()


def check_sharescreen_time():
    Client.close_all_client()
    send_id = str(uuid.uuid4())
    send = Client(send_id)
    send.login(USERA_NAME, USER_PWD, ROOM1_ID)
    send.shareScreen()

    recv_id = str(uuid.uuid4())
    recv = Client(recv_id, False)
    recv.login(USERB_NAME, USER_PWD, ROOM1_ID)
    time.sleep(30)
    send.closeClient()
    recv.closeClient()

    if recv.has_recv_shareScreen():
        time_used = recv.calc_sharescreen_time()
        return time_used
    else:
        return -1

