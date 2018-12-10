#-*-coding:utf-8-*-
import os, time
import win32api, win32con, win32gui
from lxml import etree
import subprocess
import sys
import os
_path = '..'
sys.path.append(_path)
from Config.config import *


def _deploy_simulator_config(roomlist,
                             userlist,
                             userpwd,
                             roompwd='123456',
                             frontaddr='TCP:192.168.7.185:1089'):
    xmlfile_path = os.path.join(SIMULATOR_PATH, 'ClientSimulator.xml')
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xmlfile_path, parser)
    root = tree.getroot()
    frontaddr_el = tree.find('FrontAddr')
    frontaddr_el.text = frontaddr
    roomlist_el = root.find('RoomList')
    # 遍历删除房间
    for room in roomlist_el.getchildren():
        roomlist_el.remove(room)
    # 遍历添加房间
    for roomid in roomlist:
        room_el = etree.SubElement(roomlist_el, 'Room')
        roomid_el = etree.SubElement(room_el, 'RoomID')
        roomid_el.text = roomid
        roompassword_el = etree.SubElement(room_el, 'RoomPassword')
        roompassword_el.text = roompwd

    userlist_el = root.find('UserList')
    # 遍历删除用户
    for user in userlist_el.getchildren():
        userlist_el.remove(user)
    # 遍历添加用户
    for user in userlist:
        user_el = etree.SubElement(userlist_el, 'User')
        username_el = etree.SubElement(user_el, 'UserName')
        username_el.text = user
        userpwd_el = etree.SubElement(user_el, 'UserPwd')
        userpwd_el.text = userpwd
    # 保存到xml文件
    etree.ElementTree(root).write(
        xmlfile_path, pretty_print=True, encoding='utf-8', xml_declaration=True)


class ClientSimulator():
    def __init__(self,simulator_index, roomlist, userlist, userpwd):
        _deploy_simulator_config(roomlist, userlist, userpwd)
        self.simulator_index = simulator_index
        self.hwnd = 0
        self.total_user = len(roomlist)*len(userlist)

    def start(self):
        prog = os.path.join(SIMULATOR_PATH,'ClientSimulatorUI.exe')
        subprocess.Popen(prog)
        time.sleep(3)
        self.hwnd = win32gui.FindWindow("#32770", u"仿真测试客户端")
        print(self.hwnd)
        if self.hwnd > 0:
            startBtn = win32gui.FindWindowEx(self.hwnd, 0, "Button", u"启动")
            win32gui.SendMessage(self.hwnd, win32con.WM_COMMAND,
                                 win32api.MAKELONG(1003, win32con.BN_CLICKED), startBtn)
        loginuser_count = 0
        timeout = 0
        while loginuser_count != self.total_user:
            if timeout>120:return False
            loginuser_count = int(win32gui.GetDlgItemText(self.hwnd, 1009))
            time.sleep(1)
            timeout += 1
        return True


    def stop(self):
        stopBtn = win32gui.FindWindowEx(self.hwnd, 0, "Button", u"停止")
        win32gui.SendMessage(self.hwnd, win32con.WM_COMMAND,
                                 win32api.MAKELONG(1003, win32con.BN_CLICKED), stopBtn)
        time.sleep(5)
        quitBtn = win32gui.FindWindowEx(self.hwnd, 0, "Button", u"退出")
        win32gui.SendMessage(self.hwnd, win32con.WM_COMMAND,
                             win32api.MAKELONG(1001, win32con.BN_CLICKED), quitBtn)

if __name__ == '__main__':
    cs = ClientSimulator(['107926'],['ptAutoTest00','ptAutoTest01'],'000000')
    print cs.start()
    time.sleep(10)
    # cs.stop()