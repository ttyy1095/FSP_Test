#!/usr/bin/python
# -*- coding: utf-8 -*-
from ctypes import *
import time
import os.path

dllName = "SessionConnector.so"
dllABSPath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + dllName
dll = cdll.LoadLibrary(dllABSPath)
dll.Init.restype = c_bool
sign=dll.Init()
print "this is {0}".format(sign)

