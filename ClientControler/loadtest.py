#-*-coding:utf-8-*-
import os,time
import win32api,win32con,win32gui
while True:
    hwnd = win32gui.FindWindow("#32770",u"仿真测试客户端")
    startBtn = win32gui.FindWindowEx(hwnd,0,"Button",u"启动")
    win32gui.SendMessage(hwnd,win32con.WM_COMMAND,win32api.MAKELONG(1003,win32con.BN_CLICKED),startBtn)

    time.sleep(300)

    x = win32gui.GetDlgItemText(hwnd,1021)
    if x != "0":
        win32gui.MessageBox(0,u"登录出错",u"登录",win32con.MB_OK)
        quit(-1)

    startBtn = win32gui.FindWindowEx(hwnd,0,"Button",u"停止")
    win32gui.SendMessage(hwnd,win32con.WM_COMMAND,win32api.MAKELONG(1003,win32con.BN_CLICKED),startBtn)
    time.sleep(10)
    startBtn = win32gui.FindWindowEx(hwnd,0,"Button",u"重新启动")
    win32gui.SendMessage(hwnd,win32con.WM_COMMAND,win32api.MAKELONG(1003,win32con.BN_CLICKED),startBtn)
    time.sleep(10)

