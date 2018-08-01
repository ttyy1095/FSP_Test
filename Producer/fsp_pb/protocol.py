# coding=utf-8
# 本脚本用于构造protobuf数据
import struct

import fsp_common_pb2 as pb_common
import fsp_gc_pb2 as pb_gc
import fsp_gs_pb2 as pb_gs
import fsp_sc_pb2 as pb_sc
import fsp_ss_pb2 as pb_ss


def createMsg(messageSequence, command_id, msg_body, response_topic):
    fmt = "!BBqB%dsi" % (len(response_topic))
    msgprefix = struct.pack(fmt, 1, 1, messageSequence, len(response_topic),
                            response_topic, command_id)
    buf = msgprefix + msg_body
    return buf


def getCommonInvokeInfo(uuid, invoke_order):
    invokeInfo = pb_common.CommonInvokeInfo()
    invokeInfo.trace_id = uuid
    invokeInfo.invoke_order = invoke_order
    return invokeInfo


def CreateGroup(messageSequence, app_id, service_type, room_id,
                response_topic):
    """
    功能：
    参数：
    """
    creategroup = pb_gc.CreateGroup()
    creategroup.app_id = app_id
    creategroup.service_type = service_type
    creategroup.room_id = room_id

    msg_body = creategroup.SerializeToString()
    command_id = pb_gc.ProtoDictionary.Value("Enum2CreateGroup")
    return createMsg(messageSequence, command_id, msg_body, response_topic)


def GetGroupServers(messageSequence, group_id, client_ip, response_topic):
    getgroupserver = pb_gc.GetGroupServers()
    getgroupserver.group_id = group_id
    getgroupserver.client_ip = client_ip

    msg_body = getgroupserver.SerializeToString()
    command_id = pb_gc.ProtoDictionary.Value("Enum2GetGroupServers")
    return createMsg(messageSequence, command_id, msg_body, response_topic)


def ClientConnected(messageSequence, client_id, service_instance_id, app_id,
                    client_name, uuid, response_topic):
    clientconnected = pb_sc.ClientConnected()
    clientconnected.client_id = client_id
    clientconnected.service_instance_id = service_instance_id
    clientconnected.app_id = app_id
    clientconnected.client_name = client_name

    clientconnected.commonInvokeInfo.CopyFrom(getCommonInvokeInfo(uuid, "DFD"))
    msg_body = clientconnected.SerializeToString()
    command_id = pb_sc.ProtoDictionary.Value('Enum2ClientConnected')
    return createMsg(messageSequence, command_id, msg_body, response_topic)


def ClientDisconnected(messageSequence, client_id, service_instance_id,
                       response_topic):
    clientdisconnected = pb_sc.ClientDisconnected()
    clientdisconnected.client_id = client_id
    clientdisconnected.service_instance_id = service_instance_id
    msg_body = clientdisconnected.SerializeToString()
    command_id = pb_sc.ProtoDictionary.Value('Enum2ClientDisconnected')
    return createMsg(messageSequence, command_id, msg_body, response_topic)


def GetStream(messageSequence, group_id, user_id, media_type, media_id2, uuid,
              response_topic):
    obj = pb_gc.GetStream()
    obj.group_id = group_id
    obj.user_id = user_id
    obj.media_type = pb_common.MediaType.Value(media_type)
    obj.commonInvokeInfo.CopyFrom(getCommonInvokeInfo(uuid, "DF"))
    obj.media_id2 = media_id2
    msg_body = obj.SerializeToString()

    command_id = pb_gc.ProtoDictionary.Value("Enum2GetStream")
    return createMsg(messageSequence, command_id, msg_body, response_topic)


def CreateStream(messageSequence, app_id, stream_type, stream_property, uuid,
                 response_topic):
    creamstream = pb_sc.CreateStream()
    creamstream.app_id = app_id
    creamstream.stream_type = pb_common.StreamType.Value(stream_type)
    creamstream.stream_property = pb_common.StreamProperty.Value(
        stream_property)

    creamstream.commonInvokeInfo.CopyFrom(getCommonInvokeInfo(uuid, "DFF"))

    msg_body = creamstream.SerializeToString()
    command_id = pb_sc.ProtoDictionary.Value('Enum2CreateStream')

    return createMsg(messageSequence, command_id, msg_body, response_topic)


