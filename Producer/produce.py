# coding=utf-8
import json
import os
import struct
import threading
import time
from Queue import Queue
from threading import Lock
from time import sleep

import redis
from google.protobuf.json_format import MessageToJson
from kafka import KafkaConsumer, KafkaProducer

import fsp_common_pb2 as pb_common
import fsp_gc_pb2 as pb_gc
import fsp_sc_pb2 as pb_sc
import fsp_ss_pb2 as pb_ss
import protocol as pbbuf
from protocol_obj import PB_GC
from protocol_obj import PB_SC

import sys,uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Config.config import *


def get_commonInvokeInfo(uuid,invoke_order):
    invokeInfo = pb_common.CommonInvokeInfo(trace_id=uuid,invoke_order=invoke_order)
    return invokeInfo

def get_uuid():
    return uuid.uuid4()

class Produce(object):
    def init(self, kafkaCluster):
        self.lock = Lock()
        self.queue = Queue()
        self.kafkaCluster = kafkaCluster
        self.producer = KafkaProducer(bootstrap_servers=self.kafkaCluster)
        self.r = redis.StrictRedis(host="192.168.7.111", port='6379', db=0)

    def __init__(self):
        pass

    def destroy(self):
        self.producer.close()

    def createMsg(self, messageSequence, response_topic, command_id, msg_body):
        fmt = "!BBqB%dsi" % (len(response_topic))
        msgprefix = struct.pack(fmt, 1, 1, messageSequence, len(response_topic),
                                response_topic, command_id)
        buf = msgprefix + msg_body
        return buf

    def _CreateListenThread(self, messageSequence, listen_module, func, topic):
        """
        监听topic，根据messageSequence来过滤指定方法的消息。
        """
        listenThread = ListenThread(messageSequence, listen_module, func, topic,
                                    self.kafkaCluster, self.lock, self.queue)
        listenThread.daemon = True
        listenThread.start()
        return listenThread

    def _getRspdata(self, lt):
        data_dict = {}
        for i in range(20):
            if not self.queue.empty():
                rspdata = self.queue.get()
                print rspdata
                data_dict = json.loads(rspdata)
                break
            else:
                print('wait for consumer thread')
                time.sleep(1)
        if lt.is_alive():
            lt.stop()
        assert data_dict != {}
        return data_dict

    def CreateGroup(self, messageSequence=1, **msginfo):
        """
        由AS向GC调用
        注意：response_topic应为gc_group_topic,而不是具体的gc

        """

        listenthread = self._CreateListenThread(messageSequence, pb_gc, "CreateGroupRsp",
                                                AS_TOPIC)
        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            msg_body = pb_gc.CreateGroup(**msginfo).SerializeToString()
            buf = self.createMsg(messageSequence, AS_TOPIC,
                                 pb_gc.ProtoDictionary.Value("Enum2CreateGroup"),
                                 msg_body)
            self.producer.send(GC_GROUP_TOPIC, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def GetGroupServers(self, messageSequence=1, **msginfo):
        """
        由AS向GC调用

        注意：response_topic应为gc_group_topic,而不是具体的gc
        group_id, client_ip, user_id,app_id, company_id, room_id, type,
        :param recv_topic:

        :param messageSequence:

        :param group_id: 由AS向GC调用CreatGroup返回

        :param client_ip:

        :param response_topic:

        :return:
        """
        listenthread = self._CreateListenThread(messageSequence, pb_gc,
                                                "GetGroupServersRsp", AS_TOPIC)

        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            msg_body = pb_gc.GetGroupServers(**msginfo).SerializeToString()
            buf = self.createMsg(messageSequence, AS_TOPIC,
                                 pb_gc.ProtoDictionary.Value("Enum2GetGroupServers"),
                                 msg_body)
            self.producer.send(GC_GROUP_TOPIC, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def ClientConnected(self, response_topic, messageSequence=1, **msginfo):
        """
        由GS向SC调用
        注意：response_topic应为sc_group_topic,而不是具体的sc
        :param recv_topic:sc
        :param messageSequence:
        :param client_id:
        :param service_instance_id:
        :param app_id:
        :param client_name:
        :param response_topic: GS
        :return:
        """
        listenthread = self._CreateListenThread(messageSequence, pb_sc,
                                                "ClientConnectedRsp", response_topic)

        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            msg_body = pb_sc.ClientConnected(**msginfo).SerializeToString()
            buf = self.createMsg(messageSequence,response_topic,pb_sc.ProtoDictionary.Value("Enum2ClientConnected"),msg_body)
            self.producer.send(SC_GROUP_TOPIC, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def ClientDisconnected(self, response_topic, messageSequence, **msginfo):
        '''
        由GS向SC调用
        注意：response_topic应为sc_group_topic,而不是具体的sc

        '''
        listenthread = self._CreateListenThread(messageSequence, pb_sc,
                                                "ClientDisconnectedRsp", response_topic)

        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            msg_body = pb_sc.ClientDisconnected(**msginfo).SerializeToString()
            buf = self.createMsg(messageSequence,response_topic,pb_sc.ProtoDictionary.Value("Enum2ClientDisconnected"),msg_body)
            self.producer.send(SC_GROUP_TOPIC, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def CreateStream(self, response_topic, messageSequence, **msginfo):
        """

        :param recv_topic:
        :param messageSequence:
        :param app_id:
        :param stream_type: Video,Audio,DeskTop
        :param stream_property:Reliable,UnReliable
        :param response_topic:
        :return:
        """
        listenthread = self._CreateListenThread(messageSequence, pb_sc, "CreateStreamRsp",
                                                response_topic)
        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            msg_body = pb_sc.CreateStream(**msginfo).SerializeToString()
            buf = self.createMsg(messageSequence,response_topic,pb_sc.ProtoDictionary.Value("Enum2CreateStream"),msg_body)
            self.producer.send(SC_GROUP_TOPIC, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def CheckStreamPublishToken(self, messageSequence, topic_name, stream_id,
                                stream_public_token, response_topic):
        checkstreampublishtoken_buf = pbbuf.CheckStreamPublishToken(
            messageSequence, stream_id, stream_public_token, response_topic)
        self.producer.send(topic_name, checkstreampublishtoken_buf)

    def PublishStream(self, recv_topic, messageSequence, stream_id, client_id, client_ip,
                      uuid, response_topic):
        listenthread = self._CreateListenThread(messageSequence, pb_sc,
                                                "PublishStreamRsp", response_topic)

        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            buf = pbbuf.PublishStream(messageSequence, stream_id, client_id, client_ip,
                                      uuid, response_topic)
            self.producer.send(recv_topic, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def SetStreamSourceServer(self, response_topic, messageSequence=1, **msginfo):
        listenthread = self._CreateListenThread(
            messageSequence, pb_sc, "SetStreamSourceServerRsp", response_topic)

        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            obj = pb_sc.ClientDisconnected(**msginfo)#
            obj.commonInvokeInfo.CopyFrom(get_commonInvokeInfo(get_uuid(), "DFFDFD"))
            msg_body = obj.SerializeToString()
            buf = self.createMsg(messageSequence,response_topic,pb_sc.ProtoDictionary.Value("Enum2ClientDisconnected"),msg_body)

            self.producer.send(SC_GROUP_TOPIC, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def NotifyStreamPublished(self, recv_topic, messageSequence, client_id, stream_id,
                              group_id, user_id, media_id2, media_type, response_topic):
        listenthread = self._CreateListenThread(
            messageSequence, pb_gc, "NotifyStreamPublishedRsp", response_topic)

        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            buf = pbbuf.NotifyStreamPublished(messageSequence, client_id, stream_id,
                                              group_id, user_id, media_id2,
                                              "Enum" + media_type, response_topic)
            self.producer.send(recv_topic, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def GetSuperiorStreamServer(self, recv_topic, messageSequence, stream_id,
                                service_instance_id, uuid, response_topic):
        listenthread = self._CreateListenThread(
            messageSequence, pb_sc, "GetSuperiorStreamServerRsp", response_topic)

        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            buf = pbbuf.GetSuperiorStreamServer(messageSequence, stream_id,
                                                service_instance_id, uuid, response_topic)
            self.producer.send(recv_topic, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def GetStreamServersCP(self, recv_topic, messageSequence, stream_id, client_id,
                           client_ip, group_id, user_id, app_id, company_id, room_id,
                           media_type, response_topic):
        listenthread = self._CreateListenThread(messageSequence, pb_sc,
                                                "GetStreamServersRsp", response_topic)

        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            buf = PB_SC.GetStreamServers(messageSequence, stream_id, client_id, client_ip,
                                         group_id, user_id, app_id, company_id, room_id,
                                         media_type, response_topic)
            self.producer.send(recv_topic, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def ChannelConnected(self, recv_topic, messageSequence, client_id,
                         service_instance_id, stream_id, direction, uuid, response_topic):
        listenthread = self._CreateListenThread(messageSequence, pb_sc,
                                                "ChannelConnectedRsp", response_topic)

        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            channerlconnected_buf = pbbuf.ChannelConnected(
                messageSequence, client_id, service_instance_id, stream_id, direction,
                uuid, response_topic)
        self.producer.send(recv_topic, channerlconnected_buf)

        rspdata = self._getRspdata(listenthread)
        return rspdata

    def StreamSendingStart(self, recv_topic, messageSequence, stream_id, recv_client_id,
                           uuid, response_topic):
        listenthread = self._CreateListenThread(messageSequence, pb_sc,
                                                "StreamSendingStartRsp", response_topic)

        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            buf = pbbuf.StreamSendingStart(messageSequence, stream_id, recv_client_id,
                                           uuid, response_topic)
            self.producer.send(recv_topic, buf)

            rspdata = self._getRspdata(listenthread)
            return rspdata

    def NotifyStreamSendingStart(self, recv_topic, messageSequence, recv_client_id,
                                 stream_id, uuid, response_topic):
        listenthread = self._CreateListenThread(
            messageSequence, pb_gs, "NotifyStreamSendingStartRsp", response_topic)

        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            buf = pbbuf.NotifyStreamSendingStart(messageSequence, recv_client_id,
                                                 stream_id, uuid, response_topic)
        self.producer.send(recv_topic, buf)

        rspdata = self._getRspdata(listenthread)
        return rspdata

    def QueryDB_clientConnected(self, client_id, service_instance_id, app_id):
        sleep(2)
        checkresult1 = False
        query_result = self.r.get('client_proxy:' + client_id)
        print query_result
        if service_instance_id == query_result:
            print "find cp service instance id: %s in db successfully" % service_instance_id
            checkresult1 = True
        else:
            print "fail to find cp service instance id: %s in db " % service_instance_id
            checkresult1 = False
        checkresult2 = False
        query_result = self.r.sismember("clients:" + app_id, client_id)
        print query_result
        if query_result == 1:
            print "find client id: %s in db successfully" % client_id
            checkresult2 = True
        else:
            print "fail to find client id: %s in db " % client_id
            checkresult2 = False
        return (checkresult1 and checkresult2)

    def QueryDB_clientDisconnected(self, client_id, service_instance_id, app_id):
        sleep(2)
        checkresult1 = False
        query_result = self.r.get('client_proxy:' + client_id)
        print query_result
        if service_instance_id == query_result:
            print "find cp service instance id: %s in db successfully" % service_instance_id
            checkresult1 = False
        else:
            print "fail to find cp service instance id: %s in db " % service_instance_id
            checkresult1 = True
        checkresult2 = False
        query_result = self.r.sismember("clients:" + app_id, client_id)
        print query_result
        if query_result:
            print "find client id: %s in db successfully in clients:%s" % (client_id,
                                                                           app_id)
            checkresult2 = False
        else:
            print "fail to find client id: %s in db " % client_id
            checkresult2 = True
        return (checkresult1 and checkresult2)

    def QueryDB_quitGroup(self, client_id, service_instance_id, app_id):
        sleep(2)

        query_result = self.r.get('client_proxy:' + client_id)
        print query_result
        if service_instance_id == query_result:
            print "find cp service instance id: %s in db successfully" % service_instance_id
            checkresult1 = False
        else:
            print "fail to find cp service instance id: %s in db " % service_instance_id
            checkresult1 = True

        query_result = self.r.sismember("clients:" + app_id, client_id)
        print query_result
        if query_result:
            print "find client id: %s in db successfully in clients:%s" % (client_id,
                                                                           app_id)
            checkresult2 = False
        else:
            print "fail to find client id: %s in db " % client_id
            checkresult2 = True
        return (checkresult1 and checkresult2)

    def QueryDB_createStream(self, stream_id, stream_public_token,
                             stream_subscribe_token):
        sleep(2)
        checkdata = self.r.hmget(stream_id, "pub_token", "sub_token")
        return (stream_public_token == checkdata[0]) and (
            stream_subscribe_token == checkdata[1])

    def QueryDB_publishStream(self, stream_id, client_id, client_ip):
        sleep(2)
        checkdata = self.r.hmget(stream_id, "source", "ip")
        return (client_id == checkdata[0]) and (client_ip == checkdata[1])

    def GetStream(self, recv_topic, messageSequence, group_id, user_id, media_type,
                  media_id2, uuid, response_topic):
        """
        media_type: VNC/Audio/Video
        """
        listenthread = self._CreateListenThread(messageSequence, pb_gc, "GetStreamRsp",
                                                response_topic)
        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            buf = PB_GC.GetStream(messageSequence, group_id, user_id, media_type,
                                  media_id2, uuid, response_topic)
            self.producer.send(recv_topic, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def JoinGroup(self, recv_topic, messageSequence, group_id, user_id, group_token,
                  serviceInstanceId, uuid, response_topic):
        listenthread = self._CreateListenThread(messageSequence, pb_gc, "JoinGroupRsp",
                                                response_topic)
        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            buf = pbbuf.JoinGroup_GC(messageSequence, group_id, user_id, group_token,
                                     serviceInstanceId, uuid, response_topic)
            self.producer.send(recv_topic, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def QuitGroup(self, recv_topic, messageSequence, group_id, user_id,
                  service_instance_id, response_topic):
        listenthread = self._CreateListenThread(messageSequence, pb_gc, "QuitGroupRsp",
                                                response_topic)
        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            buf = pbbuf.QuitGroup_GC(messageSequence, group_id, user_id,
                                     service_instance_id, response_topic)
            self.producer.send(recv_topic, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def DestroyGroup(self, recv_topic, messageSequence, group_id, response_topic):
        listenthread = self._CreateListenThread(messageSequence, pb_gc, "DestroyGroupRsp",
                                                response_topic)
        if self.lock.acquire():
            sleep(1)
            self.lock.release()
            buf = pbbuf.DestroyGroup_GC(messageSequence, group_id, response_topic)
            self.producer.send(recv_topic, buf)
            rspdata = self._getRspdata(listenthread)
            return rspdata

    def NotifyPublishStream(self, recv_topic, messageSequence, user_id, media_type,
                            media_id2, stream_id, stream_publish_token, group_id, uuid,
                            response_topic):
        """
        media_type:Audio,Video,VNC
        """
        buf = pbbuf.NotifyPublishStream(messageSequence, user_id, "Enum" + media_type,
                                        media_id2, stream_id, stream_publish_token,
                                        group_id, uuid, response_topic)
        self.producer.send(recv_topic, buf)


class ListenThread(threading.Thread):
    """docstring for ListenThread"""
    startTime = time.time()

    def __init__(self, messageSequence, listen_module, func, topic, kafkaCluster, lock,
                 queue):
        super(ListenThread, self).__init__()
        self.func = func
        self.topic = topic
        self.kafkaCluster = kafkaCluster
        self.lock = lock
        self.stop_event = threading.Event()
        self.queue = queue
        self.messageSequence = messageSequence
        self.listen_module = listen_module
        if self.lock.acquire():
            self.consumer = KafkaConsumer(
                self.topic, bootstrap_servers=self.kafkaCluster, api_version=(0, 10, 1))

            print 'start listen thread {}'.format(os.getpid())
            self.lock.release()

    def stop(self):
        print 'stop listen thread'
        self.stop_event.set()

    def acquireMsg(self, aa):
        if aa[5] == getattr(getattr(self.listen_module, "ProtoDictionary"),
                            "Value")("Enum2" + self.func):
            obj = getattr(self.listen_module, self.func)()
            obj.ParseFromString(aa[6])
            resp = MessageToJson(obj)
            self.queue.put(resp)
            self.stop()

    def run(self):
        super(ListenThread, self).run()

        while True:
            raw_messages = self.consumer.poll(timeout_ms=1000, max_records=5000)
            if self.stop_event.is_set():
                self.consumer.close()
                break
            if len(raw_messages) == 0:
                continue
            if (time.time() - self.startTime) / 1000 > 20:
                print "Wait for mseeage timeout"
                self.stop()
            for topic_partition, message in raw_messages.items():
                buf = message[0].value
                topic_len = struct.unpack("b", buf[10:11])[0]
                fmt = "!bbqb%dsi%ds" % (topic_len, (len(buf) - 15 - topic_len))
                aa = struct.unpack(fmt, buf)
                print aa
                if aa[2] != self.messageSequence:
                    continue

                self.acquireMsg(aa)


if __name__ == '__main__':

    a = Produce()
    a.init("192.168.7.111:9092")
    # resp = a.QuitGroup("gc_group_01", 1, "{1603554c-f1ad-42b6-9826-acdfaffb810f}", "1430000", "gs2", "gs2")
    # a.DestroyGroup("gc_group_01",2,"{1603554c-f1ad-42b6-9826-acdfaffb810f}","gs2")
    # resp = a.JoinGroup("gc_group_01",2,"{1111111111111}",1234455)
    # user_id = "1430000"
    # media_type = config.MediaType.EnumAudio.value
    msg_body = pb_gc.CreateGroup(
        service_type=0, room_id='80664', app_id='app_hj',
        company_id='43150').SerializeToString()

    print msg_body
    resp = a.CreateGroup(
        app_id='app_hj',
        service_type=0,
        room_id='80664',
        company_id='43150',
    )
    groupid = resp['group']['groupId']
    # resp = a.GetStream('gc_group_01', 2, groupid, user_id,
    #                    config.MediaType.EnumAudio.value, '0', "{}", 'gs2')
    # print resp
    # client_id = "%s;%s" % (groupid, user_id)
    # resp = a.GetStreamServersCP(
    #     "sc_group_01",
    #     3,
    #     "cb5e8dd0-7c7a-4296-b4af-ea9bba10ddcc",
    #     client_id,
    #     "192.168.6.65",
    #     groupid,
    #     user_id,
    #     app_id='1',
    #     company_id='43100',
    #     room_id='107894',
    #     media_type=media_type,
    #     response_topic='gs2')
    # print resp
    # gs = a.GetGroupServers('gc_group_01',2,groupid,'192.168.5.168',"1430000","app2","107893","40100",'lizzietest')

    # print gs
    # print a.ClientConnected('sc_group_01',1,groupid+';client_id','gs4','app_clientconnected','gs4','gs3')
    #streamid = a.CreateStream('sc_group_01',2,'1122',0,1,'sp_instance_01')
    #print streamid
    #print a.ChannelConnected('sc_group_01',3,'gs2','ss2',streamid,'Receiving','ss2')
    # pass
    # obj = pb_gc.DestroyGroup(group_id="12344")
    #
    # obj_msg = obj.SerializeToString()
    # print obj_msg
