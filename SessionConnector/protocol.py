import time
from Main_class_dll import Main_class_dll
a = Main_class_dll()
a.int_create_()
session_id = a.connect("192.168.7.72", "50003", 1)
time.sleep(2)
print a.dllName
rsp =  a.loginCP(session_id, "{953c1afd-f0d7-4ab3-af45-9dd7ec1809e9}", "2251", "1422200")
print a.session_id
print rsp