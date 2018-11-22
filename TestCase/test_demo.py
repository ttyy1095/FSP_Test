#-*-coding:utf-8-*-
import time
import logging
import pytest
logging.basicConfig(level=logging.DEBUG)

def test_1():
    log = logging.getLogger('test_1')
    time.sleep(1)
    log.debug('after 1 sec')
    time.sleep(1)
    log.debug('after 2 sec')
    time.sleep(1)
    log.debug('after 3 sec')
    assert 1, 'should pass'


def test_2():
    log = logging.getLogger('test_2')
    time.sleep(1)
    log.debug('after 1 sec')
    time.sleep(1)
    log.debug('after 2 sec')
    time.sleep(1)
    log.debug('after 3 sec')
    assert 0, 'failing for demo purposes'

if __name__ == '__main__':
    pytest.main('-q test_demo.py --capture=no')