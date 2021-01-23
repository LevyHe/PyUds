# -*- coding: utf-8 -*-
"""
Created on Fri May 10 21:12:49 2019

@author: levy.he
"""
import traceback
import time
from pyuds import PyUds
from pyuds import Scripts
from pyuds.TestCase import UdsLoging, html_report

class ReportTest(object):
    def __init__(self, diag):
        self.diag = diag

    @UdsLoging(test_level=0)
    def SessionControl(self, session, desc=None):
        step_desc = 'SessionControl'
        resp = PyUds.DiagResponse([0x50, 0x01, 0x00, 0x0A, 0x00, 0x20])
        this = ReportTest.SessionControl
        this.desc = step_desc
        return resp

    @UdsLoging(test_level=0)
    def UdsRawRequest(self, *cmd, desc=None):
        req_raw=list(cmd)
        self.diag.UpdateRawValue(req_raw)
        resp = PyUds.DiagResponse([0x51,0x01])
        step_desc = 'Send Uds Request '
        ReportTest.UdsRawRequest.desc = step_desc
        return resp

    @UdsLoging(test_level=0)
    def UdsNegRequest(self, *cmd, desc=None):
        req_raw = list(cmd)
        self.diag.UpdateRawValue(req_raw)
        resp = PyUds.DiagResponse([0x7F, 0x11, 0x31])
        step_desc = 'Send Neg Request '
        ReportTest.UdsRawRequest.desc = step_desc
        return resp

    @UdsLoging(test_level=0,test_type=3)
    def Message_test(self):
        msg = PyUds.Message(arbitration_id=0x182, data=[0x00] * 8)
        step_desc = 'can message send'
        __class__.Message_test.desc = step_desc
        return msg

    @UdsLoging(test_level=0,test_type=3)
    def Frame_test(self):
        msg = PyUds.FrFrame(slot_id=77, base_cycle=0, repetition_cycle=2, data=[0x00] * 32)
        step_desc = 'frmae send'
        __class__.Frame_test.desc = step_desc
        return msg
    
    @UdsLoging(test_level=1)
    def SubSteptest(self):
        self.UdsRawRequest(0x10,0x01)
        self.Message_test()
        self.Frame_test()
        resp = self.SessionControl(0x02)
        return resp    

    @UdsLoging(test_level=0, func_request=True)
    def UdsFuncRequest(self, *cmd, desc=None):
        req_raw = list(cmd)
        self.diag.UpdateRawValue(req_raw)
        step_desc = 'Send Uds Request '
        ReportTest.UdsFuncRequest.desc = step_desc
        return None
    
    @UdsLoging(test_level=5)
    def TestGroup1(self, desc=None):
        self.TestSuite1()
        self.TestSuite1()
        self.nodesc_testsuite()

    @UdsLoging(test_level=5)
    def TestGroup2(self, desc=None):
        pass

    #@UdsLoging(test_level=4)
    def TestSuite1(self, desc=None):
        self.msg_test_case()
        self.TestCase1()
        self.TestCase2()
        ReportTest.TestSuite1.desc = 'TestSuite1'

    @UdsLoging(test_level=4)
    def nodesc_testsuite(self, desc=None):
        self.setUpTest()
        self.TestCase1()
        self.TestCase2()
        

    @UdsLoging(test_level=3)
    def setUpTest(self, desc=None):
        self.UdsFuncRequest(0x3E, 0x00)
        self.TestStep1()


    @UdsLoging(test_level=3)
    def TestCase1(self, desc=None):
        self.UdsFuncRequest(0x3E,0x00)
        resp = self.TestStep1()
        self.AssertPositiveResponse(resp)

    @UdsLoging(test_level=3)
    def msg_test_case(self, desc=None):
        self.Message_test()
        self.Frame_test()
        self.SubSteptest()
        resp = self.TestStep1()
        self.AssertPositiveResponse(resp)

    @UdsLoging(test_level=3)
    def TestCase2(self, desc=None):
        ReportTest.TestCase2.desc = 'TestCase2'
        self.SessionControl(0x01)
        resp = self.UdsFuncRequest(0x3E,0x80)
        self.AssertNone(resp)
        self.Message_test()
        self.Frame_test()
        self.SubSteptest()
        resp = self.TestStep1()
        self.AssertPositiveResponse(resp)

    @UdsLoging(test_level=1)
    def TestStep1(self, desc=None):
        self.SessionControl(0x01)
        resp = self.UdsRawRequest(0x11, 0x01)
        ReportTest.TestStep1.desc = 'TestStep1'
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
        this = ReportTest.AssertPositiveResponse
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
        this = ReportTest.AssertNegativeResponse
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
        this = ReportTest.AssertNone
        this.desc = step_desc
        this.expect = expect
        this.actual = actual
        this.result = result
        return result
try:
    config = Scripts.UdsConfigParse('UdsConfig.json')
    start_time=time.time()
    bus = PyUds.BusBase()
    tp = PyUds.CanTp(phy_id=0x727,
                     func_id=0x7DF,
                     resp_id=0x7A7,)
    client = PyUds.DiagClient(tp_protocol=tp)
    diag = PyUds.BaseDiagnostic(uds_client=client)
    tester = ReportTest(diag=diag)
    tester.TestGroup2()
    tester.TestGroup1()
    
    test_list = UdsLoging.test_group
    test_result = UdsLoging.get_all_result()
    end_time = time.time()
    test_info = [
        'Test Environment Overview',
        'Test Software: python 3.7',
        'Test Hardware:',
        'b)      DC Power Supply',
        'a)      VN7600',
        'Test Setup:',
        'a)      Turn on Power Supply for the test box / module and set the voltage = 13 volts and the current = 4 amps.',
        'b)      Turn power on to the Test Box.',
        'c)      Start the CAN Tool.'
    ]
    test_detail = 'Reference: /206298 Chinese OEM GAC A39 EL ECU RC GAC A39 RCS/30_DES_Requirements/DES_SW_Requirements/DES_GAC_A39_CANDDiagnostics'
    report = html_report('test_report.html')
    report.test_report(test_list, test_result, start_time, end_time,
                       title='test template report',
                       test_info=test_info,
                       test_detail=test_detail)
except:
    traceback.print_exc()
finally:
    pass
