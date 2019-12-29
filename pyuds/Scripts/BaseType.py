# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 21:03:23 2019

@author: levy.he
"""


class TpBase(object):
    def SendFuncReq(self, data):
        pass
    def SendPhyReq(self, data):
        pass
    def WaitResponse(self, timeout):
        pass
    def WaitReserverMsg(self):
        pass
    def sender(self):
        pass
    def reader(self):
        pass

class BusBase(object):
    def send(self):
        pass
    def recv(self):
        pass
    def send_periodic(self):
        pass
    def flush_tx_buffer(self):
        pass
    def shutdown(self):
        pass

class ComBase(object):
    def start(self):
        pass
    def stop(self):
        pass
    def add_sender(self, sender):
        pass
    def add_reader(self, reader):
        pass
    def wait(self, timeout):
        pass
    def SendOnce(self, msg):
        pass

class DiagClientBase(object):

    def diagRequest(self, buf):
        pass

    def diagFuncRequest(self, buf):
        pass

    def diagWaitResponse(self):
        pass

    def StartTesterPresent(self):
        pass

    def StopTesterPresent(self):
        pass

class DiagRequest(object):

    def diagSendRequest(self, data=None):
        pass
    def diagSendFuncRequest(self, data=None):
        pass
    def diagWaitResponse(self):
        pass
    def StartTesterPresent(self):
        pass
    def StopTesterPresent(self):
        pass

class DiagResponse(object):

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

class BaseDiagnostic(object):

    def diagDelay(self, seconds):
        pass
    def diagRawRequest(self, *cmd):
        return DiagResponse()
    def diagFuncRequest(self, *cmd):
        return DiagResponse()
    def SessionControl(self, session):
        return DiagResponse()
    def ECUReset(self, _type):
        return DiagResponse()
    def ClearDiagnosticInformation(self, group=0xFFFFFF):
        return DiagResponse()
    def ReadDtcInformation(self, SubFunc, *arg):
        return DiagResponse()
    def ReadDataByIdentifier(self, *did):
        return DiagResponse()
    def ReadMemoryByAddress(self, Format, Address, Length):
        return DiagResponse()
    def SecurityAccess(self, SubFunc, *Seed):
        return DiagResponse()
    def CommunicationControl(self, State, CommType):
        return DiagResponse()
    def ReadDataByPeriodicIdentifier(self, mode, *did):
        return DiagResponse()
    def DynamicallyDefineDataIdentifier(self, *arg):
        return DiagResponse()
    def WriteDataByIdentifier(self, DID, *DataRecord):
        return DiagResponse()
    def InputOutputControlByIdentifier(self, DID, Option, *ControlState):
        return DiagResponse()
    def RoutineControl(self, SubFunc, RID, *ControlState):
        return DiagResponse()
    def RequestDownload(self, DataFormat, Format, Address, Length):
        return DiagResponse()
    def RequestUpload(self, DataFormat, Format, Address, Length):
        return DiagResponse()
    def TransferData(self, Counter, *data):
        return DiagResponse()
    def RequestTransferExit(self, *param):
        return DiagResponse()
    def WriteMemoryByAddress(self, Format, Address, Length, *data):
        return DiagResponse()
    def TesterPresent(self, SubFunc):
        return DiagResponse()
    def ControlDTCSetting(self, SubFunc):
        return DiagResponse()

class Message(object):

    def __init__(self,*args, **kwargs):
        pass


class DBPaser(object):
    def __init__(self, db_path=None):
        pass
    def get_db_msg(self, name):
        pass
    def get_db_msgs_all(self):
        pass


class TesterBase(object):
    def __init__(self, client, keygen=None):
        pass

    def BaseDiagRequest(self, diag_name, *arg, desc=None, IsCheck=False):
        return DiagResponse()

    def WaitMs(self, ms):
        pass
    def AddDescription(self, desc):
        pass

    def LogMessage(self, msg, desc=None):
        return msg

    def SessionControl(self, session, desc=None, IsCheck=True):
        return DiagResponse()

    def ECUReset(self, _type, desc=None, IsCheck=True):
        return DiagResponse()

    def ClearDiagnosticInformation(self, SubFunc, *arg, desc=None, IsCheck=True):
        return DiagResponse()

    def ReadDtcInformation(self, SubFunc, *arg, desc=None, IsCheck=True):
        return DiagResponse()

    def ReadDataByIdentifier(self, *did, desc=None, IsCheck=True):
        return DiagResponse()

    def ReadMemoryByAddress(self,
                            Format,
                            Address,
                            Length,
                            desc=None,
                            IsCheck=True):
        return DiagResponse()

    def SecurityAccess(self, SubFunc, *Seed, desc=None, IsCheck=True):
        return DiagResponse()

    def CommunicationControl(self, State, CommType, desc=None, IsCheck=True):
        return DiagResponse()

    def ReadDataByPeriodicIdentifier(self, mode, *did, desc=None,
                                     IsCheck=True):
        return DiagResponse()

    def DynamicallyDefineDataIdentifier(self, *cmd, desc=None, IsCheck=True):
        return DiagResponse()

    def WriteDataByIdentifier(self, DID, *DataRecord, desc=None, IsCheck=True):
        return DiagResponse()

    def InputOutputControlByIdentifier(self,
                                       DID,
                                       Option,
                                       *ControlState,
                                       desc=None,
                                       IsCheck=True):
        return DiagResponse()

    def RoutineControl(self,
                       SubFunc,
                       RID,
                       *ControlState,
                       desc=None,
                       IsCheck=True):
        return DiagResponse()

    def RequestDownload(self,
                        DataFormat,
                        Format,
                        Address,
                        Length,
                        desc=None,
                        IsCheck=True):
        return DiagResponse()

    def RequestUpload(self,
                      DataFormat,
                      Format,
                      Address,
                      Length,
                      desc=None,
                      IsCheck=True):
        return DiagResponse()

    def TransferData(self, Counter, *data, desc=None, IsCheck=True):
        return DiagResponse()

    def RequestTransferExit(self, *param, desc=None, IsCheck=True):
        return DiagResponse()
    def WriteMemoryByAddress(self,
                             Format,
                             Address,
                             Length,
                             *data,
                             desc=None,
                             IsCheck=True):
        return DiagResponse()

    def TesterPresent(self, SubFunc, desc=None, IsCheck=True):
        return DiagResponse()

    def ControlDTCSetting(self, SubFunc, desc=None, IsCheck=True):
        return DiagResponse()
    def UdsRawRequest(self, *cmd, desc=None, IsCheck=False):
        return DiagResponse()

    def UdsFuncRequest(self, *cmd, desc=None, IsCheck=False):
        return DiagResponse()

    def UdsUnlock(self, level, desc=None, IsCheck=True):
        return DiagResponse()

    def GetSecurityKey(self, seed_level, seed):
        return DiagResponse()


    def ReadDtcByMaskStatus(self, mask, IsCheck=True):
        return DiagResponse()

    def AssertPositiveResponse(self, resp, desc=None):
        return True

    def AssertNegativeResponse(self, resp, desc=None):
        return True

    def AssertNRC(self, resp, nrc, desc=None):
        return True

    def AssertNotNRC(self, resp, nrc, desc=None):
        return True

    def AssertNone(self, resp, desc=None):
        return True

    def AssertDataRecord(self, resp, data, desc=None):
        return True

    def AssertDtcStatus(self, resp, dtc, status, desc=None):
        return True

    def AssertEqual(self, actual_value, expect_value, desc=None):
        return True

    def AssertNotEqual(self, actual_value, expect_value, desc=None):
        return True

    def AssertGreater(self, actual_value, expect_value, desc=None):
        return True

    def AssertLess(self, actual_value, expect_value, desc=None):
        return True