def CheckStreamPublishToken(messageSequence, stream_id, stream_public_token,
                            response_topic):
    checkstreampublishtoken = pb_sc.CheckStreamPublishToken()
    checkstreampublishtoken.stream_id = stream_id
    checkstreampublishtoken.stream_public_token = stream_public_token
    msg_body = checkstreampublishtoken.SerializeToString()
    command_id = pb_sc.ProtoDictionary.Value('Enum2CheckStreamPublishToken')

    return createMsg(messageSequence, command_id, msg_body, response_topic)


def PublishStream(messageSequence, stream_id, client_id, client_ip, uuid,
                  response_topic):
    publishstreamcp = pb_sc.PublishStream()
    publishstreamcp.stream_id = stream_id
    publishstreamcp.client_id = client_id
    publishstreamcp.client_ip = client_ip

    publishstreamcp.commonInvokeInfo.CopyFrom(
        getCommonInvokeInfo(uuid, "DFFDF"))

    msg_body = publishstreamcp.SerializeToString()
    command_id = pb_sc.ProtoDictionary.Value('Enum2PublishStream')

    return createMsg(messageSequence, command_id, msg_body, response_topic)


def SetStreamSourceServer(messageSequence, stream_id, service_instance_id,
                          uuid, response_topic):
    obj = pb_sc.SetStreamSourceServer()
    obj.stream_id = stream_id
    obj.service_instance_id = service_instance_id

    obj.commonInvokeInfo.CopyFrom(getCommonInvokeInfo(uuid, "DFFDFD"))
    msg_body = obj.SerializeToString()
    command_id = pb_sc.ProtoDictionary.Value("Enum2SetStreamSourceServer")
    return createMsg(messageSequence, command_id, msg_body, response_topic)


def GetStreamServersCP(messageSequence, stream_id, client_id, client_ip,
                       exception_servers, response_topic):
    getstreamserverscp = pb_sc.GetStreamServers()
    getstreamserverscp.stream_id = stream_id
    getstreamserverscp.client_id = client_id
    getstreamserverscp.client_ip = client_ip
    for i in exception_servers:
        getstreamserverscp.exception_servers.append(i)

    msg_body = getstreamserverscp.SerializeToString()
    command_id = pb_sc.ProtoDictionary.Value('Enum2GetStreamServers')

    return createMsg(messageSequence, command_id, msg_body, response_topic)


def ChannelConnected(messageSequence, client_id, service_instance_id,
                     stream_id, direction, uuid, response_topic):
    channerlconnected = pb_sc.ChannelConnected()
    channerlconnected.client_id = client_id
    channerlconnected.service_instance_id = service_instance_id
    channerlconnected.stream_id = stream_id
    channerlconnected.direction = pb_common.DataDirection.Value(direction)
    channerlconnected.commonInvokeInfo.CopyFrom(
        getCommonInvokeInfo(uuid, "DFDDF"))

    msg_body = channerlconnected.SerializeToString()
    command_id = pb_sc.ProtoDictionary.Value('Enum2ChannelConnected')

    return createMsg(messageSequence, command_id, msg_body, response_topic)


def JoinGroup_GC(messageSequence, group_id, user_id, group_token,
                 serviceInstanceId, uuid, response_topic):
    """
    """
    obj = pb_gc.JoinGroup()
    obj.group_id = group_id
    obj.group_token = group_token
    obj.user_id = user_id
    obj.service_instance_id = serviceInstanceId
    obj.client_id = "%s;%s" % (group_id, user_id)
    obj.commonInvokeInfo.CopyFrom(getCommonInvokeInfo(uuid, "DF"))
    obj_msg = obj.SerializeToString()
    command_id = pb_gc.ProtoDictionary.Value("Enum2JoinGroup")

    return createMsg(messageSequence, command_id, obj_msg, response_topic)


