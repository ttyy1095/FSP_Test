#-*-coding:utf-8-*-
import _winreg
from lxml import etree
xml = """<?xml version="1.0" encoding="UTF-8" ?>
<root>
    <GroupName>Fastonz</GroupName>
    <ProductName>FMDesktop</ProductName>
    <Version>03.15.05.33</Version>
    <ProductSeries>1</ProductSeries>
    <ProductID>FMS002</ProductID>
    <ClientType>1</ClientType>
    <TerminalType>1</TerminalType>
    <ClientMode>1</ClientMode>
    <DownloadBitrate>1000000</DownloadBitrate>
    <FrontSrvAppID>20</FrontSrvAppID>
    <RoomAppID>11</RoomAppID>
    <EntranceSrvAppID>8</EntranceSrvAppID>
    <!--音视频参数定义-->
    <MaxFrameRate>30</MaxFrameRate>
    <MaxVideoWidth>1920</MaxVideoWidth>
    <MaxVideoHeight>1080</MaxVideoHeight>
    <MaxVideoBitrate>3000</MaxVideoBitrate>
    <MaxMediaBitrate>3000</MaxMediaBitrate>
    <CameraVerticalMode>0</CameraVerticalMode>
    <OverlayNameOnLocalVideo>0</OverlayNameOnLocalVideo>
    <OverlayNameOnRemoteVideo>1</OverlayNameOnRemoteVideo>
    <ShowUserListTree>1</ShowUserListTree>
    <!--功能开关-->
    <SupportDualMode>1</SupportDualMode>
    <SupportMultiVideoChannel>1</SupportMultiVideoChannel>
    <SupportScreenDevice>1</SupportScreenDevice>
    <EnableAudio>1</EnableAudio>
    <EnableVideo>1</EnableVideo>
    <EnableWB>1</EnableWB>
    <EnableWEB>0</EnableWEB>
    <EnableVNC>1</EnableVNC>
    <EnableMedia>1</EnableMedia>
    <EnableChat>1</EnableChat>
    <EnableFile>1</EnableFile>
    <EnableVote>1</EnableVote>
    <ClientEdition>1</ClientEdition>
    <!--窗口模式-->
    <InitWndMode>1</InitWndMode>
    <InitWndVideoRelayID>0</InitWndVideoRelayID>
    <InitWndDataActive>1</InitWndDataActive>
    <MaxVideoSplitCount>25</MaxVideoSplitCount>
    <AdConfig>https://ws.haoshitong.com/ClientAD/ADConfig.xml</AdConfig>
    <DefaultServerList>
        <Server>a.haoshitong.com</Server>
    </DefaultServerList>
    <AppCustomParam>
        <Param Name="EnableRoomLink" Value="1" />
        <Param Name="UserDataDirName" Value="\Inpor\Send\" />
    </AppCustomParam>
</root>
"""

root = etree.fromstring(xml)
# print  etree.tostring(root)

element = root.xpath('AppCustomParam/Param[@Name="UserDataDirName"]')
print len(element)
print type(element)
print element
element[0].set("Value", "\\Inpor\\%s\\" % "11223")
print etree.tostring(root)
etree.ElementTree(root).write("ppp.xml",pretty_print=True)