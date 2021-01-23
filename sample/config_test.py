# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 16:10:22 2019

@author: levy.he
"""

from pyuds import PyUds
from pyuds import Scripts
from pyuds.PyUds import ThreadSafety
import time
if __name__ == '__main__':
    config = Scripts.UdsConfigParse('UdsConfig.json')
    bus = config.GetBus('CanBus1')
    diag = config.GetUdsDiag('CanPhy')
    ACU_SRS_1 = config.GetMessage('ACU_SRS_1')
    BCS_2 = config.GetMessage('BCS_2')
    SRS1_SyncRead = config.GetMessage('SRS1_SyncRead')
    BCS2_SendOnce = config.GetMessage('BCS2_SendOnce')
    Msg_SRS1_Cycle = config.GetMessage('Msg_SRS1_Cycle')
    Msg_SRS1_ReadOnce = config.GetMessage('Msg_SRS1_ReadOnce')
    Msg_BCS2_Cycle = config.GetMessage('Msg_BCS2_Cycle')
    Msg_BCS2_SendOnce = config.GetMessage('Msg_BCS2_SendOnce')
    with ThreadSafety(bus):
        resp = diag.SessionControl(0x01)
        print("SessionControl Response", resp)
        resp = diag.diagFuncRequest(0x10, 0x03)
        print("Functional Request Response", resp)
        ACU_SRS_1.start()
        for i in range(100):
            bus.wait(0.02)
            print("SRS_MsgCounter", ACU_SRS_1['SRS_MsgCounter'])
        BCS_2.start()
        bus.wait(2.0)
        BCS_2.stop()
        bus.wait(1.0)
        srs1 = SRS1_SyncRead()
        print("SRS1_SyncRead\n",srs1)
        BCS2_SendOnce()
        print("BCS2_SendOnce\n",BCS2_SendOnce)
        Msg_SRS1_Cycle.start()
        bus.wait(0.02)
        for i in range(100):
            bus.wait(0.02)
            print("Msg_SRS1_Cycle",Msg_SRS1_Cycle.data[6])
        srs1 = Msg_SRS1_ReadOnce()
        print("Msg_SRS1_ReadOnce\n",srs1)
        srs1 = Msg_SRS1_ReadOnce()
        print("Msg_SRS1_ReadOnce\n",srs1)
        srs1 = Msg_SRS1_ReadOnce()
        print("Msg_SRS1_ReadOnce\n",srs1)
        srs1 = Msg_SRS1_ReadOnce()
        print("Msg_SRS1_ReadOnce\n",srs1)
        Msg_BCS2_Cycle.start()
        bus.wait(2.0)
        Msg_BCS2_Cycle.stop()
        bus.wait(1.0)
        Msg_BCS2_SendOnce()
        print("Msg_BCS2_SendOnce\n",Msg_BCS2_SendOnce)
