#-*-coding:utf-8-*-

import pytest
import allure
import paramiko
import os,sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from  Producer.produce import Produce
from Config import config
@pytest.fixture(scope="session")
def producer():
    print "create producer"
    producer = Produce()
    producer.init(config.kafkaCluster)
    yield producer
    print "destroy producer"
    producer.destroy()

@pytest.fixture(scope="session")
def sftp():
    print "create sftp"
    transport = paramiko.Transport(config.rule_server)
    transport.connect(username="root",password="123456")
    sftp = paramiko.SFTPClient.from_transport(transport)
    yield sftp
    print "close sftp"
    sftp.close()
    transport.close()

