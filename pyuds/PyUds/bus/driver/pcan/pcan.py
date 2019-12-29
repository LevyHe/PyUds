# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 09:09:52 2019

@author: levy.he
"""
import ctypes
import time
from win32event import CreateEvent
from win32event import WaitForSingleObject, WAIT_OBJECT_0, INFINITE
from . import basic
from ...can import Message

CAN_FD_DLC = [
    0, 1, 2, 3, 4, 5, 6, 7, 8,
    12, 16, 20, 24, 32, 48, 64
]

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

class PCANError(Exception):
    pass

pcan_bitrate_objs = {1000000: basic.PCAN_BAUD_1M,
                     800000: basic.PCAN_BAUD_800K,
                     500000: basic.PCAN_BAUD_500K,
                     250000: basic.PCAN_BAUD_250K,
                     125000: basic.PCAN_BAUD_125K,
                     100000: basic.PCAN_BAUD_100K,
                     95000: basic.PCAN_BAUD_95K,
                     83000: basic.PCAN_BAUD_83K,
                     50000: basic.PCAN_BAUD_50K,
                     47000: basic.PCAN_BAUD_47K,
                     33000: basic.PCAN_BAUD_33K,
                     20000: basic.PCAN_BAUD_20K,
                     10000: basic.PCAN_BAUD_10K,
                     5000: basic.PCAN_BAUD_5K}


class CanBus(basic.PCANBasic):
    def __init__(self, channel=0, app_name="PCAN", can_filters=None, poll_interval=0.01,
                 bitrate=500000, rx_queue_size=2** 14, **config):
        super(CanBus, self).__init__()
        self.channel = channel
        self.channel_info = 'PCAN_USBBUS%d' % (self.channel + 1)
        self.bitrate = pcan_bitrate_objs.get(bitrate, basic.PCAN_BAUD_500K)
        self.bus_type = basic.PCAN_TYPE_ISA
        self.ioport = 0x02A0
        self.interrupt = 11

        self.poll_interval = poll_interval
        self.rx_queue_size = rx_queue_size
        
        self._app_name = app_name

        # self.m_objPCANBasic = PCANBasic()
        self.m_PcanHandle = getattr(basic, self.channel_info)

        # if basic.state is basic.BusState.ACTIVE or basic.BusState.PASSIVE:
        #     self._state = basic.state
        # else:
        #     raise PCANError("BusState must be Active or Passive")

        result = self.Initialize(
            self.m_PcanHandle, self.bitrate, self.bus_type, self.ioport, self.interrupt)

        if result != basic.PCAN_ERROR_OK:
            raise PCANError(self._get_formatted_error(result))
        self._recv_event = self._pcan_event()
        result = self.SetValue(
            self.m_PcanHandle, basic.PCAN_RECEIVE_EVENT, self._recv_event)
        if result != basic.PCAN_ERROR_OK:
            raise PCANError(self._get_formatted_error(result))

        self.bus_start_time = time.time()
        self._start = True
        self.is_time_sync = False
        self._time_offset = 0

    def _get_formatted_error(self, error):
        """
        Gets the text using the GetErrorText API function.
        If the function call succeeds, the translated error is returned. If it fails,
        a text describing the current error is returned. Multiple errors may
        be present in which case their individual messages are included in the
        return string, one line per error.
        """

        def bits(n):
            """TODO: document"""
            while n:
                b = n & (~n+1)
                yield b
                n ^= b

        stsReturn = self.GetErrorText(error, 0)
        if stsReturn[0] != basic.PCAN_ERROR_OK:
            strings = []

            for b in bits(error):
                stsReturn = self.GetErrorText(b, 0)
                if stsReturn[0] != basic.PCAN_ERROR_OK:
                    text = "An error occurred. Error-code's text ({0:X}h) couldn't be retrieved".format(
                        error)
                else:
                    text = stsReturn[1].decode('utf-8', errors='replace')

                strings.append(text)

            complete_text = '\n'.join(strings)
        else:
            complete_text = stsReturn[1].decode('utf-8', errors='replace')

        return complete_text

    def _pcan_event(self):
        return CreateEvent(None, 0, 0, None)

    def time_sync(self, time_stamp):
        if not self.is_time_sync:
            self._time_offset = time.time() - time_stamp
            self.is_time_sync = True

    def start(self):
        if not self._start:
            super(CanBus, self).__init__()
            result = self.Initialize(
                self.m_PcanHandle, self.bitrate, self.bus_type, self.ioport, self.interrupt)

            if result != basic.PCAN_ERROR_OK:
                raise PCANError(self._get_formatted_error(result))
            self._recv_event = self._pcan_event()
            result = self.SetValue(
                self.m_PcanHandle, basic.PCAN_RECEIVE_EVENT, self._recv_event)
            if result != basic.PCAN_ERROR_OK:
                raise PCANError(self._get_formatted_error(result))
            self.bus_start_time = time.time()
            self._start = True
            self.is_time_sync = False
            self._time_offset = 0

    def shutdown(self):
        self.Uninitialize(self.m_PcanHandle)
        self._start = False

    def reset(self):
        super(CanBus, self).Reset(self.m_PcanHandle)

    def send(self, msg):
        msgType = basic.PCAN_MESSAGE_EXTENDED if msg.is_extended_id else basic.PCAN_MESSAGE_STANDARD

        CANMsg = basic.TPCANMsg()

        CANMsg.ID = msg.arbitration_id
        CANMsg.LEN = msg.dlc
        CANMsg.MSGTYPE = msgType
        if msg.is_remote_frame:
            CANMsg.MSGTYPE = msgType.value | basic.PCAN_MESSAGE_RTR.value
        else:
            CANMsg.DATA[0:len(msg.data)] = msg.data

        result = self.Write(self.m_PcanHandle, CANMsg)

        if result != basic.PCAN_ERROR_OK:
            raise PCANError("Failed to send: " +
                            self._get_formatted_error(result))

    def recv(self, timeout=None):
        end_time = time.time() + timeout if timeout is not None else None
        while True:
            result = self.Read(self.m_PcanHandle)
            if result[0] == basic.PCAN_ERROR_OK:
                theMsg = result[1]
                itsTimeStamp = result[2]

                #log.debug("Received a message")

                is_remote_frame = (theMsg.MSGTYPE &
                                   basic.PCAN_MESSAGE_RTR.value) == basic.PCAN_MESSAGE_RTR.value
                is_extended_id = (theMsg.MSGTYPE &
                                  basic.PCAN_MESSAGE_EXTENDED.value) == basic.PCAN_MESSAGE_EXTENDED.value
                is_error_frame = (theMsg.MSGTYPE &
                                  basic.PCAN_MESSAGE_ERRFRAME.value) == basic.PCAN_MESSAGE_ERRFRAME.value
                dlc = theMsg.LEN
                timestamp = (itsTimeStamp.micros + 1000 * itsTimeStamp.millis +
                                                    0x100000000 * 1000 * itsTimeStamp.millis_overflow) / (1000.0 * 1000.0)
                self.time_sync(timestamp)
                msg_id = theMsg.ID
                channel = self.channel
                msg = Message(
                    timestamp=timestamp + self._time_offset,
                    arbitration_id=msg_id & 0x1FFFFFFF,
                    is_extended_id=bool(is_extended_id),
                    is_remote_frame=bool(is_remote_frame),
                    is_error_frame=bool(is_error_frame),
                    is_fd=False,
                    dlc=dlc,
                    direction='Rx',
                    data=theMsg.DATA[:dlc],
                    channel=channel)
                return msg
            elif result[0] & (basic.PCAN_ERROR_BUSLIGHT | basic.PCAN_ERROR_BUSHEAVY):
                return None
            elif result[0] == basic.PCAN_ERROR_QRCVEMPTY:
                if end_time is not None and time.time() > end_time:
                    return None
                if timeout is None:
                    time_left_ms = 1000
                else:
                    time_left = end_time - time.time()
                    time_left_ms = max(0, int(time_left * 1000))
                WaitForSingleObject(self._recv_event, time_left_ms)
            else:
                raise PCANError(self._get_formatted_error(result[0]))


class CanFdBus(basic.PCANBasic):

    fd_parameter_list = ['f_clock', 'nom_brp', 'nom_tseg1', 'nom_tseg2',
                              'nom_sjw', 'data_brp', 'data_tseg1', 'data_tseg2', 'data_sjw']

    def __init__(self, channel=0, app_name="PCAN", can_filters=None, poll_interval=0.01,
                 bitrate=500000, rx_queue_size=2 ** 14, f_clock=80000000, nom_brp=10, nom_tseg1=5, nom_tseg2=2, nom_sjw=1, data_brp=4, data_tseg1=7, data_tseg2=2, data_sjw=1, **config):
        super(CanFdBus, self).__init__()
        self.channel = channel
        self.channel_info = 'PCAN_USBBUS%d' % (self.channel + 1)
        self.bitrate = pcan_bitrate_objs.get(bitrate, basic.PCAN_BAUD_500K)
        self.bus_type = basic.PCAN_TYPE_ISA
        self.ioport = 0x02A0
        self.interrupt = 11

        self.poll_interval = poll_interval
        self.rx_queue_size = rx_queue_size
        self._app_name = app_name

        self.m_PcanHandle = getattr(basic, self.channel_info)
        self.canFdConf = dict(f_clock=f_clock, nom_brp=nom_brp, nom_tseg1=nom_tseg1, nom_tseg2=nom_tseg2,
                              nom_sjw=nom_sjw, data_brp=data_brp, data_tseg1=data_tseg1, data_tseg2=data_tseg2, data_sjw=data_sjw)
        
        
        self.fd_bitrate = ','.join(
            ["{}={}".format(n, self.canFdConf[n]) for n in CanFdBus.fd_parameter_list]).encode("ASCII")

        result = self.InitializeFD(self.m_PcanHandle, self.fd_bitrate)

        if result != basic.PCAN_ERROR_OK:
            raise PCANError(self._get_formatted_error(result))
        self._recv_event = self._pcan_event()
        result = self.SetValue(
            self.m_PcanHandle, basic.PCAN_RECEIVE_EVENT, self._recv_event)
        if result != basic.PCAN_ERROR_OK:
            raise PCANError(self._get_formatted_error(result))

        # self.SetValue(self.m_PcanHandle, basic.PCAN_LISTEN_ONLY,
        #               basic.PCAN_PARAMETER_OFF)
        self.bus_start_time = time.time()
        self._start = True
        self.is_time_sync = False
        self._time_offset = 0

    def _pcan_event(self):
        return CreateEvent(None, 0, 0, None)

    def _get_formatted_error(self, error):
        """
        Gets the text using the GetErrorText API function.
        If the function call succeeds, the translated error is returned. If it fails,
        a text describing the current error is returned. Multiple errors may
        be present in which case their individual messages are included in the
        return string, one line per error.
        """

        def bits(n):
            """TODO: document"""
            while n:
                b = n & (~n+1)
                yield b
                n ^= b

        stsReturn = self.GetErrorText(error, 0)
        if stsReturn[0] != basic.PCAN_ERROR_OK:
            strings = []

            for b in bits(error):
                stsReturn = self.GetErrorText(b, 0)
                if stsReturn[0] != basic.PCAN_ERROR_OK:
                    text = "An error occurred. Error-code's text ({0:X}h) couldn't be retrieved".format(
                        error)
                else:
                    text = stsReturn[1].decode('utf-8', errors='replace')

                strings.append(text)

            complete_text = '\n'.join(strings)
        else:
            complete_text = stsReturn[1].decode('utf-8', errors='replace')

        return complete_text

    def start(self):
        if not self._start:
            super(CanFdBus, self).__init__()
            self.fd_bitrate = ','.join(
                ["{}={}".format(n, self.canFdConf[n]) for n in CanFdBus.fd_parameter_list]).encode("ASCII")
            result = self.InitializeFD(self.m_PcanHandle, self.fd_bitrate)
            if result != basic.PCAN_ERROR_OK:
                raise PCANError(self._get_formatted_error(result))
            self._recv_event = self._pcan_event()
            result = self.SetValue(
                self.m_PcanHandle, basic.PCAN_RECEIVE_EVENT, self._recv_event)
            if result != basic.PCAN_ERROR_OK:
                raise PCANError(self._get_formatted_error(result))
            self.bus_start_time = time.time()
            self._start = True
            self.is_time_sync = False
            self._time_offset = 0

    def time_sync(self, time_stamp):
        if not self.is_time_sync:
            self._time_offset = time.time() - time_stamp
            self.is_time_sync = True


    def shutdown(self):
        self.Uninitialize(self.m_PcanHandle)
        self._start = False

    def reset(self):
        super(CanFdBus, self).Reset(self.m_PcanHandle)

    def send(self, msg):
        msgType = 0
        if msg.is_extended_id:
            msgType |= basic.PCAN_MESSAGE_EXTENDED.value
        if msg.is_fd:
            msgType |= basic.PCAN_MESSAGE_FD.value
        if msg.bitrate_switch:
            msgType |= basic.PCAN_MESSAGE_BRS.value
        if msg.is_remote_frame:
            msgType |= basic.PCAN_MESSAGE_RTR.value

        CANMsg = basic.TPCANMsgFD()
        
        CANMsg.ID = msg.arbitration_id
        CANMsg.DLC = len2dlc(msg.dlc)
        CANMsg.MSGTYPE = basic.TPCANMessageType(msgType)
        if not msg.is_remote_frame:
            CANMsg.DATA[0:len(msg.data)] = msg.data
        # while True:
        result = self.WriteFD(self.m_PcanHandle, CANMsg)
        if result == basic.PCAN_ERROR_OK:
            return
        elif result == basic.PCAN_ERROR_BUSOFF:
            pass
        else:
            raise PCANError("Failed to send: " +
                            self._get_formatted_error(result))

    def recv(self, timeout=None):
        end_time = time.time() + timeout if timeout is not None else None
        while True:
            result = self.ReadFD(self.m_PcanHandle)
            if result[0] == basic.PCAN_ERROR_OK:
                theMsg = result[1]
                itsTimeStamp = result[2]

                #log.debug("Received a message")

                is_remote_frame = (theMsg.MSGTYPE &
                                   basic.PCAN_MESSAGE_RTR.value) == basic.PCAN_MESSAGE_RTR.value
                is_extended_id = (theMsg.MSGTYPE &
                                  basic.PCAN_MESSAGE_EXTENDED.value) == basic.PCAN_MESSAGE_EXTENDED.value
                is_error_frame = (theMsg.MSGTYPE &
                                  basic.PCAN_MESSAGE_ERRFRAME.value) == basic.PCAN_MESSAGE_ERRFRAME.value
                is_fd = (theMsg.MSGTYPE &
                         basic.PCAN_MESSAGE_FD.value) == basic.PCAN_MESSAGE_FD.value
                error_state_indicator = (theMsg.MSGTYPE &
                                         basic.PCAN_MESSAGE_ESI.value) == basic.PCAN_MESSAGE_ESI.value
                bitrate_switch = (theMsg.MSGTYPE &
                                  basic.PCAN_MESSAGE_BRS.value) == basic.PCAN_MESSAGE_BRS.value
                dlc = dlc2len(theMsg.DLC)
                timestamp = itsTimeStamp.value / 1e6
                self.time_sync(timestamp)
                timestamp += self._time_offset
                msg_id = theMsg.ID
                channel = self.channel
                msg = Message(
                    timestamp=timestamp,
                    arbitration_id=msg_id & 0x1FFFFFFF,
                    is_extended_id=bool(is_extended_id),
                    is_remote_frame=bool(is_remote_frame),
                    is_error_frame=bool(is_error_frame),
                    error_state_indicator=error_state_indicator,
                    bitrate_switch=bitrate_switch,
                    is_fd=is_fd,
                    dlc=dlc,
                    direction='Rx',
                    data=theMsg.DATA[:dlc],
                    channel=channel)
                return msg
            elif result[0] & (basic.PCAN_ERROR_BUSLIGHT | basic.PCAN_ERROR_BUSHEAVY):
                return None
            elif result[0] == basic.PCAN_ERROR_QRCVEMPTY:
                if end_time is not None and time.time() > end_time:
                    return None
                if timeout is None:
                    time_left_ms = 1000
                else:
                    time_left = end_time - time.time()
                    time_left_ms = max(0, int(time_left * 1000))
                WaitForSingleObject(self._recv_event, time_left_ms)
            else:
                raise PCANError(self._get_formatted_error(result[0]))
