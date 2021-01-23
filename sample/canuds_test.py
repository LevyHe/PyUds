# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 23:12:01 2019

@author: levy.he
"""
from pyuds.PyUds import CanBus, ComCan, CanTp, DiagRequest, DiagClient, ThreadSafety, BaseDiagnostic
from pyuds.Scripts import InternalKeyGen
from pyuds.PyUds import MessageLog

if __name__ == '__main__':
    can = CanBus(app_name='CANalyzer', channel=0, bitrate=500000)
    can_bus = ComCan(can)
    can_tp = CanTp(phy_id=0x1A000020, func_id=0x7DF, resp_id=0x1A000021)
    uds_client = DiagClient(can_tp)
    diag = BaseDiagnostic(uds_client=uds_client)
    can_bus.add_sender(can_tp.sender)
    can_bus.add_reader(can_tp.reader)
    key_gen = InternalKeyGen(0x61)
    MessageLog.start(log_level=3)
    can_bus.set_filters(filters=[0x1A000020,0x1A000021])
    with ThreadSafety(can_bus):
        for i in range(100):
            print("current test count %d"%(i))
            resp = diag.SessionControl(0x03)
            print(resp)
            #print(resp)
            #dtc = diag.ReadDtcInformation(0x0A)
            #print(dtc)
            resp = diag.SecurityAccess(0x61)
            key = key_gen.KenGen(0x61, resp.DataRecord)
            diag.SecurityAccess(0x62,*key)
            resp = diag.WriteDataByIdentifier(0xF18C, *([0x30] * 16))
            print(resp)
            if not resp.IsPositiveResponse:
                pass
            can_bus.wait(0.2)
            #dids = diag.ReadDataByIdentifier(*([0xF195] * 400))
            #print(dids)
    with ThreadSafety(can_bus):
        for i in range(100):
            print("current test count %d" % (i))
            resp = diag.SessionControl(0x03)
            print(resp)
            #print(resp)
            #dtc = diag.ReadDtcInformation(0x0A)
            #print(dtc)
            resp = diag.SecurityAccess(0x61)
            key = key_gen.KenGen(0x61, resp.DataRecord)
            diag.SecurityAccess(0x62, *key)
            resp = diag.WriteDataByIdentifier(0xF18C, *([0x30] * 16))
            print(resp)
            if not resp.IsPositiveResponse:
                pass
            can_bus.wait(0.2)
    MessageLog.stop()
