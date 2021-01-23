# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 14:29:55 2019

@author: levy.he
"""

from pyuds.PyUds import CanMsgSendOnce, CanMsgReadOnce, CanMsgReader, CanMsgSender
from pyuds.PyUds import CanBus, ComCan, ThreadSafety, BaseDiagnostic, DiagClient, CanTp

if __name__ == '__main__':
    can = CanBus(app_name='CANalyzer', channel=0, bitrate=500000)
    bus = ComCan(can)
    can_tp = CanTp(phy_id=0x727, func_id=0x7DF, resp_id=0x7A7)
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
        
        while True:
            msg = ReadOnce(2)
            if msg is not None:
                ms_count += 20
            else:
                break
    print('message stop send time is %d ms' % (ms_count))

