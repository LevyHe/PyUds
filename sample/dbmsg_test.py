# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 16:10:22 2019

@author: levy.he
"""

from pyuds.PyUds import DBPaser, DBMsgReader, DBMsgSender, DBMsgReadOnce
from pyuds.PyUds import CanBus, ComCan,ThreadSafety
import traceback

# from win32api import GetCurrentProcessId
# from win32process import SetPriorityClass,SetProcessPriorityBoost,GetProcessAffinityMask,THREAD_PRIORITY_TIME_CRITICAL,REALTIME_PRIORITY_CLASS

if __name__ == '__main__':
    can = CanBus(app_name='CANalyzer', channel=0, bitrate=500000)
    can2 = CanBus(app_name='CANalyzer', channel=1, bitrate=500000)
    bus = ComCan(can)
    bus2 = ComCan(can2)
    with ThreadSafety(bus,bus2):
        # print('CurrentProcessID', GetCurrentProcessId())
        db_path = 'SC2_HSCAN.DBC'
        dbc = DBPaser(db_path)
        dbs = dbc.get_db_msgs_all()
        SRS1 = dbs['ACU_SRS_1']
        SRS2 = dbs['ACU_SRS_2']
        BCS2 = dbs['BCS_2']
        SRS1_Read = DBMsgReadOnce(bus, SRS1, timeout=2)
        SRS2_Read = DBMsgReader(bus, SRS2)
        BCS2_Send = DBMsgSender(bus, BCS2)
        SRS1_Msg = SRS1_Read()
        for k in SRS1_Msg.keys():
            print(k, SRS1_Msg[k])
        SRS2_Read.start()
        for i in range(10):
            bus.wait(0.1)
            print("Msg Counter: %d" % (SRS2_Read['SRS_2_MsgCounter']))
        SRS2_Read.stop()
        for i in range(10):
            bus.wait(0.1)
            print("Msg Counter: %d" % (SRS2_Read['SRS_2_MsgCounter']))
        BCS2_Send.start()
        
        for i in range(100):
            bus.wait(0.1)
            BCS2_Send['BCS_VehSpd'] += 1
        BCS2_Send.stop()
        for i in range(100):
            bus.wait(0.05)
            BCS2_Send['BCS_VehSpd'] += 1

