#-*-coding:utf-8-*-
import socket
import os
from lxml import etree

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('114.114.114.114', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip



# def choose_server_by_ip(use_specialline=False,**assign_server):
#     """
#     修改配置文件，使客户端能登录到指定服务器上
#     :param service_type:
#     :param group_name:
#     :param use_specialline:
#     :return:
#     """
#     testdata_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'TestData')
#     default_conf = os.path.join(testdata_path,'rule-config_Transnational.xml')
#     tree = etree.parse(default_conf)
#
#     r = tree.xpath('//IPRuleSet')[0]
#     r.clear()
#     for service_type,group_name in assign_server.items():
#
#         iprule = etree.Element('IPRule', {"serverType": service_type})
#         ip = etree.Element('IP')
#         ip.text = get_host_ip()
#         groupname = etree.Element("GroupName")
#         groupname.text = group_name
#         iprule.append(ip)
#         iprule.append(groupname)
#         r.append(iprule)
#     if use_specialline:
#         ValueOfUseSpecialLineConfig = tree.find('//TransnationalConfig/ValueOfUseSpecialLineConfig')
#         ValueOfUseSpecialLineConfig.text = '0.01'
#     xml_str =  etree.tostring(tree,encoding="utf-8",pretty_print=True)
#     xml_path = os.path.join(testdata_path,'rule-config_temp.xml')
#     with open(xml_path,'w') as f:
#         f.write(xml_str)

def use_specialline(use_specialline):
    testdata_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'TestData')
    default_conf = os.path.join(testdata_path,'rule-config_Transnational.xml')
    tree = etree.parse(default_conf)
    ValueOfUseSpecialLineConfig = tree.find('//TransnationalConfig/ValueOfUseSpecialLineConfig')
    if use_specialline:
        ValueOfUseSpecialLineConfig.text = '0.01'
    else:
        ValueOfUseSpecialLineConfig.text = '500'

    xml_str =  etree.tostring(tree,encoding="utf-8",pretty_print=True)
    with open(default_conf,'w') as f:
        f.write(xml_str)