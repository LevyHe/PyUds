# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 23:00:31 2019

@author: levy.he
"""

import threading
import time
from . import Message
from .ComBase import TpBase

class CanTpTimeout(Exception):
    def __str__(self):
        return "CanTp Response or Send Timeout."


class CanTpFrameError(Exception):
    def __str__(self):
        return "CanTp Frame Length Error."


class CanTpSendError(Exception):
    def __str__(self):
        return "Can bus is not ok, could not send data now."


class CanTp(TpBase):
    EXT_ID_MASK = 0x80000000
    FRAME_LENGTH = 8
    FUNC_FRAME_LENGTH = 8
    PAD_CHAR = 0xCC
    SELF_STMIN = 0.002
    FrameBuf = []
    FC_MESSAGE = [0x30,0x00,0x00,0xAA,0xAA,0xAA,0xAA,0xAA]
    _message = None

    def __init__(self,
                 phy_id=0x727,
                 func_id=0x7DF,
                 resp_id=0x7A7,
                 uudt_id=0x7FF,
                 FRAME_LENGTH=None):
        if phy_id > 0x7FF: phy_id = (phy_id & 0x1FFFFFFF) | self.EXT_ID_MASK
        if func_id > 0x7FF: func_id = (func_id & 0x1FFFFFFF) | self.EXT_ID_MASK
        if resp_id > 0x7FF: resp_id = (resp_id & 0x1FFFFFFF) | self.EXT_ID_MASK
        if uudt_id > 0x7FF: uudt_id = (uudt_id & 0x1FFFFFFF) | self.EXT_ID_MASK
        self.phy_id = phy_id
        self.func_id = func_id
        self.resp_id = resp_id
        self.uudt_id = uudt_id
        self.N_AS_AR = 1.0
        self.N_BS_CR = 1.0
        if FRAME_LENGTH is not None:
            self.FRAME_LENGTH = FRAME_LENGTH
        self.STmin=0
        self.FS=0
        self.BS=0
        self.SN=0
        self.ReqBuf=[]
        self.RespBuf=[]
        self.RxLength=0
        self.ReqIndex=0
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._req_event = threading.Event()
        self._resp_event = threading.Event()
        self._busBusy = False
        self._PduState = self.PDU_TYPE_NONE
        self._running = True
        self._sending = False
        self._sending_once = False
        self._start_time = time.time()
        self.diag_start = False
        

    def GetAddrInfo(self):
        return (self.phy_id, self.func_id, self.resp_id)
        
    def SendFuncReq(self, data):
        self.diag_start = True
        self._resp_event.clear()
        if len(data) < self.FUNC_FRAME_LENGTH:
            self.ReqBuf = data[:]
            self.FrameBuf = [len(data) & 0x0F] + self.ReqBuf
            self._message = self._pack_func_message(
                self.func_id, self.FrameBuf)
            self._sending_once = True
            rtn = self._req_event.wait(self.N_BS_CR)
            if rtn :
                self._req_event.clear()
            else:
                raise CanTpTimeout()
        else:
            raise CanTpFrameError()
    def SendPhyReq(self, data):
        self.diag_start = True
        self._resp_event.clear()
        if len(data) < self.FRAME_LENGTH:
            if len(data) < self.FUNC_FRAME_LENGTH:
                self.ReqBuf = data[:]
                self.FrameBuf = [len(data) & 0x0F] + self.ReqBuf
            else:
                self.ReqBuf = data[:]
                self.FrameBuf = [0x00, len(data) & 0xFF] + self.ReqBuf

            self._message = self._pack_message(self.phy_id, self.FrameBuf)
            self._sending_once = True
            rtn = self._req_event.wait(self.N_BS_CR)
            if rtn :
                self._req_event.clear()
            else:
                raise CanTpTimeout()
        else:
            self.SN = 1
            self.ReqBuf = data[:4095]
            self.FrameBuf = [(len(self.ReqBuf) >> 8)|0x10,len(self.ReqBuf) & 0xFF]+self.ReqBuf[:6]
            self.ReqIndex = self.FRAME_LENGTH - 2
            self._message = self._pack_message(self.phy_id, self.FrameBuf)
            self._sending_once = True
            self._busBusy = True
            while self._busBusy:
                rtn = self._req_event.wait(self.N_BS_CR)
                if rtn :
                    self._req_event.clear()
                else:
                    raise CanTpTimeout()

    def WaitResponse(self,timeout):
        rtn = self._resp_event.wait(timeout)
        if rtn:
            self._resp_event.clear()
            return self._PduState,self.RespBuf
        else:
            return self.TIME_OUT_ERROR, None
    def WaitReserverMsg(self):
        while self._busBusy:
            rtn = self._resp_event.wait(self.N_BS_CR)
            if rtn is not None:
                self._resp_event.clear()
            else:
                return self.TIME_OUT_ERROR, None
        return self._PduState, self.RespBuf

    def _cf_sender(self):
        if self._sending:
            end_index = self.ReqIndex + self.FRAME_LENGTH - 1
            self.FrameBuf = [0x20 | (self.SN & 0x0F)] + self.ReqBuf[self.ReqIndex:end_index]
            self.ReqIndex += len(self.FrameBuf) - 1
            self.SN &= 0xFF
            self._req_event.set()
            if self.ReqIndex >= len(self.ReqBuf):
                self._sending = False
                self._busBusy = False
            if self.BS != 0 and (self.SN%self.BS) == 0:
                self._sending = False
            self.SN += 1
            return self._pack_message(self.phy_id,self.FrameBuf)
        else:
            return None
    def sender(self):
        if self._sending_once:
            self._sending_once = False
            self._req_event.set()
            return self._message

        wait_time = time.time() - self._start_time
        if wait_time > self.STmin:
            self._start_time = time.time()
            return self._cf_sender()
    def reader(self, msg):
        if not self.diag_start:
            return
        if msg.is_extended_id:
            msg_id = self.EXT_ID_MASK | msg.arbitration_id
        else:
            msg_id = msg.arbitration_id
        if msg_id == self.resp_id and msg.dlc <= self.FRAME_LENGTH:
            pdu_type = msg.data[0] >> 4
            if pdu_type == 0x00:
                if msg.data[0] == 0x00:
                    self.RxLength = msg.data[1] & 0xFF
                    self.RespBuf = list(msg.data[2:self.RxLength + 2])
                else:
                    self.RxLength = msg.data[0] & 0x0F
                    self.RespBuf = list(msg.data[1:self.RxLength + 1])
                self._resp_event.set()
                self._PduState = self.PDU_TYPE_SF
            elif pdu_type == 0x01:
                self.RxLength = ((msg.data[0] & 0x0F)<<8) + msg.data[1]
                self.RespBuf = list(msg.data[2:msg.dlc])
                self.SN = 0x01
                self._message = self._pack_message(self.phy_id, self.FC_MESSAGE)
                self._sending_once = True
                self._resp_event.set()
                self._busBusy = True
                self._PduState = self.PDU_TYPE_MF
            elif pdu_type == 0x02:
                r_sn = msg.data[0] & 0x0F
                if r_sn == (self.SN & 0x0F):
                    self.SN += 1
                    if (len(self.RespBuf) + msg.dlc - 1) < self.RxLength:
                        self.RespBuf+=list(msg.data[1:msg.dlc])
                    else:
                        self.RespBuf+=list(msg.data[1:self.RxLength - len(self.RespBuf) + 1])
                        self._busBusy = False
                        self._PduState = self.PDU_TYPE_LF
                self._resp_event.set()
            elif pdu_type == 0x03:
                self.FS = msg.data[0] & 0x0F
                self.BS = msg.data[1]
                stmin = msg.data[2]
                if stmin <= 0x7F:
                    self.STmin = stmin/1000.0
                elif 0xF1 <= stmin <= 0xF9:
                    self.STmin = (stmin & 0x0F)/10000.0
                else:
                    self.STmin = 0.127
                if self.STmin < self.SELF_STMIN:
                    self.STmin = self.SELF_STMIN
                self._req_event.set()
                self._PduState = self.PDU_TYPE_FC
                if self.FS == 0x00:
                    self._sending = True
                    self._start_time = time.time()
            else:
                pass

    def _pack_func_message(self, tx_id, buf):
        if (tx_id & self.EXT_ID_MASK) == 0:
            ext_id = False
            msg_id = tx_id & 0x7FF
        else:
            ext_id = True
            msg_id = tx_id & 0x1FFFFFFF
        sbuf = buf + [self.PAD_CHAR] * (self.FUNC_FRAME_LENGTH - len(buf))
        msg = Message(arbitration_id=msg_id, data=sbuf, is_extended_id=ext_id)
        return msg

    def _pack_message(self, tx_id, buf):
        if (tx_id & self.EXT_ID_MASK) == 0:
            ext_id = False
            msg_id = tx_id & 0x7FF
        else:
            ext_id = True
            msg_id = tx_id & 0x1FFFFFFF
        sbuf = buf + [self.PAD_CHAR] * (self.FRAME_LENGTH - len(buf))
        msg = Message(arbitration_id=msg_id, data=sbuf, is_extended_id=ext_id)
        return msg

class CanFdTp(CanTp):
    CAN_FD_DLC = [
        8, 12, 16, 20, 24, 32, 48, 64
    ]
    def __init__(self,
                 phy_id=0x727,
                 func_id=0x7DF,
                 resp_id=0x7A7,
                 uudt_id=0x7FF,
                 FRAME_LENGTH=64):
        super(CanFdTp, self).__init__(
            phy_id=phy_id, func_id=func_id, resp_id=resp_id, uudt_id=uudt_id, FRAME_LENGTH=FRAME_LENGTH)

    def _pack_func_message(self, tx_id, buf):
        if (tx_id & self.EXT_ID_MASK) == 0:
            ext_id = False
            msg_id = tx_id & 0x7FF
        else:
            ext_id = True
            msg_id = tx_id & 0x1FFFFFFF
        dlc = 64
        for l in self.CAN_FD_DLC:
            if l >= len(buf):
                dlc = l
                break
        is_fd = True
        
        sbuf = buf + [self.PAD_CHAR] * (dlc - len(buf))
        msg = Message(arbitration_id=msg_id, data=sbuf, is_extended_id=ext_id, is_fd=is_fd)
        return msg

    def _pack_message(self, tx_id, buf):
        if (tx_id & self.EXT_ID_MASK) == 0:
            ext_id = False
            msg_id = tx_id & 0x7FF
        else:
            ext_id = True
            msg_id = tx_id & 0x1FFFFFFF
        dlc = 64
        for l in self.CAN_FD_DLC:
            if l >= len(buf):
                dlc = l
                break
        is_fd = True
        
        sbuf = buf + [self.PAD_CHAR] * (dlc - len(buf))
        msg = Message(arbitration_id=msg_id, data=sbuf, is_extended_id=ext_id, is_fd=is_fd)
        return msg
