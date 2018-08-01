from locust import HttpLocust,TaskSet,task
from ctypes import *
import time
import os.path

class UserBehavior(TaskSet):
#class Test():
	dllName = "SessionConnector.dll"
	dllPath = "C:\\Python27\\Lib\\site-packages\\SessionConnector\\SessionConnector.dll"
	dll = cdll.LoadLibrary(dllPath)
	session_id=''
	judeInit=False
	
	def int_create_(self):
		self.dll.Init.restype = c_bool
		if self.judeInit == False:
			sign = self.dll.Init()
			self.judeInit = True
		else:
			pass
	
#	def Do_work_connector(self,ip,port,app_id):
	def Do_work_connector(self):
		#self.dll.CreateSession.argtypes=[c_char_p,c_char_p,c_int]
		self.dll.CreateSession.restype = c_int
		self.session_id = self.dll.CreateSession('192.168.7.153','1089',1)
		return self.session_id
		
	@task
	def test(self):
		self.int_create_()
		self.Do_work_connector()
		
class WebsiteUser(HttpLocust):
	host = '192.168.7.153:1089'
	task_set = UserBehavior
	min_wait = 2000
	max_wait = 4000
		
"""	def Do_work_send_recv(self,buf,session_id):
		time.sleep(2)
		self.session_id = session_id
		self.dll.SendSessionMsg.restype = c_bool
		self.dll.SendSessionMsg.argtypes = [c_int,c_char_p,c_uint]
		ret = self.dll.SendSessionMsg(self.session_id,buf,len(buf)+1)
		self.dll.RecvSessionMsg.argtypes = [c_int,c_char_p,c_uint,cint]
		self.dll.RecvSessionMsg.restype = c_bool
		recv_buf = create_string_buffer(1024)
		ret = self.dll.RecvSessionMsg(self.session_id,recv_buf,1024,3000)
		
		self.dll.DestroySession.restype = c_bool;
		ret = self.dll.DestroySession(self.session_id)
		
		return recv_buf.values
		
	def Close_Session_id(self,session_id):
		self.session_id = session_id
		self.dll.MainSessionClosed.argtypes = [c_int]
		self.dll.MainSessionClosed.restype = None
		self.dll.MainSessionClosed(self.session_id)
		
	def Close_Session(self):
		self.dll.MainSessionClosed.argtypes = [c_int]
		self.dll.MainSessionClosed.restype = None
		self.dll.MainSessionClosed(self.session_id)
		
if __name__ == '__main__':
	a=Test()
	a.int_create_()
	b=a.Do_work_connector("192.168.7.153","1089",1)
	print "b is :",b    """
	
	
		
	
		
	
		
