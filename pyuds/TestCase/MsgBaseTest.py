# -*- coding: utf-8 -*-
"""
Created on Fri May 5 20:13:59 2019

@author: levy.he
"""
from .Report.UdsLog import UdsLoging
from ..PyUds import CanMsgSender, CanMsgSendOnce


def list_to_hex_str(data):
    return ' '.join(['%02X' % (x) for x in data])


class MsgTesterBase(object):

    @UdsLoging(test_level=0, test_type=0)
    def AddDescription(self, desc):
        __class__.AddDescription.desc = desc

    @UdsLoging(test_level=0, test_type=3)
    def StartSendCanMsg(self, msg: CanMsgSender, desc=None):
        if desc is not None:
            step_desc = desc
        else:
            ext = 'x' if msg.is_extended_id else ''
            step_desc = 'StartSendCanMsg:' + '%03X' % (msg.arbitration_id) + ext
        __class__.StartSendCanMsg.desc = step_desc
        msg.start()
        
        return msg

    @UdsLoging(test_level=0, test_type=3)
    def StopSendCanMsg(self, msg: CanMsgSender, desc=None):
        if desc is not None:
            step_desc = desc
        else:
            ext = 'x' if msg.is_extended_id else ''
            step_desc = 'StopSendCanMsg:' + '%03X' % (msg.arbitration_id) + ext
        __class__.StopSendCanMsg.desc = step_desc
        msg.stop()
        return msg

    @UdsLoging(test_level=0, test_type=3)
    def SendCanMsgOnce(self, msg: CanMsgSendOnce, desc=None):
        if desc is not None:
            step_desc = desc
        else:
            ext = 'x' if msg.is_extended_id else ''
            step_desc = 'SendCanMsgOnce:' + '%03X' % (msg.arbitration_id) + ext
        __class__.SendCanMsgOnce.desc = step_desc
        msg()
        return msg

    @UdsLoging(test_level=0, test_type=3)
    def ReadCanMsg(self, msg, desc=None):
        if desc is not None:
            step_desc = desc
        else:
            ext = 'x' if msg.is_extended_id else ''
            step_desc = 'ReadCanMsg:' + '%03X' % (msg.arbitration_id) + ext
        __class__.ReadCanMsg.desc = step_desc
        
        return msg
        

    @UdsLoging(test_level=0, test_type=3)
    def ReadCanMsgOnce(self, msg, desc=None):
        if desc is not None:
            step_desc = desc
        else:
            ext = 'x' if msg.is_extended_id else ''
            step_desc = 'ReadCanMsg:' + '%03X' % (msg.arbitration_id) + ext
        __class__.ReadCanMsgOnce.desc = step_desc
        msg()
        return msg
