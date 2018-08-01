# -*- coding: utf-8 -*-
import os
import sys
import time
import struct
import platform
from ctypes import *
import Producer.fsp_pb.fsp_ss_pb2 as pb_ss
import Producer.fsp_pb.fsp_common_pb2 as pb_common
'''
bool Init();
int  CreateSession(char* ip, char* port, unsigned int appid);
bool SendSessionMsg(int session_id, const char* msg, unsigned int msg_len);
bool RecvSessionMsg(int session_id, char* msg, unsigned int msg_size, int time_out);
void CloseSession(int Session_id);
'''

system = platform.system()
if system == "Linux":
    dllName = "libSessionConnector.so"
elif system == "Windows":
    dllName = "SessionConnector.dll"
else:
    sys.exit("Sorry, platform {0} was not support yet".format(system))

class Main_class_dll():

    dllName = "libSessionConnector.so"
    dllABSPath = os.path.dirname(
        os.path.abspath(__file__)) + os.path.sep + dllName

    dll = cdll.LoadLibrary(dllABSPath)

    dllhandle = dll._handle
    print dllhandle
    judeInit = False

    def __init__(self):
        pass
    def __del__(self):
        global system
        if system == "Windows":
            import win32api
            win32api.FreeLibrary(self.dllhandle)
    def int_create_(self):

        if self.judeInit == False:
            self.dll.Init.restype = c_bool
            sign = self.dll.Init()
            return sign


#              self.judeInit=True
        else:
            print "dll has been Init"

    def connect(self, ip, port, appid):
        self.dll.CreateSession.argtypes = [c_char_p, c_char_p, c_uint]
        self.dll.CreateSession.restype = c_int
        self.session_id = self.dll.CreateSession(ip, port, appid)
        return self.session_id

    def send_recv(self, buf, session_id):
        time.sleep(2)
        self.session_id = session_id
        self.dll.SendSessionMsg.restype = c_bool
        self.dll.SendSessionMsg.argtypes = [c_int, c_char_p, c_uint]
        ret = self.dll.SendSessionMsg(self.session_id, buf, len(buf) + 1)
        time.sleep(2)
        self.dll.RecvSessionMsg.argtypes = [c_int, c_char_p, c_uint, c_int]
        self.dll.RecvSessionMsg.restype = c_bool
        recv_buf = create_string_buffer(1024)
        ret = self.dll.RecvSessionMsg(self.session_id, recv_buf, 1024, 3000)
        #       time.sleep(2)
        #       self.dll.CloseSession.restype = c_bool
        #       ret = self.dll.CloseSession(self.session_id)

        return recv_buf.value

    def Close_Session(self, session_id):
        self.session_id = session_id
        self.dll.MainSessionClosed.argtypes = [c_int]
        self.dll.MainSessionClosed.restype = None
        self.dll.MainSessionClosed(self.session_id)

    def test(self):
        dllName = "libSessionConnector.so"
        dllABSPath = os.path.dirname(
            os.path.abspath(__file__)) + os.path.sep + dllName
        return dllABSPath

    def OC_login_CP(self, session_id, group_id, group_token, user_id):
        buf = '<cmd id="8701"><Guid val="{}" /><CheckCode val="{}" /><FrontUserID val="{}" /></cmd>'.format(
            group_id, group_token, user_id)
        print buf
        return self.send_recv(buf, session_id)

    def NC_login_CP(self, session_id, group_id, group_token, user_id):
        buf = '<cmd id="8701"><Guid val="{}" /><CheckCode val="{}" /><FrontUserID val="{}" /><ClientVersion val="nc" /></cmd>'.format(
            group_id, group_token, user_id)
        print buf
        return self.send_recv(buf, session_id)

    def oc_recvreq_cp(self, session_id, group_id, recv, media_type, media_id,
                      frontUserId, srcUserId):
        """
        ''recv''    是否接收，0-停止接收，1-接收

        ''media_type''  媒体类型，1-音频数据，2-视频数据

        """
        buf = '<cmd id="8703"><Guid val="{}" /><Recv val="{}" /><MediaType val="{}" /><MediaID val="{}" /><FrontUserID val="{}" /><SrcUserID val="{}" /></cmd>'.format(
            group_id, recv, media_type, media_id, frontUserId, srcUserId)
        print buf
        return self.send_recv(buf, session_id)
    def LoginRecevingChannel(self, stream_id, stream_subscribe_token, client_token, uuid):
        obj = pb_ss.LoginReceivingChannel()
        obj.stream_id = stream_id
        obj.stream_subscribe_token = stream_subscribe_token
        obj.client_token = client_token
        invokeInfo = pb_common.CommonInvokeInfo()
        invokeInfo.trace_id = uuid
        invokeInfo.invoke_order = "DFDD"
        obj.commonInvokeInfo.CopyFrom(invokeInfo)
        msg_body = obj.SerializeToString()
        command_id = pb_ss.ProtoDictionary.Value("Enum2LoginReceivingChannel")
        # fmt = "!LBL"
        # msgprefix = struct.pack(fmt, 6563651, 3, command_id)
        fmt = "!L"
        msgprefix = struct.pack(fmt , command_id)
        buf = msg_body
        print buf
        f = open("buf", "wb")
        f.write(buf)
        f.close()
        return buf

if __name__ == '__main__':

    a = Main_class_dll()
    
    a.int_create_()
    session_id = a.connect("192.168.7.105", "50003", 1)
    print session_id
    time.sleep(0.010)
    # buf = a.LoginRecevingChannel("05d56423-5d80-43ad-95e1-bc66f10732c1","","gs2","{ca784686-3cbe-d70f-e7cc-ae9b4ddd7ed7}")
    # rsp = a.send_recv(buf,session_id)
    rsp =  a.OC_login_CP(session_id, "{0add0d33-ece9-4975-b186-afad3365bc02}", "5219", "1422200")
    print rsp

    pass
