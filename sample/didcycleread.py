# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 09:10:06 2019

@author: levy.he
"""
from pyuds.PyUds import CanMsgSendOnce, CanMsgReadOnce, CanMsgReader, CanMsgSender
from pyuds.PyUds import CanBus, ComCan, ThreadSafety, BaseDiagnostic, DiagClient, CanTp
import time

if __name__ == '__main__':
    can = CanBus(app_name='CANalyzer', channel=0, bitrate=500000)
    bus = ComCan(can)
    can_tp = CanTp(phy_id=0x1A000020, func_id=0x7DF, resp_id=0x1A000021)
    uds_client = DiagClient(can_tp)
    diag = BaseDiagnostic(uds_client=uds_client)
    bus.add_sender(can_tp.sender)
    bus.add_reader(can_tp.reader)
    ms_count = 0
    with ThreadSafety(bus):
        ReadOnce = CanMsgReadOnce(bus, timeout=0.2, arbitration_id=0x1AE)
        while True:
            resp = diag.ReadDataByIdentifier(0x1000)
            if resp is not None:
                voltage = resp.DataRecord[0]
                if voltage < 60:
                    print("current volatge is %0.1f V"%(voltage/10.0))
                    break
        power_down_time = time.time()
        for i in range(200):
            resp = diag.ReadDataByIdentifier(0xFD3E)
            resp2 = diag.ReadDataByIdentifier(0xFDBA)
            if resp is not None:
                Er_voltage =0
                Er_voltage = int.from_bytes(bytes(resp.DataRecord),byteorder="big")
                print('%0.3f'%(time.time()-power_down_time), "%0.2f"%(Er_voltage*0.0368),resp2.DataRecord[0])
            else:
                break
            
#        while True:
#            msg = ReadOnce(2)
#            if msg is not None:
#                ms_count += 20
#            else:
#                break
#    print('message stop send time is %d ms' % (ms_count))

