# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 23:12:01 2019

@author: levy.he
"""
import traceback
from pyuds.PyUds import FrBus, ComFr, FrTp, DiagRequest, DiagClient, ThreadSafety, BaseDiagnostic,Sender,FrFrame,MessageLog

rx_slots = [(70, 0, 1),
            (76, 0, 1),
            (82, 0, 1)]

tx_slots = [
    (88, 0, 1),
    (89, 0, 1),
    (90, 0, 1),
    (91, 0, 1),
    (92, 0, 1),
    (93, 0, 1),
    (94, 0, 1),]

if __name__ == '__main__':
    fr = FrBus()
    fr_bus = ComFr(fr)
    fr_tp = FrTp(rx_slots=rx_slots, tx_slots=tx_slots[:1],
                 source_addr=0x0e80, target_addr=0x1c01)
    uds_client = DiagClient(fr_tp)
    diag = BaseDiagnostic(uds_client=uds_client)
    fr_1s = FrFrame(slot_id=0, base_cycle=0, repetition_cycle=1, data=[])
    fr_sender = Sender(1.0,fr_1s)
    fr_bus.add_fr_cycle_setter(fr_tp.update_fr_cycle)
    #fr_bus.add_sender(fr_sender)
    fr_bus.add_sender(fr_tp.sender)
    fr_bus.add_reader(fr_tp.reader)
    MessageLog.start(log_level=0)
    with ThreadSafety(fr_bus):
        for i in range(100):
            resp = diag.ReadDataByIdentifier(0xFD39)
            print(i,resp)
            dtc = diag.ReadDtcInformation(0x0A)
            print(i,dtc)
            dids = diag.WriteDataByIdentifier(0xFD39,*[0x00]*1000)
            print(i,dids)
            if dids is None:break
            
    msg_list = MessageLog.get_logs()
    MessageLog.stop()