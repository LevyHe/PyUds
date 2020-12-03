# -*- coding: utf-8 -*-
"""
Created on Sat Mar  20 10:51:35 2019

@author: levy.he
"""
import ctypes
import time
from . import vxlapy
from . import vxlbase
from ...can import Message


# List of valid data lengths for a CAN FD message
CAN_FD_DLC = [
    0, 1, 2, 3, 4, 5, 6, 7, 8,
    12, 16, 20, 24, 32, 48, 64
]


class VectorError(IOError):

    def __init__(self, error_code, error_string, function):
        self.error_code = error_code
        text = "%s failed (%s)" % (function, error_string)
        super(VectorError, self).__init__(text)


def len2dlc(length):
    """Calculate the DLC from data length.

    :param int length: Length in number of bytes (0-64)

    :returns: DLC (0-15)
    :rtype: int
    """
    if length <= 8:
        return length
    for dlc, nof_bytes in enumerate(CAN_FD_DLC):
        if nof_bytes >= length:
            return dlc
    return 15


def dlc2len(dlc):
    """Calculate the data length from DLC.

    :param int dlc: DLC (0-15)

    :returns: Data length in number of bytes (0-64)
    :rtype: int
    """
    return CAN_FD_DLC[dlc] if dlc <= 15 else 64


class CanBus(vxlbase.VxlBase):
    def __init__(self, channel=0, app_name="CANalyzer", can_filters=None, poll_interval=0.01,
                 bitrate=500000, rx_queue_size=2 ** 14, **config):
        super(CanBus, self).__init__()
        self.xlInterfaceVersion = vxlapy.XL_INTERFACE_VERSION_V3
        self.channel = channel
        self.poll_interval = poll_interval
        self.rx_queue_size = rx_queue_size
        self.bitrate = bitrate
        self._app_name = app_name
        self.channel_info = '%s:CAN %d' % (app_name, self.channel + 1)
        self.bus_type = vxlapy.XL_BUS_TYPE_CAN
        self.channelIdx = self.getchannelIdx()
        self.getChannelMask()
        self.openPort()
        offset = vxlapy.XLuint64()
        self.api.xlGetSyncTime(self.portHandle, offset)
        self.bus_start_time = time.time()
        self._time_offset = self.bus_start_time - offset.value * 1e-9
        self.event_handle = vxlapy.XLhandle()
        self.api.xlSetNotification(
            self.portHandle, ctypes.byref(self.event_handle), 1)
        self._start = True

    def getchannelIdx(self):
        return super(CanBus, self).getchannelIdx(self.channel, self._app_name, self.bus_type)

    def getChannelMask(self):
        return super(CanBus, self).getChannelMask(self.bus_type, self.channelIdx,
            self.xlInterfaceVersion)
    def activateChannel(self):
        return super(CanBus, self).activateChannel(self.bus_type)

    def deactivateChannel(self):
        return super(CanBus, self).deactivateChannel()

    def openPort(self):
        super(CanBus, self).openPort(busType=self.bus_type, userName=self._app_name, rxQueueSize=self.rx_queue_size, xlInterfaceVersion=self.xlInterfaceVersion)
        if self.initAccess:
            self.api.xlCanSetChannelBitrate(
                self.portHandle, self.accessMask, self.bitrate)
        self.activateChannel()

    def start(self):
        if not self._start:
            super(CanBus, self).__init__()
            self.xlInterfaceVersion = vxlapy.XL_INTERFACE_VERSION_V3
            self.channelIdx = self.getchannelIdx()
            self.getChannelMask()
            self.openPort()
            offset = vxlapy.XLuint64()
            self.api.xlGetSyncTime(self.portHandle, offset)
            self.bus_start_time = time.time()
            self._time_offset = self.bus_start_time - offset.value * 1e-9
            self.event_handle = vxlapy.XLhandle()
            self.api.xlSetNotification(
                self.portHandle, ctypes.byref(self.event_handle), 1)
            self._start = True

    def shutdown(self):
        self.closePort()
        self._start = False

    def reset(self):
        self.deactivateChannel()
        self.activateChannel()

    def send(self, msg):
        msg_id = msg.arbitration_id
        if msg.is_extended_id:
            msg_id |= vxlapy.XL_CAN_EXT_MSG_ID
        flags = 0
        message_count = ctypes.c_uint(1)
        xl_event = vxlapy.XLevent()
        xl_event.tag = vxlapy.XL_TRANSMIT_MSG
        xl_event.tagData.msg.id = msg_id
        xl_event.tagData.msg.dlc = msg.dlc
        xl_event.tagData.msg.flags = flags
        xl_event.tagData.msg.data[0:len(msg.data)] = msg.data
        try:
            self.api.xlCanTransmit(
                self.portHandle, self.accessMask, ctypes.byref(message_count), ctypes.byref(xl_event))
        except vxlapy.XLstatusError as e:
            if e.status not in [vxlapy.XL_ERR_QUEUE_IS_EMPTY, vxlapy.XL_ERROR, vxlapy.XL_ERR_QUEUE_IS_FULL]:
                raise

    def recv(self, timeout=None):
        end_time = time.time() + timeout if timeout is not None else None
        event = vxlapy.XLevent()
        event_count = ctypes.c_uint()

        while True:
            event_count.value = 1
            try:
                self.api.xlReceive(self.portHandle, ctypes.byref(
                    event_count), ctypes.byref(event))
            except vxlapy.XLstatusError as e:
                if e.status not in [vxlapy.XL_ERR_QUEUE_IS_EMPTY, vxlapy.XL_ERROR]:
                    raise
            else:
                if event.tag == vxlapy.XL_RECEIVE_MSG:
                    msg_id = event.tagData.msg.id
                    dlc = event.tagData.msg.dlc
                    flags = event.tagData.msg.flags
                    timestamp = event.timeStamp * 1e-9
                    channel = event.chanIndex
                    msg = Message(
                        timestamp=timestamp + self._time_offset,
                        arbitration_id=msg_id & 0x1FFFFFFF,
                        is_extended_id=bool(msg_id & vxlapy.XL_CAN_EXT_MSG_ID),
                        is_remote_frame=bool(flags & vxlapy.XL_CAN_MSG_FLAG_REMOTE_FRAME),
                        is_error_frame=bool(flags & vxlapy.XL_CAN_MSG_FLAG_ERROR_FRAME),
                        is_fd=False,
                        dlc=dlc,
                        direction='Tx' if bool(flags & vxlapy.XL_CAN_MSG_FLAG_TX_COMPLETED) else 'Rx',
                        data=event.tagData.msg.data[:dlc],
                        channel=channel)
                    return msg
            if end_time is not None and time.time() > end_time:
                return None
            if timeout is None:
                time_left_ms = 1000
            else:
                time_left = end_time - time.time()
                time_left_ms = max(0, int(time_left * 1000))
            self.api.waitForSingleObject(self.event_handle.value, time_left_ms)


