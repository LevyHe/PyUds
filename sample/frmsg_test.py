# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 16:10:22 2019

@author: levy.he
"""

from pyuds.PyUds import FrSendOnce, FrReadOnce, FrReader, FrSender, MessageLog
from pyuds.PyUds import FrBus, ComFr, ThreadSafety


if __name__ == '__main__':
    fr = FrBus()
    fr_bus = ComFr(fr)
    fr_bus.set_filters(filters=[77])
    MessageLog.start(log_level=2)
    with ThreadSafety(fr_bus):
        frsender = FrSender(fr_bus, slot_id=77, base_cycle=0, repetition_cycle=2, data=[0x00] * 32)
        frsender.start()
        fr_bus.wait(1)
        frsender.stop()
        fr_bus.wait(5)
    msg_list = MessageLog.get_logs()
    MessageLog.stop()
