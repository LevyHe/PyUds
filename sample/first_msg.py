# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 09:16:28 2019

@author: levy.he
"""


from pyuds.PyUds import CanMsgSendOnce, CanMsgReadOnce, CanMsgReader, CanMsgSender
from pyuds.PyUds import CanBus, ComCan, ThreadSafety, BaseDiagnostic, DiagClient, CanTp
from pyps.agilent import E364xA
import time

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
        start_time = time.time()
        # aiglent = E364xA("COM6")
        # aiglent.reset()
        # aiglent.setonoff(False)
        # bus.wait(4)
        resp = diag.ECUReset(1)
        start_time = time.time()
        while ReadOnce(0.03):
            pass
            # start_time = time.time()
        # aiglent.setonoff(True)
        # start_time = time.time()
        msg = ReadOnce(2)
        revc_time = time.time()
        # del aiglent
        if msg is not None:
            print("First Message 0x1AE Send time is: %0.3f" %
                  (revc_time-start_time))
        else:
            raise Exception("Message was not send")
