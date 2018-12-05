# -*- coding:utf-8 -*-
"""
__description__ = load FsBase dynamic link library for automated testing
__author__ = si wen wei
"""
import os
import copy
import ctypes
from lxml import etree
import enum

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DLL_DIR_NAME = "DLL"
DLL_FILE_NAME = "FsBase.dll"
DLL_PATH = os.path.join(BASE_DIR, DLL_DIR_NAME, DLL_FILE_NAME)
DLL = ctypes.WinDLL(DLL_PATH)


class Channel(object):

    # IsInit = None

    def __init__(self):

        self.id = None

    # def initFsBase(self):

    # DLL.InitFsBase.restype = None
    # return DLL.InitFsBase()

    # def uninitFsBase(self):

    # DLL.InitFsBase.restype = None
    # return DLL.UninitFsBase()

    def open(self, server_addr, app_id, compress, timeout=15):

        # if not self.IsInit:
        # self.IsInit = self.initFsBase()
        timeout = timeout * 1000
        DLL.CreateConnection.restype = ctypes.c_int
        DLL.CreateConnection.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_bool, ctypes.c_int
        ]
        self.id = DLL.CreateConnection(server_addr, app_id, compress, timeout)
        return self.id

    def send(self, data):

        DLL.SendData.restype = ctypes.c_bool
        data = ctypes.create_string_buffer(data)
        data_len = ctypes.sizeof(data)
        return DLL.SendData(ctypes.c_int(self.id), data, ctypes.c_int(data_len))

    def recv(self, buffer_len=64 * 1024, timeout=15):

        timeout = timeout * 1000
        DLL.RecvData.restype = ctypes.c_int
        #DLL.RecvData.argtypes 	= [ctypes.c_int, ctypes.POINTER(ctypes.c_char), ctypes.c_int, ctypes.c_int]

        buffer = ctypes.create_string_buffer(buffer_len)

        recv_data_len = DLL.RecvData(
            ctypes.c_int(self.id), buffer, ctypes.c_int(buffer_len),
            ctypes.c_int(timeout))

        response = buffer.value
        # return copy.deepcopy(response)
        return response

    def close(self):

        DLL.CloseConnection.restype = ctypes.c_void_p
        DLL.CloseConnection.argtypes = [ctypes.c_int]
        if self.id != 0 and self.id:
            DLL.CloseConnection(self.id)
            # if is_release.lower() != "no":
            # if self.IsInit:
            # self.uninitFsBase()
            # self.IsInit = None
            self.id = None  #restore


def initFsBase():
    """Loading environment"""
    DLL.InitFsBase.restype = ctypes.c_void_p
    return DLL.InitFsBase()


def uninitFsBase():
    """Release environment"""
    DLL.InitFsBase.restype = ctypes.c_void_p
    return DLL.UninitFsBase()


def toInt(value, default):

    if not isinstance(value, (int, float)):
        try:
            value = int(value)
        except Exception:
            try:
                value = float(value)
            except Exception:
                value = default
    return value


def toBoolean(value):
    """
	Converts the given item to Boolean true or false. 
	Handles strings `True` and `False` (case-insensitive) as expected, otherwise returns item's truth value using Python's `bool` method.
	"""
    if not isinstance(value, bool):
        if isinstance(value, basestring):
            to_lower = value.lower()
            if to_lower == "true":
                value = True
            elif to_lower == "false":
                value = False
            else:
                value = bool(value)
        else:
            value = bool(value)
    return value


def openChannel(server_addr, app_id, compress, timeout=15):
    """
		Open a server connection, Returns a connection object
	"""
    app_id = int(app_id)
    timeout = toInt(timeout, 15)
    compress = toBoolean(compress)

    channel = Channel()
    id = channel.open(server_addr, app_id, compress, timeout)

    if id == 0:
        error_msg = "connect server(%s) failed" % server_addr
        raise ValueError(error_msg)
    return channel


def sendData(channel, data):

    return channel.send(data)


def recvData(channel, buffer_len=64 * 1024, timeout=15):

    buffer_len = toInt(buffer_len, 64 * 1024)
    timeout = toInt(timeout, 15)
    data = channel.recv(buffer_len, timeout)
    return data


def closeChannel(channel):
    """Close a server connection"""
    if channel.id != 0 and channel.id:
        channel.close()


def clearCacheData(connection, timeout=0):

    all_recv_data = []
    while True:
        res = recvData(connection, timeout=timeout)

        if not res:
            break
        all_recv_data.append(res)
    return all_recv_data

dll_init_flag = 0



