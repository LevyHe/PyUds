# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 17:26:48 2019

@author: levy.he
"""

from pyuds.PyUds import CanMsgSendOnce, CanMsgReadOnce, CanMsgReader, CanMsgSender
from pyuds.PyUds import CanBus, ComCan, ThreadSafety, BaseDiagnostic, DiagClient, CanTp
from pyps.agilent import E364xA
import time
import random



def InternalFaultUnPack(DataRecord):
    event_list=[]
    for i in range(0, len(DataRecord), 3):
        event_id = (DataRecord[i] << 8) + DataRecord[i + 1]
        status = DataRecord[i + 2]
        if event_id != 0 and status != 0:
            event_list.append((event_id, status))
    return event_list

def ProcessTheResp(resp, i, v, f):
        row = (i,v,0,0)
        if resp is not None:
            event_list = InternalFaultUnPack(resp.DataRecord)
            event_dict = {x[0]: x[1] for x in event_list}
            if 1294 in event_dict:
                row = (i, v, 1294, event_dict[1294])
        f.write("{:d},'{:0.3f},'{:d},'{:02X}\n".format(*row))
            
            

if __name__ == '__main__':
    can = CanBus(app_name='CANalyzer', channel=0, bitrate=500000)
    bus = ComCan(can)
    can_tp = CanTp(phy_id=0x1A000020, func_id=0x1A000021, resp_id=0x7A7)
    uds_client = DiagClient(can_tp)
    diag = BaseDiagnostic(uds_client=uds_client)
    bus.add_sender(can_tp.sender)
    bus.add_reader(can_tp.reader)
    ms_count = 0
    with ThreadSafety(bus):
        aiglent = E364xA("COM6")
        #aiglent.reset()
        aiglent.setonoff(True)
        f = open('log.csv','a+')
        for i in range(10):
            print("current test cycle is %d"%(i))
        #    aiglent.setonoff(False)
        #    ran = random.uniform(0.1,10.0)
        #    time.sleep(ran)
        #    aiglent.setonoff(True)
            #aiglent.setv()
            ran = random.uniform(0.0,15.0)
            aiglent.setv(ran)
            time.sleep(0.1)
            resp = diag.ReadDataByIdentifier(0xFD39)
            ProcessTheResp(resp,i,ran,f)
        f.close()
        del aiglent
        
        
                