class CanFdBus(vxlbase.VxlBase):
    def __init__(self, channel=0, app_name="CANalyzer", can_filters=None, poll_interval=0.01,
                 bitrate=500000, rx_queue_size=2 ** 14, data_bitrate=2000000, sjwAbr=8, tseg1Abr=31, tseg2Abr=8, sjwDbr=2, tseg1Dbr=7, tseg2Dbr=2, **config):

        super(CanFdBus, self).__init__()
        self.xlInterfaceVersion = vxlapy.XL_INTERFACE_VERSION_V4
        self.channel = channel
        self.poll_interval = poll_interval
        self.rx_queue_size = rx_queue_size
        self.bitrate = bitrate
        self._app_name = app_name
        self.channel_info = '%s:CAN %d' % (app_name, self.channel + 1)
        self.bus_type = vxlapy.XL_BUS_TYPE_CAN
        self.canFdConf = vxlapy.XLcanFdConf()
        self.canFdConf.arbitrationBitRate = ctypes.c_uint(bitrate)
        self.canFdConf.sjwAbr = ctypes.c_uint(sjwAbr)
        self.canFdConf.tseg1Abr = ctypes.c_uint(tseg1Abr)
        self.canFdConf.tseg2Abr = ctypes.c_uint(tseg2Abr)
        self.canFdConf.sjwDbr = ctypes.c_uint(sjwDbr)
        self.canFdConf.tseg1Dbr = ctypes.c_uint(tseg1Dbr)
        self.canFdConf.tseg2Dbr = ctypes.c_uint(tseg2Dbr)
        self.canFdConf.reserved = (ctypes.c_uint * 2)(*[0, 0])
        self.canFdConf.dataBitRate = ctypes.c_uint(data_bitrate)
        self.channelIdx = self.getchannelIdx()
        self.getChannelMask()
        self.openPort()
        offset = vxlapy.XLuint64()
        self.api.xlGetSyncTime(self.portHandle, offset)
        self.bus_start_time = time.time()
        self._time_offset = self.bus_start_time - offset.value * 1e-9
        self.event_handle = vxlapy.XLhandle()
        self.api.xlSetNotification(
            self.portHandle, ctypes.byref(self.event_handle), 1)
        self._start = True

    def getchannelIdx(self):
        return super(CanFdBus, self).getchannelIdx(self.channel, self._app_name, self.bus_type)

    def getChannelMask(self):
        return super(CanFdBus, self).getChannelMask(self.bus_type, self.channelIdx,
                                                  self.xlInterfaceVersion)

    def activateChannel(self):
        return super(CanFdBus, self).activateChannel(self.bus_type)

    def deactivateChannel(self):
        return super(CanFdBus, self).deactivateChannel()

    def openPort(self):
        super(CanFdBus, self).openPort(busType=self.bus_type, userName=self._app_name,
                                     rxQueueSize=self.rx_queue_size, xlInterfaceVersion=self.xlInterfaceVersion)
        if self.initAccess:
            self.api.xlCanFdSetConfiguration(
                self.portHandle, self.accessMask, ctypes.byref(self.canFdConf))
        self.activateChannel()

    def start(self):
        if not self._start:
            super(CanFdBus, self).__init__()
            self.xlInterfaceVersion = vxlapy.XL_INTERFACE_VERSION_V4
            self.channelIdx = self.getchannelIdx()
            self.getChannelMask()
            self.openPort()
            offset = vxlapy.XLuint64()
            self.api.xlGetSyncTime(self.portHandle, offset)
            self.bus_start_time = time.time()
            self._time_offset = self.bus_start_time - offset.value * 1e-9
            self.event_handle = vxlapy.XLhandle()
            self.api.xlSetNotification(
                self.portHandle, ctypes.byref(self.event_handle), 1)
            self._start = True

    def shutdown(self):
        self.closePort()
        self._start = False

    def reset(self):
        self.deactivateChannel()
        self.activateChannel()

    def send(self, msg):
        msg_id = msg.arbitration_id
        if msg.is_extended_id:
            msg_id |= vxlapy.XL_CAN_EXT_MSG_ID
        flags = 0
        if msg.is_fd:
            flags |= vxlapy.XL_CAN_TXMSG_FLAG_EDL
        if msg.bitrate_switch:
            flags |= vxlapy.XL_CAN_TXMSG_FLAG_BRS
        if msg.is_remote_frame:
            flags |= vxlapy.XL_CAN_TXMSG_FLAG_RTR

        message_count = ctypes.c_uint(1)
        MsgCntSent = ctypes.c_uint(0)
        xl_event = vxlapy.XLcanTxEvent()
        xl_event.tag = vxlapy.XL_CAN_EV_TAG_TX_MSG
        xl_event.transId = 0xffff

        xl_event.tagData.canMsg.canId = msg_id
        xl_event.tagData.canMsg.dlc = len2dlc(msg.dlc)
        xl_event.tagData.canMsg.msgFlags = flags
        xl_event.tagData.canMsg.data[0:len(msg.data)] = msg.data
        try:
            self.api.xlCanTransmitEx(
                self.portHandle, self.accessMask, message_count, ctypes.byref(MsgCntSent), ctypes.byref(xl_event))
        except vxlapy.XLstatusError as e:
            if e.status not in [vxlapy.XL_ERR_QUEUE_IS_EMPTY, vxlapy.XL_ERROR, vxlapy.XL_ERR_QUEUE_IS_FULL]:
                raise

    def recv(self, timeout=None):
        end_time = time.time() + timeout if timeout is not None else None
        event = vxlapy.XLcanRxEvent()

        while True:
            try:
                self.api.xlCanReceive(self.portHandle, ctypes.byref(event))
            except vxlapy.XLstatusError as e:
                if e.status not in [vxlapy.XL_ERR_QUEUE_IS_EMPTY, vxlapy.XL_ERROR, vxlapy.XL_ERR_QUEUE_IS_FULL]:
                    raise
            else:
                if event.tag == vxlapy.XL_CAN_EV_TAG_RX_OK or event.tag == vxlapy.XL_CAN_EV_TAG_TX_OK:
                    msg_id = event.tagData.canRxOkMsg.canId
                    dlc = dlc2len(event.tagData.canRxOkMsg.dlc)
                    flags = event.tagData.canRxOkMsg.msgFlags
                    timestamp = event.timeStampSync * 1e-9
                    channel = event.channelIndex
                    msg = Message(
                        timestamp=timestamp + self._time_offset,
                        arbitration_id=msg_id & 0x1FFFFFFF,
                        is_extended_id=bool(msg_id & vxlapy.XL_CAN_EXT_MSG_ID),
                        is_remote_frame=bool(flags & vxlapy.XL_CAN_RXMSG_FLAG_RTR),
                        is_error_frame=bool(flags & vxlapy.XL_CAN_RXMSG_FLAG_EF),
                        is_fd=bool(flags & vxlapy.XL_CAN_RXMSG_FLAG_EDL),
                        error_state_indicator=bool(flags & vxlapy.XL_CAN_RXMSG_FLAG_ESI),
                        bitrate_switch=bool(flags & vxlapy.XL_CAN_RXMSG_FLAG_BRS),
                        dlc=dlc,
                        direction='Rx',
                        data=event.tagData.canRxOkMsg.data[:dlc],
                        channel=channel)
                    return msg
            if end_time is not None and time.time() > end_time:
                return None
            if timeout is None:
                time_left_ms = 1000
            else:
                time_left = end_time - time.time()
                time_left_ms = max(0, int(time_left * 1000))
            self.api.waitForSingleObject(self.event_handle.value, time_left_ms)

if __name__ == "__main__":
    can_bus = CanBus(channel=0)
    msg = can_bus.recv()
    print(msg)
