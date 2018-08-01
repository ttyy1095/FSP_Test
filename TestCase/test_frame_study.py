#coding=utf-8
import pytest
import allure

def setup_module():
    print "setup module"
def setup_function():
    """  每个函数都会调用  """
    print "setup function"
class TestGC():
    @allure.title("title")
    @allure.step("创建群组")
    def test_createGroup(self):
        # print "创建群组"
        i = 1
        assert 1 == i

pss = [1,2,3]

class TestParams():
    @pytest.fixture(scope="session",params=pss)
    def ps(self,request):
        return request.param

    def test_is_0(self,ps):
        assert ps != 0


class TestParametrize():

    @pytest.mark.parametrize("test_input,expected",[("3+5",8),("2+4",6),("5+6",10)])
    def test_eval(self,test_input,expected):
        assert eval(test_input) == expected

# @pytest.mark.parametrize

from datetime import datetime, timedelta

testdata = [
    (datetime(2001, 12, 12), datetime(2001, 12, 11), timedelta(1)),
    (datetime(2001, 12, 11), datetime(2001, 12, 12), timedelta(-1)),
]
@pytest.mark.parametrize("a,b,expected", testdata, ids=["forward", "backward"])
def test_timedistance_v1(a, b, expected):
    diff = a - b
    assert diff == expected