class UserBehavior(object):
    online_user_dict = {}
    def __init__(self):
        global dll_init_flag
        if not dll_init_flag:
            dll_init_flag = initFsBase()

    def login(self,username,userpwd,roomname,frontaddress='TCP:192.168.7.185:1089'):
        # 登录前置
        channel = openChannel(frontaddress, 20, True, 15)
        if channel.id:
            login_xml = '<cmd id="30000" ver="1.2"><ClientType val="1"/><TerminalType val="1"/><UserType val="1"/><AppType val="11"/><UserLoginType val="1"/><UserName val="%s"/><ProductName val="FMS002"/><UserPassword val="%s"/><LoginServerAddr val="%s"/></cmd>' % (
                        username, userpwd, frontaddress[len('TCP:'):])
            sendData(channel, login_xml)
            login_resp = recvData(channel)
            tree = etree.fromstring(login_resp)
            LocalUserID = tree.xpath('/cmd[@id="30001"]/LocalUserID')[0].attrib['val']
            get_room_cmd = """<cmd id="30002"><IsGetAllList var="1" /><IsGetRoomDesc val="0" /></cmd>"""
            sendData(channel, get_room_cmd)
            room_list = recvData(channel)
            tree = etree.fromstring(room_list)
            roomnodeid = tree.xpath('/cmd[@id="30003"]/RoomNodeID')[0].attrib['val']
            roomid = tree.xpath(
                '/cmd[@id="30003"]/RoomInfo/Name[@val="%s"]/parent::RoomInfo/RoomID'%(roomname).decode('utf-8'))[0].attrib['val']
            roomappid = tree.xpath(
                '/cmd[@id="30003"]/RoomInfo/Name[@val="%s"]/parent::RoomInfo/RoomAppID'%roomname.decode('utf-8'))[0].attrib['val']
            enter_room = """<cmd id="30004"><RoomNodeID val="%s" /><RoomID val="%s" /><RoomAppID val="%s" /><PreferServer val="" /><PhoneGwDevID val="" /><PhoneGwDevVerifyCode val="" /></cmd>""" % (
                roomnodeid, roomid, roomappid)
            print enter_room
            sendData(channel, enter_room)
            enter_room_resp = recvData(channel)
            print enter_room_resp
            tree = etree.fromstring(enter_room_resp)
            roomsrv_node_id = tree.xpath('/cmd[@id="30005"]/RoomSrvNodeID')[0].attrib['val']
            userid = tree.xpath('/cmd[@id="30005"]/RoomUserID')[0].attrib['val']
            token = tree.xpath('/cmd[@id="30005"]/Token')[0].attrib['val']
            srvadd = tree.xpath('/cmd[@id="30005"]/Server/SrvAddr')[0].attrib['val'].split(';')[0]
            print roomsrv_node_id, userid, token, srvadd

        meetingsrv_channel = openChannel(srvadd,11,True)
        self.meetingsrv_channel = meetingsrv_channel
        if meetingsrv_channel:
            login_room = """<cmd id="6501" ver="1.2"><ClientType val="1" /><TerminalType val="1" /><RoomSrvNodeID val="%s" /><RoomID val="%s" /><UserID val="%s" /><UserName val="%s" /><UserType val="1" /><Token val="%s" /><VerifyMode val="1" /><RoomPassword val="" /><DeviceID val="BFEBFBFF000306A9-7427EA528352" /><LanCode val="1" /><LoginServerAddr val="%s" /><Capability><Mode val="1" /><DownBitrate val="1000000" /></Capability></cmd>""" % (
                roomsrv_node_id, roomid, userid, username, token,srvadd[len("TCP:"):])
            print(login_room.strip())
            sendData(meetingsrv_channel, login_room.strip())
            print(recvData(meetingsrv_channel))
            sendData(meetingsrv_channel, """<cmd id="6517" ver="1.2"/>""")
            resp6602 = recvData(meetingsrv_channel)
            print(resp6602)
            tree = etree.fromstring(resp6602)
            users = tree.xpath('/cmd[@id="6602"]/User')

            for user in users:
                online_userid = user.find('UserID').attrib['val']
                online_username = user.find('Name').attrib['val']
                self.online_user_dict[online_username] = online_userid
            print recvData(meetingsrv_channel, timeout=1)

    def publish_video(self,publish_list):

            for user in self.online_user_dict.keys():
                if user in publish_list:
                    change_user_state = """<cmd id="6509"><UserID val="%s"/><Video><ID val="0"/><State val="2"/></Video></cmd>""" % \
                                        self.online_user_dict[user]
                    sendData(self.meetingsrv_channel, change_user_state)
                    print(recvData(self.meetingsrv_channel,2))
                else:
                    change_user_state = """<cmd id="6509"><UserID val="%s"/><Video><ID val="0"/><State val="0"/></Video></cmd>""" % \
                                        self.online_user_dict[user]
                    sendData(self.meetingsrv_channel, change_user_state)
                    print(recvData(self.meetingsrv_channel,2))


if __name__ == "__main__":

    user = UserBehavior()
    user.login('ttyy09','000000','湖北厅')
    user.publish_video(['ttyy01'])
