# -*- coding: utf-8 -*-
"""
Created on Fri May 5 20:13:59 2019

@author: levy.he
"""
import time
from .Report.UdsLog import UdsLoging


def list_to_hex_str(data):
    return ' '.join(['%02X' % (x) for x in data])

class TesterBase(object):
    '''
    @client, the class of BaseDiagnostic
    @keygen, the class of BaseKeyGen
    '''
    def __init__(self, client, keygen=None):
        self.diag = client
        self.keygen = keygen
        self.base_step = []
        self.base_count = 0
        self.sub_test = None
        self.sub_step = 0

    @UdsLoging(test_level=0)
    def BaseDiagRequest(self, diag_name, *arg, desc=None, IsCheck=False):
        request = self.diag.__getattribute__(diag_name)
        resp = request(*arg)
        if desc is None:
            desc = diag_name
        TesterBase.BaseDiagRequest.desc = desc
        TesterBase.BaseDiagRequest.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0, test_type=1)
    def WaitMs(self, ms):
        __class__.WaitMs.desc = 'Wait %d ms' % (ms)
        self.diag.diagDelay(ms/1000.)
    
    def GetCycleDiagRequestFunc(self, diag_name, resp_check_func, cycle_time=None, desc=None):
        request = self.diag.__getattribute__(diag_name)
        UdsLoging.diag = self.diag
        @UdsLoging(test_level=0)
        def caller(*args):
            time_start = time.time()
            run_time = 0
            run_count = 0
            while True:
                test_start_time = time.time()
                resp = request(*args)
                run_count += 1
                if resp_check_func(resp):
                    run_time = time.time()-time_start
                    break
                if cycle_time is not None:
                    time_left = cycle_time - (time.time() - test_start_time)
                    self.diag.diagDelay(time_left)

            if desc is not None:
                step_desc = desc + ': Count:%d, time:%d s'%(run_count, run_time)
            else:
                step_desc = diag_name +' '+ list_to_hex_str(args) + ': Count:%d, time:%d s'%(run_count, run_time) 
            caller.desc = step_desc
            resp.RequestCount = run_count
            resp.RunTime = run_time
            return resp
        return caller

    @UdsLoging(test_level=0, test_type=0)
    def AddDescription(self, desc):
        __class__.AddDescription.desc = desc

    @UdsLoging(test_level=0, test_type=4)
    def Requirements(self, desc, link=None):
        if link:
            desc = (desc, link)
        __class__.Requirements.desc = desc

    @UdsLoging(test_level=0, test_type=0)
    def StartTesterPresent(self):
        s3time = int(self.diag.uds_client.S3ClientTime * 1000)
        __class__.StartTesterPresent.desc = 'StartTesterPresent each %d ms'%(s3time)
        self.diag.StartTesterPresent()

    @UdsLoging(test_level=0, test_type=0)
    def StopTesterPresent(self):
        __class__.StopTesterPresent.desc = 'StopTesterPresent'
        self.diag.StopTesterPresent()

    @UdsLoging(test_level=0, test_type=3)
    def LogMessage(self, msg, desc=None):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'LogMessage'
        __class__.LogMessage.desc = step_desc
        return msg

    @UdsLoging(test_level=0)
    def SessionControl(self, session, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            if session <= 4:
                s_str = ['Unknown', 'Default', 'Programming', 'Extended', 'SafetySystem'][session]
            else:
                s_str = 'Other'
            step_desc = 'Change to %s Session 0x%02X' % (s_str, session)
        resp = self.diag.SessionControl(session)
        TesterBase.SessionControl.desc = step_desc
        TesterBase.SessionControl.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def ECUReset(self, _type, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            if _type <= 3:
                s_str = ['Unknown', 'Hard', 'KeyOffOn', 'Soft', ][_type]
            else:
                s_str = 'Other'
            step_desc = 'ECU  %sReset 0x%02X' % (s_str, _type)
        resp = self.diag.ECUReset(_type)
        TesterBase.ECUReset.desc = step_desc
        TesterBase.ECUReset.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def ClearDiagnosticInformation(self, group=0xFFFFFF, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'ClearDTC for group 0x%06X' % (group)
        resp = self.diag.ClearDiagnosticInformation(group)
        TesterBase.ClearDiagnosticInformation.desc = step_desc
        TesterBase.ClearDiagnosticInformation.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def ReadDtcInformation(self, SubFunc, *arg, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            if SubFunc <= 10:
                s_str = ['UnknownDTCReport', 'reportNumberOfDTC', 'reportDTC', 'reportDTCSnapshotID',
                'reportDTCSnapshotRecord', 'reportDTCStoredData', 'reportDTCExtDataRecord',
                'reportNumberOfDTCBySeverity', 'reportNumberOfDTCBySeverity', 'reportDTCBySeverity',
                'reportSeverityInformation', 'reportSupportedDTC'][SubFunc]
            else:
                s_str = 'OtherDTCReport'
            step_desc = '%s 0x%02X' % (s_str, SubFunc)
        resp = self.diag.ReadDtcInformation(SubFunc, *arg)
        TesterBase.ReadDtcInformation.desc = step_desc
        TesterBase.ReadDtcInformation.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def ReadDataByIdentifier(self, *did, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            did_str=', '.join(['0x%04X'%(x) for x in did])
            step_desc = 'Read DID %s value' % (did_str)
        resp = self.diag.ReadDataByIdentifier(*did)
        TesterBase.ReadDataByIdentifier.desc = step_desc
        TesterBase.ReadDataByIdentifier.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def ReadMemoryByAddress(self, Format, Address, Length, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'ReadMemoryByAddress'
        resp = self.diag.ReadMemoryByAddress(Format, Address, Length)
        TesterBase.ReadMemoryByAddress.desc = step_desc
        TesterBase.ReadMemoryByAddress.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)    
    def SecurityAccess(self, SubFunc, *Seed, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'RequestSeed 0x%02X' % (SubFunc)  if (SubFunc & 0x01)!=0 else 'SendKey 0x%02X' % (SubFunc)
        resp = self.diag.SecurityAccess(SubFunc, *Seed)
        TesterBase.SecurityAccess.desc = step_desc
        TesterBase.SecurityAccess.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def CommunicationControl(self, State, CommType, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            if State <= 3:
                s_str = ['EnableRxAndTx', 'EnableRxAndDisableTx', 'DisableRxAndEnableTx', 'DisableRxAndTx', ][State]
            else:
                s_str = 'Other'
            step_desc = '%sControl 0x%02X' % (s_str, State)
        resp = self.diag.CommunicationControl(State, CommType)
        TesterBase.CommunicationControl.desc = step_desc
        TesterBase.CommunicationControl.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def ReadDataByPeriodicIdentifier(self, mode, *did, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            if mode <= 4:
                mode_str = ['Reserved', 'SlowRead', 'MediumRead', 'FastRead', 'StopRead'][mode]
            else:
                mode_str = 'Reserved'
            did_str = ', '.join(['0x%02X' % (x) for x in did])
            step_desc = '%s DID %s value' % (mode_str, did_str)
        resp = self.diag.ReadDataByPeriodicIdentifier(mode, *did)
        TesterBase.ReadDataByPeriodicIdentifier.desc = step_desc
        TesterBase.ReadDataByPeriodicIdentifier.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def DynamicallyDefineDataIdentifier(self, *cmd, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'DynamicallyDefineDataIdentifier'
        resp = self.diag.DynamicallyDefineDataIdentifier(*cmd)
        TesterBase.DynamicallyDefineDataIdentifier.desc = step_desc
        TesterBase.DynamicallyDefineDataIdentifier.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def WriteDataByIdentifier(self, DID, *DataRecord, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'Write DID 0x%04X value' % (DID)
        resp = self.diag.WriteDataByIdentifier(DID, *DataRecord)
        TesterBase.WriteDataByIdentifier.desc = step_desc
        TesterBase.WriteDataByIdentifier.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def InputOutputControlByIdentifier(self, DID, Option, *ControlState, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            if Option <= 3:
                ctr_str = ['StopControl', 'ResetControl', 'FreezeControl','AdjustControl'][Option]
            else:
                ctr_str='UnknownControl'
            step_desc = '%s DID 0x%04X' % (ctr_str, DID)
        resp = self.diag.InputOutputControlByIdentifier(DID, Option, *ControlState)
        TesterBase.InputOutputControlByIdentifier.desc = step_desc
        TesterBase.InputOutputControlByIdentifier.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def RoutineControl(self, SubFunc, RID, *ControlState, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            if SubFunc <= 3:
                ctr_str = ['Unknown', 'Start', 'Stop','Result'][SubFunc]
            else:
                ctr_str='Unknown'
            step_desc = 'RoutineControl %s RID 0x%04X' % (ctr_str, RID)
        resp = self.diag.RoutineControl(SubFunc, RID, *ControlState)
        TesterBase.RoutineControl.desc = step_desc
        TesterBase.RoutineControl.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def RequestDownload(self, DataFormat, Format, Address, Length, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'RequestDownload'
        resp = self.diag.RequestDownload(DataFormat, Format, Address, Length)
        TesterBase.RequestDownload.desc = step_desc
        TesterBase.RequestDownload.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def RequestUpload(self, DataFormat, Format, Address, Length, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'RequestUpload'
        resp = self.diag.RequestUpload(DataFormat, Format, Address, Length)
        TesterBase.RequestUpload.desc = step_desc
        TesterBase.RequestUpload.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def TransferData(self, Counter, *data, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'TransferData'
        resp = self.diag.TransferData(Counter, *data)
        TesterBase.TransferData.desc = step_desc
        TesterBase.TransferData.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def RequestTransferExit(self, *param, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'RequestTransferExit'
        resp = self.diag.RequestTransferExit(*param)
        TesterBase.RequestTransferExit.desc = step_desc
        TesterBase.RequestTransferExit.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def WriteMemoryByAddress(self, Format, Address, Length, *data, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'WriteMemoryByAddress'
        resp = self.diag.WriteMemoryByAddress(Format, Address, Length, *data)
        TesterBase.WriteMemoryByAddress.desc = step_desc
        TesterBase.WriteMemoryByAddress.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def TesterPresent(self, SubFunc, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'TesterPresent'
        resp = self.diag.TesterPresent(SubFunc)
        TesterBase.TesterPresent.desc = step_desc
        TesterBase.TesterPresent.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def ControlDTCSetting(self, SubFunc, desc=None, IsCheck=True):
        if desc is not None:
            step_desc = desc
        else:
            if SubFunc <= 2:
                s_str = ['Unknown', 'On', 'Off' ][SubFunc]
            else:
                s_str = 'Unknown'
            step_desc = 'DTCSetting %s 0x%02X' % (s_str, SubFunc)
        resp = self.diag.ControlDTCSetting(SubFunc)
        TesterBase.ControlDTCSetting.desc = step_desc
        TesterBase.ControlDTCSetting.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0)
    def UdsRawRequest(self, *cmd, desc=None, IsCheck=False):
        resp = self.diag.diagRawRequest(*cmd)
        if resp is not None:
            req_raw = self.diag.RawValue[:]
        else:
            req_raw = []
        if desc is not None:
            step_desc = desc
        else:
            ext = ''
            if len(req_raw) > 7:
                ext = '...'
            req_p = req_raw[:7]
            step_desc = 'Send Uds Request '+' '.join(['%02X'%(x) for x in req_p]) + ext
        TesterBase.UdsRawRequest.desc = step_desc
        TesterBase.UdsRawRequest.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=0, func_request=True)
    def UdsFuncRequest(self, *cmd, desc=None, IsCheck=False):
        resp = self.diag.diagFuncRequest(*cmd)
        if resp is not None:
            req_raw = self.diag.RawValue[:]
        else:
            req_raw = []
        if desc is not None:
            step_desc = desc
        else:
            ext = ''
            if len(req_raw) > 7:
                ext = '...'
            req_p = req_raw[:7]
            step_desc = 'Send Func Request ' + ' '.join(['%02X' % (x) for x in req_p]) + ext
        TesterBase.UdsFuncRequest.desc = step_desc
        TesterBase.UdsFuncRequest.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=1)
    def UdsUnlock(self, level, desc=None, IsCheck=True):
        resp = self.SecurityAccess(level, IsCheck=IsCheck)
        if resp.DataRecord != [0x00]*(len(resp.DataRecord)):
            key = self.GetSecurityKey(level,resp.DataRecord)
            resp = self.SecurityAccess(level + 1, *key, IsCheck=IsCheck)
        if desc is not None:
            step_desc = desc
        else:
            step_desc = 'UnLock Security Level %02X' % (level)
        this = TesterBase.UdsUnlock
        this.desc = step_desc
        this.IsCheck = IsCheck
        return resp

    def GetSecurityKey(self, seed_level, seed):
        if self.keygen is not None:
            return self.keygen(seed_level, seed)[:len(seed)]
        else:
            return seed

    def _dtc_status_pack(self, buf):
        if len(buf) < 4:
            return (0, 0)
        dtc = (buf[0] << 16) + (buf[1] << 8) + buf[2]
        status = buf[3]
        return {dtc:status}

    @UdsLoging(test_level=0)
    def ReadDtcByMaskStatus(self, mask, IsCheck=True):
        step_desc = 'ReadDtcByMaskStatus(0x%02X)' % (mask)
        resp = self.diag.ReadDtcInformation(0x02, mask)
        buf = resp.DataRecord[1:]
        dtc_list = {}
        for i in range(0, len(buf), 4):
            dtc_list.update(self._dtc_status_pack(buf[i:i + 4]))
        resp.DTCList = dtc_list
        __class__.ReadDtcInformation.desc = step_desc
        __class__.ReadDtcInformation.IsCheck = IsCheck
        return resp

    @UdsLoging(test_level=2)
    def AssertPositiveResponse(self, resp, desc=None):
        if desc is None:
            step_desc = 'Check Posistive Response'
        else:
            step_desc = desc
        expect = 'Posistive Response'
        if resp is None:
            result = False
            actual = None
        elif resp.IsPositiveResponse:
            result = True
            actual = 'Posistive Response'
        else:
            result = False
            actual = 'Negative Response %02X' % (resp.NRC)
        this = TesterBase.AssertPositiveResponse
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result

    @UdsLoging(test_level=2)
    def AssertNegativeResponse(self, resp, desc=None):
        if desc is None:
            step_desc = 'Check Negative Response'
        else:
            step_desc = desc
        expect = 'Negative Response'
        if resp is None:
            result = False
            actual = None
        elif resp.IsPositiveResponse:
            result = False
            actual = 'Posistive Response'
        else:
            result = True
            actual = 'Negative Response %02X' % (resp.NRC)
        this = TesterBase.AssertNegativeResponse
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result

    @UdsLoging(test_level=2)
    def AssertNRC(self, resp, nrc, desc=None):
        if desc is None:
            step_desc = 'Check Negative Response'
        else:
            step_desc = desc
        expect = 'Negative Response %02X' % (nrc)
        if resp is None:
            result = False
            actual = None
        elif resp.IsPositiveResponse:
            result = False
            actual = 'Posistive Response'
        elif resp.NRC == nrc:
            result = True
            actual = 'Negative Response %02X' % (resp.NRC)
        else:
            result = False
            actual = 'Negative Response %02X' % (resp.NRC)
        this = TesterBase.AssertNRC
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result

    @UdsLoging(test_level=2)
    def AssertNotNRC(self, resp, nrc, desc=None):
        if desc is None:
            step_desc = 'Check Negative Response'
        else:
            step_desc = desc
        expect = 'Not Negative Response %02X' % (nrc)
        if resp is None:
            result = False
            actual = None
        elif resp.IsPositiveResponse:
            result = True
            actual = 'Posistive Response'
        elif resp.NRC != nrc:
            result = True
            actual = 'Negative Response %02X' % (resp.NRC)
        else:
            result = False
            actual = 'Negative Response %02X' % (resp.NRC)
        this = TesterBase.AssertNRC
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result

    @UdsLoging(test_level=2)
    def AssertNone(self, resp, desc=None):
        if desc is None:
            step_desc = 'Check None Response'
        else:
            step_desc = desc
        expect = 'None Response'
        if resp is None:
            result = True
            actual = None
        elif resp.IsPositiveResponse:
            result = False
            actual = 'Posistive Response'
        else:
            result = False
            actual = 'Negative Response %02X' % (resp.NRC)
        this = TesterBase.AssertNone
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result

    @UdsLoging(test_level=2)
    def AssertDataRecord(self, resp, data, desc=None):
        if desc is None:
            step_desc = 'Check Data Record'
        else:
            step_desc = desc
        expect = list_to_hex_str(data)
        if resp is None:
            result = False
            actual = None
        elif resp.IsPositiveResponse:
            if resp.DataRecord == data:
                result = True
                actual = list_to_hex_str(data)
            else:
                result = False
                actual = list_to_hex_str(resp.DataRecord)                
        else:
            result = False
            actual = 'Negative Response %02X' % (resp.NRC)
        this = TesterBase.AssertDataRecord
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result

    @UdsLoging(test_level=2)
    def AssertDtcStatus(self, resp, dtc, status, desc=None):
        if desc is None:
            step_desc = 'Check DTC 0x%06X Status' % (dtc)
        else:
            step_desc = desc
        ac_st = resp.DTCList.get(dtc, None)
        if status is None:
            expect = 'No DTC Report'
            if ac_st is None:
                result = True
                actual = expect
            else:
                result = False
                actual = '0x%02X' % (ac_st)
        elif status == 0x00:
            expect = 'DTC is not active'
            if ac_st is None or (ac_st & 0x01) != 0x01:
                result = True
                actual = 'No DTC Report' if ac_st is None else '0x%02X' % (
                    ac_st)
            else:
                result = False
                actual = '0x%02X' % (ac_st)
        else:
            expect = '0x%02X' % (status)
            if status is ac_st:
                result = True
                actual = expect
            else:
                result = False
                actual = 'No DTC Report' if ac_st is None else '0x%02X' % (
                    ac_st)
        this = __class__.AssertDtcStatus
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result

    @UdsLoging(test_level=2)
    def AssertEqual(self, actual_value, expect_value, desc=None):
        if desc is None:
            step_desc = 'Check the response value'
        else:
            step_desc = desc
        expect = str(expect_value)
        actual = str(actual_value)
        result = True if actual_value == expect_value else False

        this = __class__.AssertEqual
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result

    @UdsLoging(test_level=2)
    def AssertNotEqual(self, actual_value, expect_value, desc=None):
        if desc is None:
            step_desc = 'Check the response value'
        else:
            step_desc = desc
        expect = '!= ' + str(expect_value)
        actual = str(actual_value)
        result = True if actual_value != expect_value else False

        this = __class__.AssertNotEqual
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result

    @UdsLoging(test_level=2)
    def AssertGreater(self, actual_value, expect_value, desc=None):
        if desc is None:
            step_desc = 'Check the response value'
        else:
            step_desc = desc
        expect = '> ' + str(expect_value)
        actual = str(actual_value)
        result = True if actual_value > expect_value else False

        this = __class__.AssertGreater
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result

    @UdsLoging(test_level=2)
    def AssertLess(self, actual_value, expect_value, desc=None):
        if desc is None:
            step_desc = 'Check the response value'
        else:
            step_desc = desc
        expect = '< '+ str(expect_value)
        actual = str(actual_value)
        result = True if actual_value < expect_value else False

        this = __class__.AssertLess
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result










