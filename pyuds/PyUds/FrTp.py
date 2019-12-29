# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 23:00:31 2019

@author: levy.he
"""
import threading
import time
from . import FrFrame
from .ComBase import TpBase


class FrTpTimeout(Exception):
    def __str__(self):
        return "FrTp Response or Send Timeout."


class FrTpFrameError(Exception):
    def __init__(self, error_string):
        super(FrTpFrameError, self).__init__(error_string)

class FrTpSendError(Exception):
    def __str__(self):
        return "Can bus is not ok, could not send data now."


class FrTp(TpBase):

    PAD_CHAR = 0x00
    FrameBuf = []
    TP_CL_IDLE = 0
    TP_CL_TX = 1
    TP_CL_RX = 2
    TP_WAITING=0
    TP_SENDING = 1
    RX_MAX_RETRY = 5
    TX_MAX_RETRY = 5
    _message = None
    FR_STF = 0x40
    FR_STFU = 0x40
    FR_STFA = 0x41
    FR_CF1 = 0x50
    FR_CF2 = 0x60
    FR_CF_EOB = 0x70
    FR_FC = 0x80
    FR_FC_CTS = 0x83
    FR_FC_ACK_RET = 0x84
    FR_FC_WAIT = 0x85
    FR_FC_ABT = 0x86
    FR_FC_OVER_FLOW = 0x87
    FR_LF = 0x90
    FR_FC_ACK = 0
    FR_FC_RET = 1
    FC_ACK_PCI = [FR_FC_ACK_RET, FR_FC_ACK, 0x00, 0x00]
    FC_ABT_PCI = [FR_FC_ABT]
    FC_CTS_PCI = [FR_FC_CTS, 0x00, 0x00, 0x00]
    def __init__(self,rx_slots=[(0,0,1)],tx_slots=[(0,0,1)],source_addr=0,target_addr=0,func_addr=0,tx_frame_length=22,rx_frame_length=32, ack=False):

        self.rx_slots = [dict(slot_id=x[0], base_cycle=x[1], repetition_cycle=x[2]) for x in rx_slots]
        self.tx_slots = [dict(slot_id=x[0], base_cycle=x[1], repetition_cycle=x[2]) for x in tx_slots]
        self.source_addr = source_addr&0xFFFF
        self.target_addr = target_addr&0xFFFF
        self.func_addr = func_addr & 0xFFFF
        self.tx_frame_length = tx_frame_length
        self.tx_max_stf_length = tx_frame_length - 8
        self.tx_max_cf_length = tx_frame_length - 6
        self.tx_max_lf_length = tx_frame_length - 8
        self.rx_frame_length = rx_frame_length
        self.rx_max_stf_length = rx_frame_length - 8
        self.rx_max_cf_length = rx_frame_length - 6
        self.rx_max_lf_length = rx_frame_length - 8
        self.ack = 1 if ack else 0
        self.rx_ack = 0
        self._rx_cf_toggle = self.FR_CF1
        self._tx_cf_toggle = self.FR_CF1
        self._phy_addr_pad = [(self.target_addr >> 8)&0xFF, self.target_addr &
                              0xFF, (self.source_addr >> 8)&0xFF, self.source_addr & 0xFF]
        self._func_addr_pad = [(self.func_addr >> 8)&0xFF, self.func_addr &
                               0xFF, (self.source_addr >> 8)&0xFF, self.source_addr & 0xFF]
        self.N_AS_AR = 1.0
        self.N_BS_CR = 1.0
        self.TX_BFS = 65536
        self.RX_BFS = 0
        self.SC=0
        self.MNPC=0
        self.SN=0
        self.ReqBuf=[]
        self.RespBuf=[]
        self.Rx_ML=0
        self.ReqIndex = 0
        self.Tx_CF_Index = 0
        self._CL_STATUS = self.TP_CL_IDLE
        self._TP_TX_STATUS = self.TP_WAITING
        self._TP_RX_STATUS = self.TP_WAITING
        self._rx_retry_count = 0
        self._tx_retry_count = 0
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._req_event = threading.Event()
        self._resp_event = threading.Event()
        self._PduState = self.PDU_TYPE_NONE
        self._sending_once = False
        self._start_time = time.time()
        self._fr_cycle = 0
        self._last_fr_cycle = 0
        self._current_pci = 0
        self.error_str = ''

    def GetAddrInfo(self):
       return (self.target_addr, self.func_addr, self.source_addr)
       
    def update_fr_cycle(self,fr_cycle):
        self._fr_cycle = fr_cycle

    def SendFuncReq(self, data):
        self.error_str = ''
        self._resp_event.clear()
        if len(data) <= self.tx_max_stf_length:
            self.ReqBuf = data[:]
            ML = len(self.ReqBuf)
            C_PCI = [self.FR_STFU, len(self.ReqBuf), ML >> 8, ML & 0xFF]
            self._func_send_once(C_PCI, self.ReqBuf)
            rtn = self._req_event.wait(self.N_BS_CR)
            if rtn is not None:
                self._req_event.clear()
            else:
                raise FrTpTimeout()
        else:
            raise FrTpFrameError('Functional request has wrong frame length')
    def SendPhyReq(self, data):
        self.error_str = ''
        self._resp_event.clear()
        self.ReqBuf = data[:0xFFFF]
        fpl = min(len(self.ReqBuf), self.tx_max_stf_length)
        self.ReqIndex = fpl
        self.Tx_CF_Index = fpl
        ML = len(self.ReqBuf)
        stf = self.FR_STF | self.ack
        C_PCI = [stf, fpl, ML >> 8, ML & 0xFF]
        self._phy_send_once(C_PCI, self.ReqBuf[:fpl])
        if ML <= self.tx_max_stf_length:
            rtn = self._req_event.wait(self.N_BS_CR)
            if rtn :
                self._req_event.clear()
            else:
                raise FrTpTimeout()
        else:
            self.SN = 1
            self._CL_STATUS = self.TP_CL_TX
            self._TP_TX_STATUS = self.TP_WAITING
            while self._CL_STATUS == self.TP_CL_TX:
                rtn = self._req_event.wait(self.N_BS_CR)
                if rtn is not None:
                    self._req_event.clear()
                else:
                    raise FrTpTimeout()
            if len(self.error_str) > 0:
                raise FrTpFrameError(self.error_str)
            
    def WaitResponse(self,timeout):
        rtn = self._resp_event.wait(timeout)
        if rtn:
            self._resp_event.clear()
            return self._PduState,self.RespBuf
        else:
            return self.TIME_OUT_ERROR, None
    def WaitReserverMsg(self):
        while self._CL_STATUS == self.TP_CL_RX:
            rtn = self._resp_event.wait(self.N_BS_CR)
            if rtn is not None:
                self._resp_event.clear()
            else:
                return self.TIME_OUT_ERROR, None
        self._CL_STATUS = self.TP_CL_IDLE
        if len(self.error_str) > 0:
            raise FrTpFrameError(self.error_str)
        return self._PduState, self.RespBuf        
    
    def _cf_sender(self):
        if self._CL_STATUS == self.TP_CL_TX and self._TP_TX_STATUS == self.TP_SENDING:
            remain_len = len(self.ReqBuf) - self.ReqIndex
            BFS = min(self.RX_BFS,self.TX_BFS)
            cf_remain = BFS - self.Tx_CF_Index
            if remain_len <= self.tx_max_lf_length:
                ML = len(self.ReqBuf)
                lf_pci = [self.FR_LF, remain_len, ML >> 8, ML & 0xFF]
                self.FrameBuf = self._phy_addr_pad + lf_pci + self.ReqBuf[self.ReqIndex:]
                self.ReqIndex = len(self.ReqBuf)
                self._TP_TX_STATUS = self.TP_WAITING
                if self.ack == 0:
                    self._CL_STATUS = self.TP_CL_IDLE
            elif cf_remain <= self.tx_max_cf_length:
                buf = self.ReqBuf[self.ReqIndex:self.ReqIndex+cf_remain]
                cf_pci = [self.FR_CF_EOB | (self.SN & 0x0F), cf_remain]
                self.FrameBuf = self._phy_addr_pad + cf_pci + buf
                self.ReqIndex += cf_remain
                self.Tx_CF_Index = 0
                self._TP_TX_STATUS = self.TP_WAITING
            else:
                fpl = self.tx_max_cf_length
                buf = self.ReqBuf[self.ReqIndex:self.ReqIndex+fpl]
                cf_pci = [self._tx_cf_toggle | (self.SN & 0x0F), fpl]
                self.FrameBuf = self._phy_addr_pad + cf_pci + buf
                self.ReqIndex += fpl
                self.Tx_CF_Index += fpl
            self.SN += 1
            self.SN &= 0xFF
            self._req_event.set()
            return self.FrameBuf
        else:
            return None
    def sender(self):
        if self._sending_once:
            self._sending_once = False
            self._req_event.set()
            return self._message
        if self._CL_STATUS == self.TP_CL_RX:
            self._TP_RX_STATUS = self.TP_WAITING
            if len(self.RespBuf) == self.RX_ML or len(self.error_str) > 0:
                self._CL_STATUS = self.TP_CL_IDLE
        if self._CL_STATUS == self.TP_CL_IDLE:
            return None
        wait_cycle = self._fr_cycle - self._last_fr_cycle
        if wait_cycle < 0:
            wait_cycle += 64
        if wait_cycle >= self.SC:
            self._last_fr_cycle = self._fr_cycle
            tx_slots = self.tx_slots if self.MNPC == 0 else self.tx_slots[:self.MNPC]
            fr_list=[]
            for slot in tx_slots:
                fr = self._cf_sender()
                if fr is not None:
                    fr_list.append(self._pack_frame(self.FrameBuf,tx_slot=slot))
                else:
                    break
            return fr_list
    def reader(self, msg):
        if msg.slot_id in [x["slot_id"] for x in self.rx_slots]:
            target_addr = (msg.data[0] << 8) + msg.data[1]
            source_addr = (msg.data[2] << 8) + msg.data[3]
            if target_addr != self.source_addr:
                return
            pdu_type=msg.data[4]
            if pdu_type == self.FR_STFU or pdu_type == self.FR_STFA:
                if self._CL_STATUS == self.TP_CL_TX:
                    '''when tranmit message ignore STF'''
                    return
                self.rx_ack = pdu_type & 0x01
                FPL = msg.data[5]
                self.RX_ML = (msg.data[6] << 8) + msg.data[7]
                self._unpack_stf(FPL,msg.data[8:])
                self._resp_event.set()
            elif (pdu_type & 0xF0) == self._rx_cf_toggle:
                if self._CL_STATUS != self.TP_CL_RX or self._TP_RX_STATUS != self.TP_WAITING:
                    return
                r_sn = pdu_type & 0x0F
                if r_sn == (self.SN & 0x0F):
                    self.SN += 1
                    FPL = msg.data[5]
                    self._unpack_cf(FPL, msg.data[6:])
                else:
                    self._sn_error_ret()
                self._resp_event.set()
            elif (pdu_type & 0xF0) == self.FR_CF_EOB:
                if self._CL_STATUS != self.TP_CL_RX or self._TP_RX_STATUS != self.TP_WAITING:
                    return
                r_sn = pdu_type & 0x0F
                if r_sn == (self.SN & 0x0F):
                    self.SN += 1
                    FPL = msg.data[5]
                    self._unpack_cf(FPL, msg.data[6:])
                    self._phy_send_once(self.FC_CTS_PCI)
                else:
                    self._sn_error_ret()
                self._resp_event.set()
            elif pdu_type == self.FR_FC_CTS:
                if self._CL_STATUS != self.TP_CL_TX or self._TP_TX_STATUS != self.TP_WAITING:
                    return
                self._unpack_fc_cts(msg.data[5:8])
                self._req_event.set()
            elif pdu_type == self.FR_FC_ACK_RET:
                if self._CL_STATUS != self.TP_CL_TX:
                    return
                if self.ack == 0:
                    return
                if self.ReqIndex != len(self.ReqBuf):
                    return
                fc_ack = msg.data[5]
                if fc_ack == 0:
                    self._CL_STATUS = self.TP_CL_IDLE
                    self._TP_TX_STATUS = self.TP_WAITING
                elif fc_ack == 1:
                    self._unpack_fc_ret(msg.data[6:8])
                self._req_event.set()
            elif pdu_type == self.FR_FC_WAIT:
                if self._CL_STATUS != self.TP_CL_TX or self._TP_TX_STATUS != self.TP_WAITING:
                    return
                self._req_event.set()
            elif pdu_type == self.FR_FC_ABT:
                if self._CL_STATUS != self.TP_CL_TX:
                    return
                self.error_str =  'Transmit was aborted by receiver.'
                self._CL_STATUS = self.TP_CL_IDLE
                self._TP_TX_STATUS = self.TP_WAITING
                self._req_event.set()
            elif pdu_type == self.FR_FC_OVER_FLOW:
                if self._CL_STATUS != self.TP_CL_TX:
                    return
                self.error_str = 'Receive buffer over flow error.'
                self._CL_STATUS = self.TP_CL_IDLE
                self._TP_TX_STATUS = self.TP_WAITING
                self._req_event.set()
            elif pdu_type == self.FR_LF:
                if self._CL_STATUS != self.TP_CL_RX or self._TP_RX_STATUS != self.TP_WAITING:
                    return
                FPL = msg.data[5]
                RX_ML = (msg.data[6] << 8) + msg.data[7]
                self._unpack_lf(FPL, RX_ML, msg.data[8:])
                self._resp_event.set()
    def _unpack_stf(self,FPL, data):
        if FPL <= self.rx_max_stf_length and self.RX_ML >= FPL:
            self._rx_retry_count=0
            self.RespBuf = list(data[:FPL])
            self.SN = 0x01
            if self.RX_ML == 0 or self.RX_ML > FPL:
                self._phy_send_once(self.FC_CTS_PCI)
                self._PduState = self.PDU_TYPE_MF
                self._CL_STATUS = self.TP_CL_RX
                self._TP_RX_STATUS = self.TP_WAITING
            elif self.RX_ML == FPL:
                if self.rx_ack == 1:
                    self._CL_STATUS = self.TP_CL_RX
                    self._TP_RX_STATUS = self.TP_SENDING
                    self._phy_send_once(self.FC_ACK_PCI)
                else:
                    self._CL_STATUS =self.TP_CL_IDLE
                    self._PduState = self.PDU_TYPE_SF

    def _unpack_fc_cts(self, data):
        self.MNPC = (data[0] >> 3) & 0x1F
        self.SC = 2 ** (data[0] & 0x07) - 1
        self.RX_BFS = (data[1] << 8) + data[2]
        if self.RX_BFS == 0:
            self.RX_BFS = 65536
        self._PduState = self.PDU_TYPE_FC
        self._TP_TX_STATUS = self.TP_SENDING
        self._last_fr_cycle = self._fr_cycle
    def _unpack_fc_ret(self, data):
        BP = (data[0] << 8) + data[1]
        self._rx_retry_count += 1
        if self._rx_retry_count <= self.TX_MAX_RETRY:
            if BP < len(self.ReqBuf):
                self._tx_cf_toggle = self.FR_CF2 if self._tx_cf_toggle == self.FR_CF1 else self.FR_CF1
                self.ReqIndex = BP
                self.SN = 0
                self._TP_TX_STATUS = self.TP_SENDING
            else:
                self._CL_STATUS = self.TP_CL_IDLE
                self._TP_TX_STATUS = self.TP_WAITING
                self.error_str = 'receive wrong BP value'
        else:
            self.error_str = 'TX Retry over max number'
            self._CL_STATUS = self.TP_CL_IDLE
            self._TP_TX_STATUS = self.TP_WAITING
    def _unpack_cf(self, FPL, data):
        self.RespBuf += list(data[:FPL])
        #self._PduState = self.PDU_TYPE_CF

    def _unpack_lf(self, FPL,RX_ML, data):
        if FPL <= self.rx_max_lf_length:
            if self.RX_ML == 0:
                self.RX_ML = RX_ML
            if self.RX_ML == FPL + len(self.RespBuf) and self.RX_ML == RX_ML:
                self.RespBuf += list(data[:FPL])
                if self.rx_ack == 1:
                    self._TP_RX_STATUS = self.TP_SENDING
                    self._phy_send_once(self.FC_ACK_PCI)
                else:
                    self._CL_STATUS = self.TP_CL_IDLE
                    self._PduState = self.PDU_TYPE_LF
            else:
                if self.rx_ack == 1:
                    self._TP_RX_STATUS = self.TP_SENDING
                    self._phy_send_once(self.FC_ABT_PCI)
                else:
                    self._CL_STATUS = self.TP_CL_IDLE
                    self._PduState = self.PDU_TYPE_LF
                self.error_str = 'The receive message length is wrong.'

    def _sn_error_ret(self):
        if self.rx_ack == 1:
            self.SN = 0
            self._rx_retry_count += 1
            self._rx_cf_toggle = self.FR_CF2 if self._rx_cf_toggle == self.FR_CF1 else self.FR_CF1
            if self._rx_retry_count <= self.RX_MAX_RETRY:
                BP = len(self.RespBuf)
                RET_PCI = [self.FR_FC_ACK_RET, self.FR_FC_RET,
                           (BP >> 8) & 0xFF, BP & 0xFF]
                self._phy_send_once(RET_PCI)
            else:
                self.error_str = 'receive retry over max number'
                self._CL_STATUS = self.TP_CL_IDLE
        else:
            self.error_str = 'error SN transmit abort'
            self._CL_STATUS = self.TP_CL_IDLE

    def _phy_send_once(self, pci=[], data=[]):
        self.FrameBuf = self._phy_addr_pad + pci + data
        self._message = self._pack_frame(self.FrameBuf)
        self._sending_once = True

    def _func_send_once(self, pci=[], data=[]):
        self.FrameBuf = self._func_addr_pad + pci + data
        self._message = self._pack_frame(self.FrameBuf, tx_slot=self.tx_slots[1])
        self._sending_once = True

    def _pack_frame(self, buf, tx_slot=None):
            sbuf = buf[:]
            if tx_slot is None:
                tx_slot=self.tx_slots[0]
            msg = FrFrame(**tx_slot, data=sbuf, single_shot=True)
            return msg
