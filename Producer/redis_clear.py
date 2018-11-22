#coding=utf-8
import redis
import re

r = redis.StrictRedis(host="192.168.7.111", port='6379', db=0)

#清空流ID，组ID
# keys = r.keys()
# find = re.compile('[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}')
# for key in keys:
#     if ('{' in key) and ("}" in key):
#         r.delete(key)
#
#     if len(find.findall(key)) > 0:
#          r.delete(key)

print r.smembers('group_servers')
print r.hget('gs1','ip')
print type(r.hget('gs1','upload_speed'))