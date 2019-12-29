# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 12:52:34 2019

@author: levy.he
"""
import threading
import time

class DiagResponseError(Exception):
    def __init__(self, desc="Unknown Diagnostic Response Message Fromat."):
        self.desc = desc
    def __str__(self):
        return self.desc

class DiagBaseObject(object):
    HAS_SUB_SID_LIST = [0x10, 0x11, 0x19, 0x27,
                        0x28, 0x3E, 0x83, 0x84, 0x85, 0x86, 0x87]
    DATA_SRV_LIST = [0x22, 0x2E, 0x2F]
    DTC_SRV_SID = 0x19
    ROUTINE_SID = 0x31
    NRC_SID = 0x7F
    def __init__(self):
        self.RawValue=[]
    def __str__(self):
        return '[%d]'%(len(self.RawValue))+'['+','.join(['%02X'%(i) for i in self.RawValue])+']'
    def __repr__(self):
        return '[%d]'%(len(self.RawValue))+'['+','.join(['%02X'%(i) for i in self.RawValue])+']'
    def __format__(self, format_spec):
        if not format_spec:
            return self.__str__()
        else:
            raise ValueError("non empty format_specs are not supported")
    def __len__(self):
        return len(self.RawValue)
    def __list__(self):
        return list(self.RawValue)
    def __copy__(self):
        super.__copy__()


class DiagRequest(DiagBaseObject):

    __slots__ = (
        "ReqSID",
        "SubFunction",
        "DID",
        "DataRecord",
        "RawValue",
        "SPRMIB",
        "uds_client",
    )

    def __init__(self, buf=[], uds_client=None):
        self.uds_client = uds_client
        self.RawValue = []
        self.ReqSID = 0
        self.SubFunction = None
        self.DataRecord = None
        self.DID = None
        self.SPRMIB = 0
        self._pack_diag_request(buf)

    def _pack_diag_request(self,buf):
        if type(buf) is list and len(buf) > 0:
            self.RawValue = buf[:]
            self.ReqSID = buf[0]
            if len(buf) > 1 and self.ReqSID in self.HAS_SUB_SID_LIST:
                self.SubFunction = buf[1] & 0x7F
                if buf[1] & 0x80 == 0x80:
                    self.SPRMIB = 1
                if len(buf) > 2:
                    self.DataRecord = buf[2:]
            elif self.ReqSID == 0x22 and len(buf) >= 3:
                self.DID = []
                for i in range(1, len(buf), 2):
                    if (i+1) < len(buf):
                        self.DID.append((buf[i] << 8) + buf[i + 1])
            elif self.ReqSID == 0x31 and len(buf) >= 4:
                self.SubFunction = buf[1] & 0x7F
                if buf[1] & 0x80 == 0x80:
                    self.SPRMIB = 1
                self.DID = (buf[2] << 8) + buf[3]
                self.DataRecord = buf[4:]
            elif (self.ReqSID == 0x2F or self.ReqSID == 0x2E) and len(buf) >= 3:
                self.DID = (buf[1] << 8) + buf[2]
                self.DataRecord = buf[3:]
            else:
                self.DataRecord = buf[1:]

    def getTpAddrInfo(self):
        return self.uds_client.getTpAddrInfo()

    def getTpName(self):
        return self.uds_client.getTpName()

    def UpdateRawValue(self, buf):
        self._pack_diag_request(buf)

    def diagSendRequest(self, *data):
        if len(data) > 0:
            self._pack_diag_request(list(data))
        self.uds_client.diagRequest(self.RawValue)

    def diagSendFuncRequest(self, *data):
        if len(data) > 0:
            self._pack_diag_request(list(data))
        self.uds_client.diagFuncRequest(self.RawValue)

    def diagWaitResponse(self):
        buf = self.uds_client.diagWaitResponse()
        if buf is not None:
            return DiagResponse(buf,self.uds_client)

    def StartTesterPresent(self):
        self.uds_client.StartTesterPresent()

    def StopTesterPresent(self):
        self.uds_client.StopTesterPresent()


class DiagResponse(DiagBaseObject):

    __slots__ = (
        "ReqSID",
        "RespSID",
        "SubFunction",
        "DID",
        "DataRecord",
        "NRC",
        "RawValue",
        "IsPositiveResponse",
        "uds_client",
        'IsExtendedResponse'
    )

    def __init__(self, buf=[], uds_client=None):
        self.uds_client = uds_client
        self.RawValue = []
        self.ReqSID = None
        self.RespSID = None
        self.SubFunction = None
        self.DataRecord = None
        self.DID = None
        self.IsPositiveResponse = None
        self.NRC = None
        self.IsExtendedResponse = False
        self._pack_diag_response(buf)

    def _pack_diag_response(self, buf):
        self.IsExtendedResponse = False
        if type(buf) is list and len(buf) > 0:
            self.RawValue = buf[:]
            if buf[0] == 0x7F:
                self.IsPositiveResponse = False
                if len(buf) == 3:
                    self.NRC = buf[2]
                    self.ReqSID = buf[1]
                    self.RespSID = buf[0]
                else:
                    raise DiagResponseError()
            else:
                self.IsPositiveResponse = True
                self.RespSID = buf[0]
                self.ReqSID = self.RespSID - 0x40
                if len(buf) >= 2 and self.ReqSID in self.HAS_SUB_SID_LIST:
                    self.SubFunction = buf[1] & 0x7F
                    self.DataRecord = buf[2:]
                elif self.ReqSID == 0x22 and len(buf) >= 3:
                    self.DID = (buf[1] << 8) + buf[2]
                    self.DataRecord = buf[3:]
                elif self.ReqSID == 0x31 and len(buf) >= 4:
                    self.SubFunction = buf[1] & 0x7F
                    self.DID = [(buf[2] << 8) + buf[3]]
                    self.DataRecord = buf[4:]
                elif (self.ReqSID == 0x2F or self.ReqSID == 0x2E) and len(buf) >= 3:
                    self.DID = [(buf[1] << 8) + buf[2]]
                    self.DataRecord = buf[3:]
                else:
                    self.DataRecord = buf[1:]
            if self.uds_client is not None and self.uds_client.N78RepeatCount > 0:
                self.IsExtendedResponse = True

class DiagClient(object):

    '''
    @tp_protocol, a type of Instance in [CanTp, FrTp,CanFdTp]
    @P2Max,P2ExMax,S3ClientTime, see iso14229 shall be float value and the unit was seconds
    @tester_type, 0 tester Present send by phy request, 1 tester Present send by func request
    @tester_msg, the message that send by the tester present services
    '''

    def __init__(self, tp_protocol, P2Max=0.2, P2ExMax=5.0, S3ClientTime=2.0, tester_type=1, tester_msg=[0x3E, 0x80], N78MaxRepeat=10):
        self.tp_protocol = tp_protocol
        self.P2Max = P2Max
        self.P2ExMax = P2ExMax
        self.S3ClientTime = S3ClientTime
        self.N78MaxRepeat = N78MaxRepeat
        self.N78RepeatCount = 0
        self._lock = threading.Lock()
        self._tester_event = threading.Event()
        self._wait_event = threading.Event()
        self._tester_thread = None
        self._is_tester_present = False
        self._tester_msg = {"Type": tester_type, "Msg": tester_msg[:]}
    
    def getTpAddrInfo(self):
        return self.tp_protocol.GetAddrInfo()

    def getTpName(self):
        return self.tp_protocol.GetTpName()

    def diagRequest(self, buf):
        with self._lock:
            self.tp_protocol.SendPhyReq(buf)

    def diagFuncRequest(self, buf):
        with self._lock:
            self.tp_protocol.SendFuncReq(buf)
            
    def diagWaitResponse(self):
        self.N78RepeatCount = 0
        return self._diagWaitResponse()

    def diagDelay(self, second):
        self._wait_event.wait(second)

    def _diagWaitResponse(self, timeout=None):
        if timeout is None:
            timeout = self.P2Max
        state, buf = self.tp_protocol.WaitResponse(timeout)
        if state == self.tp_protocol.PDU_TYPE_SF:
            if len(buf) >= 3 and buf[0] == 0x7F and buf[2] == 0x78:
                self.N78RepeatCount += 1
                if self.N78RepeatCount > self.N78MaxRepeat:
                    raise DiagResponseError('NRC 0x78 response too many times')
                return self._diagWaitResponse(self.P2ExMax)
            else:
                return buf
        elif state == self.tp_protocol.PDU_TYPE_LF:
            return buf
        elif state == self.tp_protocol.PDU_TYPE_MF:
            state, buf = self.tp_protocol.WaitReserverMsg()
            return buf
        else:
            return None
    def StartTesterPresent(self):
        self._is_tester_present = True
        self._tester_thread = threading.Thread(target=self._tester_present)
        self._tester_thread.start()

    def StopTesterPresent(self):
        self._is_tester_present = False
        if self._tester_thread is not None:
            self._tester_thread.join()
            self._tester_thread = None

    def _tester_present(self):
        while self._is_tester_present:
            self._tester_event.wait(self.S3ClientTime)
            if self._tester_msg["Type"] == 0:
                with self._lock:
                    self.tp_protocol.SendPhyReq(self._tester_msg["Msg"])
                    self.tp_protocol.WaitResponse(self.P2Max)
            else:
                with self._lock:
                    self.tp_protocol.SendFuncReq([0x3E,0x80])


class BaseDiagnostic(DiagRequest):

    def diagDelay(self, seconds):
        self.uds_client.diagDelay(seconds)
    
    def diagRawRequest(self, *cmd):
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()
    def diagFuncRequest(self, *cmd):
        self.diagSendFuncRequest(*cmd)
        return self.diagWaitResponse()

    def SessionControl(self, session):
        cmd = [0x10, session]
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()
    def ECUReset(self, _type):
        cmd = [0x11, _type]
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def ClearDiagnosticInformation(self, group=0xFFFFFF):
        cmd = [0x14, (group >> 16) & 0xFF, (group >> 8) & 0xFF, group & 0xFF]
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def ReadDtcInformation(self, SubFunc, *arg):
        cmd = [0x19, SubFunc] + list(arg)
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def ReadDataByIdentifier(self, *did):
        cmd = [0x22]
        for x in did:
            cmd += [(x >> 8) & 0xFF, x & 0xFF]
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def ReadMemoryByAddress(self, Format, Address, Length):
        addr_bytes = list((Address).to_bytes(Format & 0x0F, 'big'))
        size_bytes = list((Length).to_bytes((Format >> 4) & 0x0F, 'big'))
        cmd = [0x23, Format] + addr_bytes + size_bytes
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()
    
    def SecurityAccess(self, SubFunc, *Seed):
        cmd = [0x27, SubFunc] + list(Seed)
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def CommunicationControl(self, State, CommType):
        cmd = [0x28, State, CommType]
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def ReadDataByPeriodicIdentifier(self, mode, *did):
        cmd = [0x2A, mode] + list(did)
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def DynamicallyDefineDataIdentifier(self, *arg):
        cmd = [0x23] + list(arg)
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def WriteDataByIdentifier(self, DID, *DataRecord):
        cmd = [0x2E, (DID >> 8) & 0xFF, DID & 0xFF] + list(DataRecord)
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def InputOutputControlByIdentifier(self, DID, Option, *ControlState):
        cmd = [0x2F, (DID >> 8) & 0xFF, DID & 0xFF, Option] + list(ControlState)
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def RoutineControl(self, SubFunc, RID, *ControlState):
        cmd = [0x31, SubFunc, (RID >> 8) & 0xFF, RID & 0xFF] + list(ControlState)
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def RequestDownload(self, DataFormat, Format, Address, Length):
        addr_bytes = list((Address).to_bytes(Format & 0x0F, 'big'))
        size_bytes = list((Length).to_bytes((Format >> 4) & 0x0F, 'big'))
        cmd = [0x34, DataFormat, Format] + addr_bytes + size_bytes
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def RequestUpload(self, DataFormat, Format, Address, Length):
        addr_bytes = list((Address).to_bytes(Format & 0x0F, 'big'))
        size_bytes = list((Length).to_bytes((Format >> 4) & 0x0F, 'big'))
        cmd = [0x35, DataFormat, Format] + addr_bytes + size_bytes
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def TransferData(self, Counter, *data):
        cmd = [0x36, Counter] + list(data)
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def RequestTransferExit(self, *param):
        cmd = [0x37] + list(param)
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def WriteMemoryByAddress(self, Format, Address, Length, *data):
        addr_bytes = list((Address).to_bytes(Format & 0x0F, 'big'))
        size_bytes = list((Length).to_bytes((Format >> 4) & 0x0F, 'big'))
        cmd = [0x3D, Format] + addr_bytes + size_bytes + list(data)
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def TesterPresent(self, SubFunc):
        cmd = [0x3E, SubFunc]
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()

    def ControlDTCSetting(self, SubFunc):
        cmd = [0x85, SubFunc]
        self.diagSendRequest(*cmd)
        return self.diagWaitResponse()