def QuitGroup_GC(messageSequence, group_id, user_id, service_instance_id,
                 response_topic):
    """
    """
    obj = pb_gc.QuitGroup()
    obj.group_id = group_id
    obj.user_id = user_id
    obj.service_instance_id = service_instance_id
    obj.client_id = "%s;%s" % (group_id, user_id)

    obj_msg = obj.SerializeToString()
    command_id = pb_gc.ProtoDictionary.Value("Enum2QuitGroup")

    return createMsg(messageSequence, command_id, obj_msg, response_topic)


def DestroyGroup_GC(messageSequence, group_id, response_topic):
    """
    """
    obj = pb_gc.DestroyGroup()
    obj.group_id = group_id

    obj_msg = obj.SerializeToString()
    command_id = pb_gc.ProtoDictionary.Value("Enum2DestroyGroup")

    return createMsg(messageSequence, command_id, obj_msg, response_topic)


def NotifyPublishStream(messageSequence, user_id, media_type, media_id2,
                        stream_id, stream_publish_token, group_id, uuid,
                        response_topic):
    obj = pb_gs.NotifyPublishStream()
    obj.stream_id = stream_id
    obj.stream_publish_token = stream_publish_token
    obj.group_id = group_id
    obj.user_id = user_id
    obj.media_type = pb_common.MediaType.Value(media_type)

    obj.commonInvokeInfo.CopyFrom(getCommonInvokeInfo(uuid, "DFFD"))

    obj.media_id2 = media_id2
    obj_msg = obj.SerializeToString()
    command_id = pb_gs.ProtoDictionary.Value("Enum2NotifyPublishStream")

    return createMsg(messageSequence, command_id, obj_msg, response_topic)

def NotifyStreamPublished(messageSequence, client_id, stream_id, group_id,
                            user_id, media_id2, media_type, response_topic):
    obj = pb_gc.NotifyStreamPublished()
    obj.client_id = client_id
    obj.stream_id = stream_id
    obj.group_id = group_id
    obj.user_id = user_id
    obj.media_id2 = media_id2
    obj.media_type = pb_common.MediaType.Value(media_type)

    msg_body = obj.SerializeToString()
    command_id = pb_gc.ProtoDictionary.Value("Enum2NotifyStreamPublished")
    return createMsg(messageSequence, command_id, msg_body, response_topic)

def GetSuperiorStreamServer(messageSequence, stream_id,
                            service_instance_id, uuid, response_topic):
    obj = pb_sc.GetSuperiorStreamServer()
    obj.stream_id = stream_id
    obj.service_instance_id = service_instance_id
    obj.commonInvokeInfo.CopyFrom(getCommonInvokeInfo(uuid, "DFD"))

    msg_body = obj.SerializeToString()
    command_id = pb_sc.ProtoDictionary.Value(
        "Enum2GetSuperiorStreamServer")

    return createMsg(messageSequence, command_id, msg_body, response_topic)

def Login():
    obj = pb_ss.LoginReceivingChannel()
    obj.stream_id = stream_id

def StreamSendingStart(messageSequence, stream_id, recv_client_id, uuid,
                        response_topic):
    obj = pb_sc.StreamSendingStart()
    obj.stream_id = stream_id
    obj.recv_client_id = recv_client_id
    obj.commonInvokeInfo.CopyFrom(getCommonInvokeInfo(uuid, "DFDDD"))

    msg_body = obj.SerializeToString()
    command_id = pb_sc.ProtoDictionary.Value("Enum2StreamSendingStart")
    return createMsg(messageSequence, command_id, msg_body, response_topic)

def NotifyStreamSendingStart(messageSequence, recv_client_id, stream_id,
                                uuid, response_topic):
    obj = pb_ss.NotifyStreamSendingStart()
    obj.recv_client_id = recv_client_id
    obj.stream_id = stream_id

    obj.commonInvokeInfo.CopyFrom(getCommonInvokeInfo(uuid, "DFDDDF"))
    msg_body = obj.SerializeToString()
    command_id = pb_ss.ProtoDictionary.Value(
        "Enum2NotifyStreamSendingStart")
    return createMsg(messageSequence, command_id, msg_body, response_topic)

