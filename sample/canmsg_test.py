# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 16:10:22 2019

@author: levy.he
"""

from pyuds.PyUds import CanMsgSendOnce, CanMsgReadOnce, CanMsgReader, CanMsgSender
from pyuds.PyUds import CanBus, ComCan,ThreadSafety


if __name__ == '__main__':
    can = CanBus(app_name='CANalyzer', channel=0, bitrate=500000)
    bus = ComCan(can)
    with ThreadSafety(bus):
        ReadOnce = CanMsgReadOnce(bus,arbitration_id=0x1AE)
        SendOnce = CanMsgSendOnce(bus, arbitration_id=0x182, data=[0x00] * 8)
        MsgReader = CanMsgReader(bus, arbitration_id=0x3AB)
        MsgSender = CanMsgSender(bus,0.01, arbitration_id=0x260, data=[0x00] * 8)
        read_one = ReadOnce()
        print(read_one)
        SendOnce()
        'should check the can bus message'
        MsgReader.start()
        for i in range(10):
            bus.wait(0.1)
            print("Msg Counter: %d" % (MsgReader.data[6]))
        MsgReader.stop()
        for i in range(10):
            bus.wait(0.1)
            print("Msg Counter: %d" % (MsgReader.data[6]))
        MsgSender.start()
        for i in range(100):
            bus.wait(0.1)
            MsgSender.data[5] += 1
        MsgSender.stop()
        for i in range(100):
            bus.wait(0.01)
        'should check the can bus message'
