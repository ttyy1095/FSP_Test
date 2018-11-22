#-*-coding:utf-8-*-

import os,time

rq = time.strftime('%Y-%m-%d', time.localtime(time.time()))
result_path = os.path.join(os.getcwd(),"result",rq)
print result_path
if not os.path.exists(result_path):
    os.mkdir(result_path)
os.system("py.test -q test_demo.py --alluredir %s"%result_path)
os.system("allure generate ./result/%s/ -o ./report/%s/"%(rq,rq))
os.system("allure open -h 127.0.0.1 -p 8083 ./report/%s/"%rq)